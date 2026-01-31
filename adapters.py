"""
Data Source Adapters

This module provides adapters for integrating data from different dinosaur databases.
Each adapter knows how to transform data from a specific source into the unified schema.
"""

from typing import Dict, Any, List, Optional
from schema import (
    Dinosaur, TaxonomicClassification, GeographicLocation,
    StratigraphicInfo, PhysicalCharacteristics, Reference,
    MuseumCollection, DataSource, DinosaurClade, GeologicalPeriod,
    FossilQuality, FossilSite
)
from datetime import datetime
import json


class BaseAdapter:
    """Base class for all data source adapters"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    def parse_record(self, record: Dict[str, Any]) -> Optional[Dinosaur]:
        """
        Parse a record from the source database into unified schema.
        Should be implemented by subclasses.
        """
        raise NotImplementedError
    
    def create_data_source(self, source_id: Optional[str] = None, 
                          url: Optional[str] = None) -> DataSource:
        """Create a DataSource object for this adapter"""
        return DataSource(
            source_database=self.source_name,
            source_id=source_id,
            last_updated=datetime.now(),
            url=url
        )


class PBDBAdapter(BaseAdapter):
    """
    Adapter for The Paleobiology Database (PBDB)
    
    PBDB provides comprehensive fossil occurrence data including:
    - Taxonomic classification
    - Geographic coordinates
    - Stratigraphic information
    - References
    """
    
    def __init__(self):
        super().__init__("Paleobiology Database (PBDB)")
    
    def parse_record(self, record: Dict[str, Any]) -> Optional[Dinosaur]:
        """Parse PBDB record into unified schema"""
        
        # Create taxonomy
        taxonomy = TaxonomicClassification(
            order=record.get('order'),
            family=record.get('family'),
            genus=record.get('genus'),
            species=record.get('species')
        )
        
        # Create location
        location = GeographicLocation(
            country=record.get('cc'),  # PBDB uses 'cc' for country code
            state_province=record.get('state'),
            locality=record.get('locality'),
            formation=record.get('formation'),
            latitude=record.get('lat'),
            longitude=record.get('lng')
        )
        
        # Create stratigraphy
        period_map = {
            'Triassic': GeologicalPeriod.TRIASSIC,
            'Jurassic': GeologicalPeriod.JURASSIC,
            'Cretaceous': GeologicalPeriod.CRETACEOUS
        }
        
        # Note: PBDB uses 'max_ma' for older age and 'min_ma' for younger age
        # We reverse this to match our schema where min_ma is minimum (older) age
        stratigraphy = StratigraphicInfo(
            geological_period=period_map.get(record.get('interval'), GeologicalPeriod.UNKNOWN),
            age_min_ma=record.get('max_ma'),  # PBDB's max_ma is the older/minimum age
            age_max_ma=record.get('min_ma'),  # PBDB's min_ma is the younger/maximum age
            formation_name=record.get('formation')
        )
        
        # Determine clade from order
        clade = DinosaurClade.UNKNOWN
        order = record.get('order', '').lower()
        if 'theropod' in order:
            clade = DinosaurClade.THEROPODA
        elif 'sauropod' in order:
            clade = DinosaurClade.SAUROPODOMORPHA
        elif 'ornithisch' in order:
            clade = DinosaurClade.ORNITHISCHIA
        
        # Create dinosaur record
        record_id = f"pbdb_{record.get('occurrence_no', record.get('oid'))}"
        scientific_name = f"{taxonomy.genus} {taxonomy.species}" if taxonomy.species else taxonomy.genus or "Unknown"
        
        dinosaur = Dinosaur(
            record_id=record_id,
            scientific_name=scientific_name,
            taxonomy=taxonomy,
            location=location,
            stratigraphy=stratigraphy,
            clade=clade,
            data_sources=[self.create_data_source(
                source_id=str(record.get('occurrence_no')),
                url=f"https://paleobiodb.org/classic/basicTaxonInfo?taxon_no={record.get('taxon_no')}"
            )]
        )
        
        # Add reference if available
        if record.get('reference_no'):
            ref = Reference(
                reference_id=str(record.get('reference_no')),
                authors=record.get('ref_author'),
                year=record.get('ref_pubyr')
            )
            dinosaur.references.append(ref)
        
        return dinosaur


class AMNHAdapter(BaseAdapter):
    """
    Adapter for American Museum of Natural History Database
    
    AMNH provides:
    - Specimen catalog numbers
    - Collection information
    - Taxonomic data
    - Images and media
    """
    
    def __init__(self):
        super().__init__("American Museum of Natural History")
    
    def parse_record(self, record: Dict[str, Any]) -> Optional[Dinosaur]:
        """Parse AMNH record into unified schema"""
        
        taxonomy = TaxonomicClassification(
            order=record.get('order'),
            family=record.get('family'),
            genus=record.get('genus'),
            species=record.get('species')
        )
        
        # AMNH has strong collection data
        collection = MuseumCollection(
            institution="American Museum of Natural History",
            collection_code=record.get('collection'),
            catalog_number=record.get('catalog_number'),
            holotype=record.get('type_status') == 'holotype'
        )
        
        location = GeographicLocation(
            country=record.get('country'),
            state_province=record.get('state_province'),
            locality=record.get('locality')
        )
        
        record_id = f"amnh_{record.get('catalog_number', record.get('specimen_id'))}"
        scientific_name = f"{taxonomy.genus} {taxonomy.species}" if taxonomy.species else taxonomy.genus or "Unknown"
        
        dinosaur = Dinosaur(
            record_id=record_id,
            scientific_name=scientific_name,
            taxonomy=taxonomy,
            location=location,
            collections=[collection],
            images=record.get('images', []),
            data_sources=[self.create_data_source(
                source_id=record.get('specimen_id'),
                url=f"https://www.amnh.org/research/paleontology/collections/search/{record.get('catalog_number')}"
            )]
        )
        
        return dinosaur


class DinoDataAdapter(BaseAdapter):
    """
    Adapter for DinoData database
    
    DinoData provides:
    - Comprehensive taxonomic data
    - Physical characteristics
    - Discovery information
    """
    
    def __init__(self):
        super().__init__("DinoData")
    
    def parse_record(self, record: Dict[str, Any]) -> Optional[Dinosaur]:
        """Parse DinoData record into unified schema"""
        
        taxonomy = TaxonomicClassification(
            order=record.get('order'),
            family=record.get('family'),
            genus=record.get('genus'),
            species=record.get('species')
        )
        
        characteristics = PhysicalCharacteristics(
            length_meters=record.get('length_m'),
            height_meters=record.get('height_m'),
            weight_kg=record.get('weight_kg'),
            diet=record.get('diet'),
            locomotion=record.get('locomotion')
        )
        
        location = GeographicLocation(
            country=record.get('country'),
            locality=record.get('locality'),
            formation=record.get('formation')
        )
        
        # Map period
        period_map = {
            'triassic': GeologicalPeriod.TRIASSIC,
            'jurassic': GeologicalPeriod.JURASSIC,
            'cretaceous': GeologicalPeriod.CRETACEOUS
        }
        
        stratigraphy = StratigraphicInfo(
            geological_period=period_map.get(
                record.get('period', '').lower(), 
                GeologicalPeriod.UNKNOWN
            )
        )
        
        # Determine clade
        clade_map = {
            'theropoda': DinosaurClade.THEROPODA,
            'sauropodomorpha': DinosaurClade.SAUROPODOMORPHA,
            'ornithischia': DinosaurClade.ORNITHISCHIA
        }
        clade = clade_map.get(record.get('clade', '').lower(), DinosaurClade.UNKNOWN)
        
        record_id = f"dinodata_{record.get('id')}"
        scientific_name = f"{taxonomy.genus} {taxonomy.species}" if taxonomy.species else taxonomy.genus or "Unknown"
        
        dinosaur = Dinosaur(
            record_id=record_id,
            scientific_name=scientific_name,
            common_name=record.get('common_name'),
            taxonomy=taxonomy,
            characteristics=characteristics,
            location=location,
            stratigraphy=stratigraphy,
            clade=clade,
            discovery_year=record.get('discovery_year'),
            discoverer=record.get('discoverer'),
            etymology=record.get('etymology'),
            description=record.get('description'),
            data_sources=[self.create_data_source(
                source_id=str(record.get('id'))
            )]
        )
        
        return dinosaur


class NHMLondonAdapter(BaseAdapter):
    """
    Adapter for Natural History Museum London Dino Directory
    
    Provides:
    - Taxonomic information
    - Educational descriptions
    - Images
    """
    
    def __init__(self):
        super().__init__("Natural History Museum London")
    
    def parse_record(self, record: Dict[str, Any]) -> Optional[Dinosaur]:
        """Parse NHM London record into unified schema"""
        
        taxonomy = TaxonomicClassification(
            order=record.get('order'),
            family=record.get('family'),
            genus=record.get('genus'),
            species=record.get('species')
        )
        
        period_map = {
            'triassic': GeologicalPeriod.TRIASSIC,
            'jurassic': GeologicalPeriod.JURASSIC,
            'cretaceous': GeologicalPeriod.CRETACEOUS
        }
        
        stratigraphy = StratigraphicInfo(
            geological_period=period_map.get(
                record.get('period', '').lower(),
                GeologicalPeriod.UNKNOWN
            )
        )
        
        location = GeographicLocation(
            country=record.get('country')
        )
        
        record_id = f"nhm_{record.get('id')}"
        scientific_name = f"{taxonomy.genus} {taxonomy.species}" if taxonomy.species else taxonomy.genus or "Unknown"
        
        dinosaur = Dinosaur(
            record_id=record_id,
            scientific_name=scientific_name,
            common_name=record.get('common_name'),
            taxonomy=taxonomy,
            location=location,
            stratigraphy=stratigraphy,
            description=record.get('description'),
            images=record.get('images', []),
            data_sources=[self.create_data_source(
                source_id=str(record.get('id')),
                url=record.get('url')
            )]
        )
        
        return dinosaur


class DinoAnimalsAdapter(BaseAdapter):
    """
    Adapter for DinoAnimals Complete Dinosaur Database
    
    Provides:
    - Complete genus and species listings
    - Size information
    - Classification data
    """
    
    def __init__(self):
        super().__init__("DinoAnimals Complete Database")
    
    def parse_record(self, record: Dict[str, Any]) -> Optional[Dinosaur]:
        """Parse DinoAnimals record into unified schema"""
        
        taxonomy = TaxonomicClassification(
            order=record.get('order'),
            family=record.get('family'),
            genus=record.get('genus'),
            species=record.get('species')
        )
        
        characteristics = PhysicalCharacteristics(
            length_meters=record.get('length'),
            weight_kg=record.get('weight'),
            diet=record.get('diet')
        )
        
        period_map = {
            'triassic': GeologicalPeriod.TRIASSIC,
            'jurassic': GeologicalPeriod.JURASSIC,
            'cretaceous': GeologicalPeriod.CRETACEOUS
        }
        
        stratigraphy = StratigraphicInfo(
            geological_period=period_map.get(
                record.get('period', '').lower(),
                GeologicalPeriod.UNKNOWN
            )
        )
        
        record_id = f"dinoanimals_{record.get('id')}"
        scientific_name = f"{taxonomy.genus} {taxonomy.species}" if taxonomy.species else taxonomy.genus or "Unknown"
        
        dinosaur = Dinosaur(
            record_id=record_id,
            scientific_name=scientific_name,
            taxonomy=taxonomy,
            characteristics=characteristics,
            stratigraphy=stratigraphy,
            valid_name=record.get('valid', True),
            accepted_name=record.get('accepted_name'),
            data_sources=[self.create_data_source(
                source_id=str(record.get('id'))
            )]
        )
        
        return dinosaur


class AdapterFactory:
    """Factory for creating appropriate adapters"""
    
    _adapters = {
        'pbdb': PBDBAdapter,
        'paleobiology_database': PBDBAdapter,
        'amnh': AMNHAdapter,
        'american_museum': AMNHAdapter,
        'dinodata': DinoDataAdapter,
        'nhm': NHMLondonAdapter,
        'natural_history_museum': NHMLondonAdapter,
        'dinoanimals': DinoAnimalsAdapter,
    }
    
    @classmethod
    def get_adapter(cls, source: str) -> BaseAdapter:
        """Get adapter for a specific data source"""
        source_key = source.lower().replace(' ', '_').replace('-', '_')
        adapter_class = cls._adapters.get(source_key)
        
        if adapter_class is None:
            raise ValueError(f"No adapter found for source: {source}")
        
        return adapter_class()
    
    @classmethod
    def list_sources(cls) -> List[str]:
        """List all available data sources"""
        return list(set(cls._adapters.values()))
