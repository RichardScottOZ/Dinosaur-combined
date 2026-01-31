# Dinosaur Database Integration System

A comprehensive system for integrating data from multiple major dinosaur archives and databases into one unified, cohesive database with a standardized schema.

## Overview

This project combines data from the following major dinosaur databases:

- **The Paleobiology Database (PBDB)** - Global fossil occurrence data
- **American Museum of Natural History (AMNH)** - Museum collection records
- **DinoData** - Comprehensive dinosaur information database
- **Natural History Museum London** - Dino Directory
- **DinoAnimals Complete Database** - Complete genus and species listings
- **National Park Service Paleontology Archives** - US fossil site data

## Features

- **Unified Schema**: Comprehensive data model accommodating all data sources
- **Data Adapters**: Source-specific adapters for seamless integration
- **Deduplication**: Intelligent merging of duplicate records across sources
- **Conflict Resolution**: Smart handling of conflicting data from different sources
- **Query Interface**: Command-line tools for searching and analyzing data
- **Export/Import**: JSON-based data exchange format
- **Validation**: Built-in data quality checks

## Architecture

### Core Components

1. **schema.py** - Unified data model
   - `Dinosaur`: Main dinosaur record with comprehensive fields
   - `TaxonomicClassification`: Full taxonomic hierarchy
   - `GeographicLocation`: Location and coordinates
   - `StratigraphicInfo`: Geological time and formation data
   - `PhysicalCharacteristics`: Size, diet, locomotion
   - `MuseumCollection`: Collection and specimen data
   - `Reference`: Bibliographic references
   - `DataSource`: Source tracking and provenance

2. **adapters.py** - Data source adapters
   - `PBDBAdapter`: Paleobiology Database adapter
   - `AMNHAdapter`: AMNH collection adapter
   - `DinoDataAdapter`: DinoData adapter
   - `NHMLondonAdapter`: Natural History Museum adapter
   - `DinoAnimalsAdapter`: DinoAnimals database adapter
   - `AdapterFactory`: Factory for creating adapters

3. **integrator.py** - Integration engine
   - `DataIntegrator`: Main integration logic
   - Deduplication and merging
   - Synonym resolution
   - Data validation
   - Statistics and reporting

4. **dinosaur_cli.py** - Command-line interface
   - Import data from sources
   - Query and search
   - Export to JSON
   - Statistics and validation

## Installation

```bash
# Clone the repository
git clone https://github.com/RichardScottOZ/Dinosaur-combined.git
cd Dinosaur-combined

# No external dependencies required - uses Python standard library only
# Requires Python 3.7+
```

## Usage

### Command-Line Interface

#### Generate Sample Database

```bash
python dinosaur_cli.py sample --output sample_database.json
```

#### Import Data

```bash
# Import from PBDB
python dinosaur_cli.py import pbdb pbdb_data.json --output integrated.json

# Import from DinoData
python dinosaur_cli.py import dinodata dinodata_records.json --output integrated.json
```

#### Query Database

```bash
# Search by name
python dinosaur_cli.py query --name "Tyrannosaurus"

# Filter by period
python dinosaur_cli.py query --period cretaceous

# Filter by clade
python dinosaur_cli.py query --clade theropoda

# Filter by genus
python dinosaur_cli.py query --genus "Triceratops"
```

#### Statistics

```bash
python dinosaur_cli.py stats --database dinosaur_database.json
```

#### Validate Database

```bash
python dinosaur_cli.py validate --database dinosaur_database.json
```

#### List Available Sources

```bash
python dinosaur_cli.py sources
```

### Python API

```python
from integrator import DataIntegrator, create_sample_data
from adapters import AdapterFactory
from schema import Dinosaur, DinosaurClade, GeologicalPeriod

# Create integrator
integrator = DataIntegrator()

# Import from different sources
pbdb_records = [...]  # Load from PBDB API or file
integrator.add_records_from_source('pbdb', pbdb_records)

dinodata_records = [...]  # Load from DinoData
integrator.add_records_from_source('dinodata', dinodata_records)

# Query the database
tyrannosaurus = integrator.database.get_by_name("Tyrannosaurus rex")
print(tyrannosaurus.scientific_name)
print(tyrannosaurus.characteristics.length_meters)

# Get all Cretaceous dinosaurs
cretaceous_dinos = integrator.database.get_by_period(GeologicalPeriod.CRETACEOUS)

# Get statistics
stats = integrator.get_statistics()
print(f"Total unique species: {stats['unique_species']}")
print(f"Merged records: {stats['total_merged_records']}")

# Export to JSON
integrator.export_to_json('combined_database.json')
```

## Data Schema

### Unified Dinosaur Record

Each dinosaur record includes:

- **Identification**
  - Unique record ID
  - Scientific name (genus + species)
  - Common name(s)
  - Valid/synonym status

- **Taxonomy**
  - Complete classification from Kingdom to Species
  - Major clade (Theropoda, Sauropodomorpha, Ornithischia)

- **Geographic Data**
  - Country, state/province, locality
  - Coordinates (latitude, longitude)
  - Geological formation
  - Paleo-location

- **Temporal Data**
  - Geological period, epoch, stage
  - Age range in millions of years
  - Formation and member names

- **Physical Characteristics**
  - Length, height, weight
  - Diet (carnivore, herbivore, omnivore)
  - Locomotion (bipedal, quadrupedal)
  - Distinctive features

- **Fossil Information**
  - Quality assessment
  - Preserved elements (skull, bones, etc.)

- **Museum Collections**
  - Institution name
  - Catalog numbers
  - Type specimen status

- **References**
  - Authors, year, title
  - Journal, volume, pages
  - DOI and URLs

- **Metadata**
  - Data sources and provenance
  - Discovery year and discoverer
  - Etymology
  - Images and media

## Data Integration Process

1. **Input**: Raw records from various sources
2. **Adaptation**: Source-specific adapter transforms to unified schema
3. **Deduplication**: Matching algorithm identifies duplicates
4. **Merging**: Duplicate records merged, combining data from all sources
5. **Validation**: Data quality checks and consistency validation
6. **Output**: Unified, integrated database

### Deduplication Strategy

Records are considered duplicates if:
- Exact scientific name match, OR
- Same genus AND temporal/geographic overlap

### Merging Strategy

When merging duplicate records:
- Combine all data sources
- Merge collections and references
- Prefer more complete/precise data
- Track all source IDs for provenance

## Example Data Formats

### PBDB Format

```json
{
  "occurrence_no": "1001",
  "taxon_no": "5001",
  "genus": "Tyrannosaurus",
  "species": "rex",
  "order": "Theropoda",
  "family": "Tyrannosauridae",
  "interval": "Cretaceous",
  "max_ma": 68.0,
  "min_ma": 66.0,
  "cc": "US",
  "state": "Montana",
  "locality": "Hell Creek Formation",
  "formation": "Hell Creek",
  "lat": 47.5,
  "lng": -107.0
}
```

### DinoData Format

```json
{
  "id": "2001",
  "genus": "Velociraptor",
  "species": "mongoliensis",
  "common_name": "Velociraptor",
  "order": "Theropoda",
  "family": "Dromaeosauridae",
  "clade": "Theropoda",
  "period": "Cretaceous",
  "country": "Mongolia",
  "length_m": 2.0,
  "weight_kg": 15.0,
  "diet": "Carnivore"
}
```

### AMNH Format

```json
{
  "specimen_id": "3001",
  "catalog_number": "AMNH-5027",
  "genus": "Tyrannosaurus",
  "species": "rex",
  "collection": "Vertebrate Paleontology",
  "type_status": "holotype",
  "country": "United States"
}
```

## Extending the System

### Adding New Data Sources

1. Create a new adapter class in `adapters.py`:

```python
class MyDatabaseAdapter(BaseAdapter):
    def __init__(self):
        super().__init__("My Database Name")
    
    def parse_record(self, record: Dict[str, Any]) -> Optional[Dinosaur]:
        # Transform record to unified schema
        taxonomy = TaxonomicClassification(...)
        location = GeographicLocation(...)
        # ... create Dinosaur object
        return dinosaur
```

2. Register the adapter in `AdapterFactory`:

```python
_adapters = {
    'mydatabase': MyDatabaseAdapter,
    ...
}
```

3. Use the new adapter:

```python
integrator.add_records_from_source('mydatabase', my_records)
```

## Contributing

Contributions are welcome! Areas for enhancement:

- Additional data source adapters
- Improved deduplication algorithms
- Web API for querying the database
- Visualization tools
- Data quality improvements
- Integration with online databases

## Data Sources and Credits

This system integrates data from:

- **Paleobiology Database** (https://paleobiodb.org/)
- **American Museum of Natural History** (https://www.amnh.org/)
- **DinoData** (https://www.ipl.org/dinodata/)
- **Natural History Museum London** (https://www.nhm.ac.uk/)
- **DinoAnimals** (https://dinoanimals.com/)

Please respect the licenses and terms of use for each original data source.

## License

This integration system is provided as-is for educational and research purposes.

## Future Enhancements

- [ ] Real-time API integration with source databases
- [ ] Web interface for browsing and searching
- [ ] Geographic visualization of fossil sites
- [ ] Temporal range visualization
- [ ] Phylogenetic tree integration
- [ ] Image gallery and 3D models
- [ ] Export to other formats (CSV, SQL, RDF)
- [ ] Machine learning for improved deduplication
- [ ] Automated data quality scoring
- [ ] Integration with additional archives
