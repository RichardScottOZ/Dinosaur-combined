"""
Comprehensive example demonstrating integration from multiple sources
"""

import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrator import DataIntegrator
from schema import DinosaurClade, GeologicalPeriod
import json


def example_multi_source_integration():
    """
    Demonstrates integrating data from multiple sources and handling
    deduplication, merging, and conflict resolution.
    """
    
    print("=" * 80)
    print("MULTI-SOURCE INTEGRATION EXAMPLE")
    print("=" * 80)
    print()
    
    # Create the integrator
    integrator = DataIntegrator()
    
    # Example 1: Import from PBDB
    print("Example 1: Importing from PBDB")
    print("-" * 80)
    
    pbdb_data = [
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
            'lng': -107.0
        },
        {
            'occurrence_no': '1002',
            'taxon_no': '5002',
            'genus': 'Stegosaurus',
            'species': 'stenops',
            'order': 'Ornithischia',
            'family': 'Stegosauridae',
            'interval': 'Jurassic',
            'max_ma': 155.0,
            'min_ma': 150.0,
            'cc': 'US',
            'state': 'Colorado',
            'formation': 'Morrison Formation',
            'lat': 39.5,
            'lng': -105.5
        }
    ]
    
    count = integrator.add_records_from_source('pbdb', pbdb_data)
    print(f"✓ Imported {count} records from PBDB")
    print()
    
    # Example 2: Import from DinoData (including duplicate T. rex)
    print("Example 2: Importing from DinoData (with duplicate)")
    print("-" * 80)
    
    dinodata_records = [
        {
            'id': '2001',
            'genus': 'Tyrannosaurus',
            'species': 'rex',
            'common_name': 'T. rex',
            'order': 'Theropoda',
            'family': 'Tyrannosauridae',
            'clade': 'Theropoda',
            'period': 'Cretaceous',
            'country': 'United States',
            'length_m': 12.0,
            'weight_kg': 8400.0,
            'diet': 'Carnivore',
            'locomotion': 'Bipedal',
            'discovery_year': 1905,
            'discoverer': 'Barnum Brown',
            'etymology': 'Tyrant lizard king',
            'description': 'Large carnivorous theropod from Late Cretaceous'
        },
        {
            'id': '2002',
            'genus': 'Velociraptor',
            'species': 'mongoliensis',
            'common_name': 'Velociraptor',
            'order': 'Theropoda',
            'family': 'Dromaeosauridae',
            'clade': 'Theropoda',
            'period': 'Cretaceous',
            'country': 'Mongolia',
            'length_m': 2.0,
            'weight_kg': 15.0,
            'diet': 'Carnivore',
            'locomotion': 'Bipedal',
            'discovery_year': 1924
        }
    ]
    
    before_count = len(integrator.database.dinosaurs)
    count = integrator.add_records_from_source('dinodata', dinodata_records)
    after_count = len(integrator.database.dinosaurs)
    
    print(f"✓ Imported {count} records from DinoData")
    print(f"✓ Database now has {after_count} unique species (added {after_count - before_count} new)")
    print(f"✓ T. rex was recognized as duplicate and merged")
    print()
    
    # Example 3: Import from AMNH
    print("Example 3: Importing from AMNH collection")
    print("-" * 80)
    
    amnh_records = [
        {
            'specimen_id': '3001',
            'catalog_number': 'AMNH-5027',
            'genus': 'Tyrannosaurus',
            'species': 'rex',
            'collection': 'Vertebrate Paleontology',
            'type_status': 'holotype',
            'country': 'United States',
            'state_province': 'Montana',
            'locality': 'Hell Creek',
            'images': [
                'https://example.com/amnh5027_skull.jpg',
                'https://example.com/amnh5027_skeleton.jpg'
            ]
        }
    ]
    
    before_count = len(integrator.database.dinosaurs)
    count = integrator.add_records_from_source('amnh', amnh_records)
    after_count = len(integrator.database.dinosaurs)
    
    print(f"✓ Imported {count} records from AMNH")
    print(f"✓ Database now has {after_count} unique species (added {after_count - before_count} new)")
    print()
    
    # Show the merged T. rex record
    print("Example 4: Examining merged T. rex record")
    print("-" * 80)
    
    trex = integrator.database.get_by_name("Tyrannosaurus rex")
    
    if trex:
        print(f"Scientific Name: {trex.scientific_name}")
        print(f"Common Name: {trex.common_name}")
        print(f"Family: {trex.taxonomy.family}")
        print(f"Clade: {trex.clade.value}")
        print()
        
        print("Data from PBDB:")
        print(f"  - Location: {trex.location.state_province}, {trex.location.country}")
        print(f"  - Coordinates: {trex.location.latitude}, {trex.location.longitude}")
        print(f"  - Age: {trex.stratigraphy.age_min_ma}-{trex.stratigraphy.age_max_ma} Ma")
        print()
        
        print("Data from DinoData:")
        print(f"  - Common name: {trex.common_name}")
        print(f"  - Length: {trex.characteristics.length_meters} m")
        print(f"  - Weight: {trex.characteristics.weight_kg} kg")
        print(f"  - Diet: {trex.characteristics.diet}")
        print(f"  - Discovery: {trex.discovery_year} by {trex.discoverer}")
        print()
        
        print("Data from AMNH:")
        print(f"  - Museum collections: {len(trex.collections)}")
        for coll in trex.collections:
            print(f"    • {coll.institution}: {coll.catalog_number}")
            print(f"      Type: {'Holotype' if coll.holotype else 'Specimen'}")
        print(f"  - Images: {len(trex.images)}")
        print()
        
        print(f"Total data sources: {len(trex.data_sources)}")
        for source in trex.data_sources:
            print(f"  - {source.source_database}")
        print()
    
    # Example 5: Query operations
    print("Example 5: Querying the integrated database")
    print("-" * 80)
    
    # By period
    cretaceous = integrator.database.get_by_period(GeologicalPeriod.CRETACEOUS)
    print(f"Cretaceous dinosaurs: {len(cretaceous)}")
    for dino in cretaceous:
        print(f"  - {dino.scientific_name}")
    print()
    
    # By clade
    theropods = integrator.database.get_by_clade(DinosaurClade.THEROPODA)
    print(f"Theropod dinosaurs: {len(theropods)}")
    for dino in theropods:
        diet = dino.characteristics.diet or 'Unknown'
        print(f"  - {dino.scientific_name} ({diet})")
    print()
    
    # Example 6: Statistics
    print("Example 6: Database statistics")
    print("-" * 80)
    
    stats = integrator.get_statistics()
    
    print(f"Unique species: {stats['unique_species']}")
    print(f"Total merged records: {stats['total_merged_records']}")
    print()
    
    print("By Geological Period:")
    for period, count in stats['by_period'].items():
        if count > 0:
            print(f"  {period}: {count}")
    print()
    
    print("By Clade:")
    for clade, count in stats['by_clade'].items():
        if count > 0:
            print(f"  {clade}: {count}")
    print()
    
    print("Records by Source:")
    for source, count in stats.get('records_by_source', {}).items():
        print(f"  {source}: {count}")
    print()
    
    # Example 7: Export
    print("Example 7: Exporting integrated database")
    print("-" * 80)
    
    output_file = 'multi_source_example.json'
    integrator.export_to_json(output_file)
    print(f"✓ Exported to {output_file}")
    
    # Show contents
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    print(f"  Total dinosaurs: {len(data['dinosaurs'])}")
    print(f"  Metadata keys: {', '.join(data['metadata'].keys())}")
    print()
    
    # Example 8: Validation
    print("Example 8: Validating database")
    print("-" * 80)
    
    issues = integrator.validate_records()
    
    if issues:
        print(f"Found {len(issues)} validation issues:")
        for record_id, issue in issues[:5]:
            print(f"  - {record_id}: {issue}")
    else:
        print("✓ All records validated successfully!")
    print()
    
    print("=" * 80)
    print("EXAMPLE COMPLETE")
    print("=" * 80)


def example_synonym_resolution():
    """
    Demonstrates handling taxonomic synonyms
    """
    
    print("\n" + "=" * 80)
    print("SYNONYM RESOLUTION EXAMPLE")
    print("=" * 80)
    print()
    
    integrator = DataIntegrator()
    
    # Add records with synonyms
    # Brontosaurus was once considered a synonym of Apatosaurus
    records = [
        {
            'id': '1',
            'genus': 'Apatosaurus',
            'species': 'ajax',
            'order': 'Sauropodomorpha',
            'family': 'Diplodocidae',
            'period': 'Jurassic'
        },
        {
            'id': '2',
            'genus': 'Brontosaurus',
            'species': 'excelsus',
            'order': 'Sauropodomorpha',
            'family': 'Diplodocidae',
            'period': 'Jurassic'
        }
    ]
    
    integrator.add_records_from_source('dinodata', records)
    
    print(f"Added 2 records: Apatosaurus ajax and Brontosaurus excelsus")
    print(f"Database has {len(integrator.database.dinosaurs)} species")
    print()
    
    # If these were synonyms (historically they were, though now considered separate)
    # We could resolve them:
    # synonyms = {'Brontosaurus excelsus': 'Apatosaurus ajax'}
    # integrator.resolve_synonyms(synonyms)
    
    print("Note: Brontosaurus and Apatosaurus are now recognized as separate genera")
    print("But the system supports synonym resolution when needed")
    print()


if __name__ == '__main__':
    example_multi_source_integration()
    example_synonym_resolution()
