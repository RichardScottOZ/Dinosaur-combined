# Dinosaur-combined

A comprehensive system for integrating data from all major dinosaur archives and databases into one unified, cohesive database.

## Overview

This project provides a complete solution for combining data from multiple dinosaur databases into a single, standardized format. It includes:

- **Unified Schema**: Comprehensive data model accommodating all major data sources
- **Data Adapters**: Source-specific adapters for seamless integration
- **Deduplication Engine**: Intelligent merging of duplicate records
- **Query Interface**: Command-line tools for searching and analyzing data
- **Export/Import**: JSON-based data exchange

## Supported Data Sources

- **The Paleobiology Database (PBDB)** - Global fossil occurrence data
- **American Museum of Natural History (AMNH)** - Museum collection records
- **DinoData** - Comprehensive dinosaur information
- **Natural History Museum London** - Dino Directory
- **DinoAnimals Complete Database** - Complete genus and species listings
- **National Park Service Archives** - US fossil site data

## Quick Start

```bash
# Install the package
pip install .

# Generate sample database
dinosaur-cli sample --output sample_database.json

# Run demonstration
python -m demo

# View statistics
dinosaur-cli stats --database sample_database.json

# Query the database
dinosaur-cli query --name "Tyrannosaurus"
```

## Installation

```bash
pip install .
```

For development, install in editable mode:

```bash
pip install -e .
```

This installs the `dinosaur-cli` command while keeping the existing top-level modules
available for Python imports such as `from integrator import DataIntegrator`.

## Features

✓ Unified schema for all dinosaur data  
✓ Automatic deduplication and merging  
✓ Support for multiple data sources  
✓ Comprehensive taxonomic classification  
✓ Geographic and stratigraphic data  
✓ Physical characteristics and measurements  
✓ Museum collection tracking  
✓ Reference management  
✓ Data validation and quality checks  

## Documentation

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed documentation including:
- Architecture overview
- Data schema details
- API reference
- Integration examples
- Extending the system

## Project Structure

```
Dinosaur-combined/
├── schema.py              # Unified data model
├── adapters.py            # Data source adapters
├── integrator.py          # Integration engine
├── dinosaur_cli.py        # Command-line interface
├── demo.py                # Demonstration script
├── INTEGRATION_GUIDE.md   # Complete documentation
├── examples/              # Sample data files
│   ├── pbdb_sample.json
│   ├── dinodata_sample.json
│   └── amnh_sample.json
└── README.md              # This file
```

## Example Usage

### Python API

```python
from integrator import DataIntegrator
from schema import GeologicalPeriod

# Create integrator
integrator = DataIntegrator()

# Import from different sources
integrator.add_records_from_source('pbdb', pbdb_records)
integrator.add_records_from_source('dinodata', dinodata_records)

# Query
trex = integrator.database.get_by_name("Tyrannosaurus rex")
cretaceous = integrator.database.get_by_period(GeologicalPeriod.CRETACEOUS)

# Export
integrator.export_to_json('combined_database.json')
```

### Command Line

```bash
# Import data
dinosaur-cli import pbdb examples/pbdb_sample.json

# Query by period
dinosaur-cli query --period cretaceous

# Query by clade
dinosaur-cli query --clade theropoda

# Show statistics
dinosaur-cli stats

# Validate database
dinosaur-cli validate
```

## Contributing

Contributions welcome! Areas for enhancement:
- Additional data source adapters
- Improved deduplication algorithms
- Web API and visualization tools
- Integration with online databases

## License

This integration system is provided for educational and research purposes. Please respect the licenses and terms of use for each original data source.
