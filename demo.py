"""
Demonstration script showing the Dinosaur Database Integration System in action
"""

from integrator import DataIntegrator, create_sample_data
from schema import DinosaurClade, GeologicalPeriod
import json


def main():
    print("=" * 70)
    print("DINOSAUR DATABASE INTEGRATION SYSTEM - DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Create sample database
    print("Step 1: Creating sample integrated database...")
    print("-" * 70)
    database = create_sample_data()
    
    print(f"✓ Created database with {len(database.dinosaurs)} dinosaurs")
    print()
    
    # Show some records
    print("Step 2: Displaying sample records...")
    print("-" * 70)
    for i, (record_id, dinosaur) in enumerate(list(database.dinosaurs.items())[:4]):
        print(f"\n{i+1}. {dinosaur.scientific_name}")
        print(f"   Common Name: {dinosaur.common_name or 'N/A'}")
        print(f"   Clade: {dinosaur.clade.value}")
        print(f"   Period: {dinosaur.stratigraphy.geological_period.value}")
        print(f"   Family: {dinosaur.taxonomy.family or 'Unknown'}")
        print(f"   Location: {dinosaur.location.country or 'Unknown'}")
        if dinosaur.characteristics.length_meters:
            print(f"   Length: {dinosaur.characteristics.length_meters}m")
        if dinosaur.characteristics.diet:
            print(f"   Diet: {dinosaur.characteristics.diet}")
        print(f"   Data Sources: {len(dinosaur.data_sources)}")
        for source in dinosaur.data_sources:
            print(f"     - {source.source_database}")
    
    print()
    print("-" * 70)
    
    # Query examples
    print("\nStep 3: Demonstrating query capabilities...")
    print("-" * 70)
    
    # Query by period
    cretaceous = database.get_by_period(GeologicalPeriod.CRETACEOUS)
    print(f"\n✓ Cretaceous dinosaurs: {len(cretaceous)}")
    for dino in cretaceous[:3]:
        print(f"  - {dino.scientific_name}")
    
    # Query by clade
    theropods = database.get_by_clade(DinosaurClade.THEROPODA)
    print(f"\n✓ Theropod dinosaurs: {len(theropods)}")
    for dino in theropods[:3]:
        print(f"  - {dino.scientific_name}")
    
    # Query by name
    trex = database.get_by_name("Tyrannosaurus rex")
    if trex:
        print(f"\n✓ Found: {trex.scientific_name}")
        print(f"  Family: {trex.taxonomy.family}")
        print(f"  Period: {trex.stratigraphy.geological_period.value}")
        print(f"  Age: {trex.stratigraphy.age_max_ma}-{trex.stratigraphy.age_min_ma} Ma")
    
    print()
    print("-" * 70)
    
    # Statistics
    print("\nStep 4: Database statistics...")
    print("-" * 70)
    stats = database.stats()
    
    print(f"\nTotal dinosaurs: {stats['total_dinosaurs']}")
    print(f"Total sites: {stats['total_sites']}")
    
    print("\nBy Geological Period:")
    for period, count in stats['by_period'].items():
        if count > 0:
            print(f"  {period}: {count}")
    
    print("\nBy Clade:")
    for clade, count in stats['by_clade'].items():
        if count > 0:
            print(f"  {clade}: {count}")
    
    print()
    print("-" * 70)
    
    # Demonstrate integration with duplicates
    print("\nStep 5: Demonstrating deduplication...")
    print("-" * 70)
    
    integrator = DataIntegrator()
    
    # Add the same Tyrannosaurus from two different sources
    pbdb_trex = {
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
        'formation': 'Hell Creek',
        'lat': 47.5,
        'lng': -107.0
    }
    
    dinodata_trex = {
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
        'discovery_year': 1905,
        'discoverer': 'Barnum Brown'
    }
    
    print("Adding T. rex from PBDB...")
    integrator.add_records_from_source('pbdb', [pbdb_trex])
    
    print("Adding T. rex from DinoData...")
    integrator.add_records_from_source('dinodata', [dinodata_trex])
    
    # Should only have 1 record, merged from both sources
    trex_merged = integrator.database.get_by_name("Tyrannosaurus rex")
    print(f"\n✓ Records merged successfully!")
    print(f"  Scientific name: {trex_merged.scientific_name}")
    print(f"  Common name: {trex_merged.common_name} (from DinoData)")
    print(f"  Length: {trex_merged.characteristics.length_meters}m (from DinoData)")
    print(f"  Coordinates: {trex_merged.location.latitude}, {trex_merged.location.longitude} (from PBDB)")
    print(f"  Data sources: {len(trex_merged.data_sources)}")
    for source in trex_merged.data_sources:
        print(f"    - {source.source_database}")
    
    print()
    print("-" * 70)
    
    # Export to JSON
    print("\nStep 6: Exporting to JSON...")
    print("-" * 70)
    
    integrator.export_to_json('demo_database.json')
    print("✓ Database exported to demo_database.json")
    
    # Show file size
    import os
    size = os.path.getsize('demo_database.json')
    print(f"  File size: {size:,} bytes")
    
    # Show a snippet of the JSON
    with open('demo_database.json', 'r') as f:
        data = json.load(f)
    
    print(f"  Contains {len(data['dinosaurs'])} dinosaur records")
    print(f"  Metadata includes: {', '.join(data['metadata'].keys())}")
    
    print()
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Try: python dinosaur_cli.py stats --database demo_database.json")
    print("  2. Try: python dinosaur_cli.py query --name Tyrannosaurus")
    print("  3. Import real data from PBDB, AMNH, or other sources")
    print("  4. See INTEGRATION_GUIDE.md for more information")
    print()


if __name__ == '__main__':
    main()
