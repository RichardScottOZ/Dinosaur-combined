"""
Integration Engine

This module provides the core integration functionality to combine data from
multiple dinosaur databases, handling deduplication, conflict resolution, and
data merging.
"""

from typing import Dict, List, Optional, Set, Tuple
from schema import Dinosaur, DinosaurDatabase, DataSource
from adapters import AdapterFactory
import json
from collections import defaultdict


class DataIntegrator:
    """
    Main integration engine for combining dinosaur data from multiple sources
    """
    
    def __init__(self):
        self.database = DinosaurDatabase()
        self.duplicates_map: Dict[str, List[str]] = defaultdict(list)  # Maps canonical ID to duplicate IDs
        
    def add_records_from_source(self, source: str, records: List[Dict]) -> int:
        """
        Add records from a specific data source
        
        Args:
            source: Name of the data source (e.g., 'pbdb', 'amnh')
            records: List of raw records from the source
            
        Returns:
            Number of records successfully added
        """
        adapter = AdapterFactory.get_adapter(source)
        count = 0
        
        for record in records:
            try:
                dinosaur = adapter.parse_record(record)
                if dinosaur:
                    self._integrate_record(dinosaur)
                    count += 1
            except Exception as e:
                print(f"Error processing record from {source}: {e}")
                continue
        
        return count
    
    def _integrate_record(self, new_dinosaur: Dinosaur) -> None:
        """
        Integrate a new dinosaur record into the database.
        Handles deduplication and merging with existing records.
        """
        # Check if this dinosaur already exists
        existing = self._find_matching_record(new_dinosaur)
        
        if existing:
            # Merge the records
            self._merge_records(existing, new_dinosaur)
        else:
            # Add as new record
            self.database.add_dinosaur(new_dinosaur)
    
    def _find_matching_record(self, dinosaur: Dinosaur) -> Optional[Dinosaur]:
        """
        Find if a matching dinosaur record already exists in the database.
        
        Matching criteria:
        1. Exact scientific name match
        2. Same genus and similar temporal/geographic data
        """
        # First try exact name match
        existing = self.database.get_by_name(dinosaur.scientific_name)
        if existing:
            return existing
        
        # Try fuzzy matching on genus and location
        for existing_dino in self.database.dinosaurs.values():
            if self._is_likely_same_species(existing_dino, dinosaur):
                return existing_dino
        
        return None
    
    def _is_likely_same_species(self, dino1: Dinosaur, dino2: Dinosaur) -> bool:
        """
        Determine if two dinosaur records likely represent the same species.
        Uses multiple heuristics.
        """
        # Check genus match
        if dino1.taxonomy.genus != dino2.taxonomy.genus:
            return False
        
        # If species names are available and different, not a match
        if (dino1.taxonomy.species and dino2.taxonomy.species and 
            dino1.taxonomy.species != dino2.taxonomy.species):
            return False
        
        # Check temporal overlap
        if not self._has_temporal_overlap(dino1, dino2):
            return False
        
        # If we get here, likely the same species
        return True
    
    def _has_temporal_overlap(self, dino1: Dinosaur, dino2: Dinosaur) -> bool:
        """Check if two dinosaurs have overlapping time ranges"""
        # If both have age ranges, check for overlap
        if (dino1.stratigraphy.age_min_ma and dino1.stratigraphy.age_max_ma and
            dino2.stratigraphy.age_min_ma and dino2.stratigraphy.age_max_ma):
            
            # Check if ranges overlap
            return not (dino1.stratigraphy.age_max_ma < dino2.stratigraphy.age_min_ma or
                       dino2.stratigraphy.age_max_ma < dino1.stratigraphy.age_min_ma)
        
        # If periods are known, check if they match
        if (dino1.stratigraphy.geological_period and 
            dino2.stratigraphy.geological_period):
            return dino1.stratigraphy.geological_period == dino2.stratigraphy.geological_period
        
        # If we don't have enough data, assume possible overlap
        return True
    
    def _merge_records(self, existing: Dinosaur, new: Dinosaur) -> None:
        """
        Merge a new dinosaur record into an existing one.
        Combines data from both records, preferring more complete information.
        """
        # Track that these are duplicates
        self.duplicates_map[existing.record_id].append(new.record_id)
        
        # Merge data sources
        existing.data_sources.extend(new.data_sources)
        
        # Merge references
        existing_ref_ids = {ref.reference_id for ref in existing.references if ref.reference_id}
        for ref in new.references:
            if ref.reference_id not in existing_ref_ids:
                existing.references.append(ref)
        
        # Merge collections
        existing_collection_ids = {
            (c.institution, c.catalog_number) 
            for c in existing.collections
        }
        for collection in new.collections:
            if (collection.institution, collection.catalog_number) not in existing_collection_ids:
                existing.collections.append(collection)
        
        # Merge images
        existing.images = list(set(existing.images + new.images))
        
        # Update fields if new record has data and existing doesn't
        if not existing.common_name and new.common_name:
            existing.common_name = new.common_name
        
        if not existing.description and new.description:
            existing.description = new.description
        
        if not existing.etymology and new.etymology:
            existing.etymology = new.etymology
        
        # Update physical characteristics if new has better data
        if new.characteristics.length_meters and not existing.characteristics.length_meters:
            existing.characteristics.length_meters = new.characteristics.length_meters
        
        if new.characteristics.weight_kg and not existing.characteristics.weight_kg:
            existing.characteristics.weight_kg = new.characteristics.weight_kg
        
        if new.characteristics.diet and not existing.characteristics.diet:
            existing.characteristics.diet = new.characteristics.diet
        
        # Update temporal data if new is more precise
        if (new.stratigraphy.age_min_ma and new.stratigraphy.age_max_ma and
            not (existing.stratigraphy.age_min_ma and existing.stratigraphy.age_max_ma)):
            existing.stratigraphy.age_min_ma = new.stratigraphy.age_min_ma
            existing.stratigraphy.age_max_ma = new.stratigraphy.age_max_ma
        
        # Update location if new has coordinates and existing doesn't
        if (new.location.latitude and new.location.longitude and
            not (existing.location.latitude and existing.location.longitude)):
            existing.location.latitude = new.location.latitude
            existing.location.longitude = new.location.longitude
    
    def resolve_synonyms(self, synonyms: Dict[str, str]) -> None:
        """
        Resolve taxonomic synonyms by merging records.
        
        Args:
            synonyms: Dict mapping invalid names to valid names
        """
        for invalid_name, valid_name in synonyms.items():
            invalid_record = self.database.get_by_name(invalid_name)
            valid_record = self.database.get_by_name(valid_name)
            
            if invalid_record and valid_record:
                invalid_record.valid_name = False
                invalid_record.accepted_name = valid_name
                self._merge_records(valid_record, invalid_record)
    
    def export_to_json(self, filename: str) -> None:
        """Export the integrated database to JSON"""
        data = {
            'metadata': {
                'total_records': len(self.database.dinosaurs),
                'total_sites': len(self.database.sites),
                'sources': list(set(
                    source.source_database 
                    for dino in self.database.dinosaurs.values()
                    for source in dino.data_sources
                )),
                'statistics': self.database.stats()
            },
            'dinosaurs': [dino.to_dict() for dino in self.database.dinosaurs.values()],
            'duplicates_map': dict(self.duplicates_map)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_from_json(self, filename: str) -> None:
        """Import data from a JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # This would need more complete implementation to reconstruct objects
        # For now, just import the dinosaur data
        print(f"Loaded {len(data.get('dinosaurs', []))} dinosaurs from {filename}")
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the integrated database"""
        stats = self.database.stats()
        
        # Add source coverage statistics
        source_counts = defaultdict(int)
        for dino in self.database.dinosaurs.values():
            for source in dino.data_sources:
                source_counts[source.source_database] += 1
        
        stats['records_by_source'] = dict(source_counts)
        stats['total_merged_records'] = sum(len(v) for v in self.duplicates_map.values())
        stats['unique_species'] = len(self.database.dinosaurs)
        
        return stats
    
    def validate_records(self) -> List[Tuple[str, str]]:
        """
        Validate all records and return list of issues found.
        
        Returns:
            List of (record_id, issue_description) tuples
        """
        issues = []
        
        for record_id, dinosaur in self.database.dinosaurs.items():
            # Check required fields
            if not dinosaur.scientific_name or dinosaur.scientific_name == "Unknown":
                issues.append((record_id, "Missing scientific name"))
            
            if not dinosaur.taxonomy.genus:
                issues.append((record_id, "Missing genus"))
            
            if not dinosaur.data_sources:
                issues.append((record_id, "No data sources"))
            
            # Check data consistency
            if dinosaur.characteristics.length_meters and dinosaur.characteristics.length_meters < 0:
                issues.append((record_id, "Invalid length (negative)"))
            
            if dinosaur.characteristics.weight_kg and dinosaur.characteristics.weight_kg < 0:
                issues.append((record_id, "Invalid weight (negative)"))
        
        return issues


def create_sample_data() -> DinosaurDatabase:
    """
    Create sample data for demonstration purposes
    """
    integrator = DataIntegrator()
    
    # Sample PBDB-style records
    pbdb_records = [
        {
            'occurrence_no': '1001',
            'taxon_no': '5001',
            'genus': 'Tyrannosaurus',
            'species': 'rex',
            'order': 'Theropoda',
            'family': 'Tyrannosauridae',
            'interval': 'Cretaceous',
            'max_ma': 68.0,
            'min_ma': 66.0,
            'cc': 'US',
            'state': 'Montana',
            'locality': 'Hell Creek Formation',
            'formation': 'Hell Creek',
            'lat': 47.5,
            'lng': -107.0,
            'reference_no': '1234',
            'ref_author': 'Osborn, H.F.',
            'ref_pubyr': 1905
        },
        {
            'occurrence_no': '1002',
            'taxon_no': '5002',
            'genus': 'Triceratops',
            'species': 'horridus',
            'order': 'Ornithischia',
            'family': 'Ceratopsidae',
            'interval': 'Cretaceous',
            'max_ma': 68.0,
            'min_ma': 66.0,
            'cc': 'US',
            'state': 'Wyoming',
            'formation': 'Lance Formation',
            'lat': 43.0,
            'lng': -105.0
        }
    ]
    
    # Sample DinoData-style records
    dinodata_records = [
        {
            'id': '2001',
            'genus': 'Velociraptor',
            'species': 'mongoliensis',
            'common_name': 'Velociraptor',
            'order': 'Theropoda',
            'family': 'Dromaeosauridae',
            'clade': 'Theropoda',
            'period': 'Cretaceous',
            'country': 'Mongolia',
            'formation': 'Djadochta Formation',
            'length_m': 2.0,
            'weight_kg': 15.0,
            'diet': 'Carnivore',
            'locomotion': 'Bipedal',
            'discovery_year': 1924,
            'discoverer': 'Peter Kaisen',
            'etymology': 'Swift seizer',
            'description': 'Small theropod dinosaur with a distinctive sickle claw'
        },
        {
            'id': '2002',
            'genus': 'Brachiosaurus',
            'species': 'altithorax',
            'common_name': 'Brachiosaurus',
            'order': 'Sauropodomorpha',
            'family': 'Brachiosauridae',
            'clade': 'Sauropodomorpha',
            'period': 'Jurassic',
            'country': 'United States',
            'formation': 'Morrison Formation',
            'length_m': 26.0,
            'weight_kg': 56000.0,
            'diet': 'Herbivore',
            'locomotion': 'Quadrupedal',
            'discovery_year': 1900,
            'etymology': 'Arm lizard'
        }
    ]
    
    integrator.add_records_from_source('pbdb', pbdb_records)
    integrator.add_records_from_source('dinodata', dinodata_records)
    
    return integrator.database
