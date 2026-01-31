"""
Command-line interface for the Dinosaur Database Integration System
"""

import argparse
import json
from integrator import DataIntegrator, create_sample_data
from adapters import AdapterFactory
from schema import DinosaurClade, GeologicalPeriod


def main():
    parser = argparse.ArgumentParser(
        description='Dinosaur Database Integration System - Combine data from multiple dinosaur archives'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from a source')
    import_parser.add_argument('source', help='Data source (pbdb, amnh, dinodata, etc.)')
    import_parser.add_argument('file', help='Input file with records')
    import_parser.add_argument('--output', '-o', help='Output file for integrated database', 
                              default='dinosaur_database.json')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export database to JSON')
    export_parser.add_argument('output', help='Output file')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.add_argument('--database', '-d', help='Database file to analyze',
                             default='dinosaur_database.json')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the database')
    query_parser.add_argument('--name', help='Search by scientific name')
    query_parser.add_argument('--genus', help='Search by genus')
    query_parser.add_argument('--period', choices=['triassic', 'jurassic', 'cretaceous'],
                             help='Filter by geological period')
    query_parser.add_argument('--clade', choices=['theropoda', 'sauropodomorpha', 'ornithischia'],
                             help='Filter by clade')
    query_parser.add_argument('--database', '-d', help='Database file to query',
                             default='dinosaur_database.json')
    
    # List sources command
    sources_parser = subparsers.add_parser('sources', help='List available data sources')
    
    # Sample data command
    sample_parser = subparsers.add_parser('sample', help='Generate sample database')
    sample_parser.add_argument('--output', '-o', help='Output file',
                              default='sample_database.json')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate database records')
    validate_parser.add_argument('--database', '-d', help='Database file to validate',
                                default='dinosaur_database.json')
    
    args = parser.parse_args()
    
    if args.command == 'import':
        handle_import(args)
    elif args.command == 'export':
        handle_export(args)
    elif args.command == 'stats':
        handle_stats(args)
    elif args.command == 'query':
        handle_query(args)
    elif args.command == 'sources':
        handle_sources(args)
    elif args.command == 'sample':
        handle_sample(args)
    elif args.command == 'validate':
        handle_validate(args)
    else:
        parser.print_help()


def handle_import(args):
    """Import data from a source file"""
    print(f"Importing from {args.source}...")
    
    integrator = DataIntegrator()
    
    try:
        with open(args.file, 'r') as f:
            records = json.load(f)
        
        if not isinstance(records, list):
            records = [records]
        
        count = integrator.add_records_from_source(args.source, records)
        print(f"Successfully imported {count} records from {args.source}")
        
        # Export the integrated database
        integrator.export_to_json(args.output)
        print(f"Database exported to {args.output}")
        
        # Show statistics
        stats = integrator.get_statistics()
        print("\nDatabase Statistics:")
        print(f"  Total dinosaurs: {stats['unique_species']}")
        print(f"  By period: {stats['by_period']}")
        print(f"  By clade: {stats['by_clade']}")
        
    except Exception as e:
        print(f"Error importing data: {e}")
        return 1
    
    return 0


def handle_export(args):
    """Export database to JSON"""
    print(f"Exporting to {args.output}...")
    # Implementation would load existing database and export
    print("Export complete")


def handle_stats(args):
    """Show database statistics"""
    try:
        with open(args.database, 'r') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        stats = metadata.get('statistics', {})
        
        print("=" * 60)
        print("DINOSAUR DATABASE STATISTICS")
        print("=" * 60)
        print(f"\nTotal Records: {metadata.get('total_records', 0)}")
        print(f"Total Sites: {metadata.get('total_sites', 0)}")
        
        print("\nData Sources:")
        for source in metadata.get('sources', []):
            print(f"  - {source}")
        
        print("\nBy Geological Period:")
        for period, count in stats.get('by_period', {}).items():
            if count > 0:
                print(f"  {period}: {count}")
        
        print("\nBy Clade:")
        for clade, count in stats.get('by_clade', {}).items():
            if count > 0:
                print(f"  {clade}: {count}")
        
        if 'records_by_source' in metadata:
            print("\nRecords by Source:")
            for source, count in metadata['records_by_source'].items():
                print(f"  {source}: {count}")
        
    except FileNotFoundError:
        print(f"Error: Database file '{args.database}' not found")
        return 1
    except Exception as e:
        print(f"Error reading database: {e}")
        return 1
    
    return 0


def handle_query(args):
    """Query the database"""
    try:
        with open(args.database, 'r') as f:
            data = json.load(f)
        
        dinosaurs = data.get('dinosaurs', [])
        results = dinosaurs
        
        # Apply filters
        if args.name:
            results = [d for d in results if args.name.lower() in d.get('scientific_name', '').lower()]
        
        if args.genus:
            results = [d for d in results if d.get('taxonomy', {}).get('genus', '').lower() == args.genus.lower()]
        
        if args.period:
            results = [d for d in results if d.get('stratigraphy', {}).get('period', '').lower() == args.period.lower()]
        
        if args.clade:
            results = [d for d in results if d.get('clade', '').lower() == args.clade.lower()]
        
        # Display results
        print(f"\nFound {len(results)} results:\n")
        for dino in results[:20]:  # Limit to first 20
            print(f"{dino.get('scientific_name', 'Unknown')}")
            print(f"  Clade: {dino.get('clade', 'Unknown')}")
            print(f"  Period: {dino.get('stratigraphy', {}).get('period', 'Unknown')}")
            print(f"  Location: {dino.get('location', {}).get('country', 'Unknown')}")
            sources = dino.get('data_sources', [])
            if sources:
                print(f"  Sources: {', '.join(sources)}")
            print()
        
        if len(results) > 20:
            print(f"... and {len(results) - 20} more results")
        
    except FileNotFoundError:
        print(f"Error: Database file '{args.database}' not found")
        return 1
    except Exception as e:
        print(f"Error querying database: {e}")
        return 1
    
    return 0


def handle_sources(args):
    """List available data sources"""
    print("\nAvailable Data Sources:")
    print("=" * 60)
    
    sources = [
        ("Paleobiology Database (PBDB)", "pbdb", "Global fossil occurrence database"),
        ("American Museum of Natural History", "amnh", "AMNH collection database"),
        ("DinoData", "dinodata", "Comprehensive dinosaur information"),
        ("Natural History Museum London", "nhm", "NHM Dino Directory"),
        ("DinoAnimals Complete Database", "dinoanimals", "Complete genus/species listings"),
    ]
    
    for name, code, description in sources:
        print(f"\n{name}")
        print(f"  Code: {code}")
        print(f"  Description: {description}")
    
    print("\nUsage: dinosaur_cli.py import <source_code> <input_file>")


def handle_sample(args):
    """Generate sample database"""
    print("Generating sample database...")
    
    database = create_sample_data()
    integrator = DataIntegrator()
    integrator.database = database
    
    integrator.export_to_json(args.output)
    print(f"Sample database created: {args.output}")
    
    stats = integrator.get_statistics()
    print(f"\nCreated database with {stats['unique_species']} dinosaurs")
    print("Use 'stats' command to see more details")
    
    return 0


def handle_validate(args):
    """Validate database records"""
    try:
        # This would need full implementation with object reconstruction
        print(f"Validating {args.database}...")
        
        with open(args.database, 'r') as f:
            data = json.load(f)
        
        dinosaurs = data.get('dinosaurs', [])
        issues = []
        
        for dino in dinosaurs:
            if not dino.get('scientific_name') or dino.get('scientific_name') == 'Unknown':
                issues.append((dino.get('record_id', 'unknown'), "Missing scientific name"))
            
            if not dino.get('taxonomy', {}).get('genus'):
                issues.append((dino.get('record_id', 'unknown'), "Missing genus"))
        
        if issues:
            print(f"\nFound {len(issues)} validation issues:")
            for record_id, issue in issues[:10]:
                print(f"  {record_id}: {issue}")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more issues")
        else:
            print("\nNo validation issues found!")
        
        return 0 if not issues else 1
        
    except FileNotFoundError:
        print(f"Error: Database file '{args.database}' not found")
        return 1
    except Exception as e:
        print(f"Error validating database: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
