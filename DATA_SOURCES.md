# Data Sources Documentation

## Overview of Integrated Dinosaur Databases

This document provides detailed information about each of the major dinosaur databases integrated into the Dinosaur-combined system.

---

## 1. The Paleobiology Database (PBDB)

**Website:** https://paleobiodb.org/

**Description:**  
The Paleobiology Database is a public, international database of fossil occurrences maintained by hundreds of paleontologists worldwide. It provides comprehensive data on dinosaurs and other prehistoric life.

**Key Features:**
- Global fossil occurrence data
- Taxonomic classifications
- Geographic coordinates
- Stratigraphic information (geological periods, formations)
- Bibliographic references
- Open API for developers

**Data Fields Provided:**
- `occurrence_no`: Unique occurrence identifier
- `taxon_no`: Taxonomic identifier
- `genus`, `species`: Taxonomic names
- `order`, `family`: Higher taxonomy
- `interval`: Geological time period
- `max_ma`, `min_ma`: Age range in millions of years
- `cc`: Country code
- `state`: State/province
- `lat`, `lng`: Coordinates
- `formation`: Geological formation
- `reference_no`: Reference ID

**Usage in Integration:**
- Primary source for fossil occurrence data
- Geographic and stratigraphic information
- Temporal range data

---

## 2. American Museum of Natural History (AMNH)

**Website:** https://www.amnh.org/research/paleontology/collections/

**Description:**  
The AMNH maintains one of the world's largest collections of dinosaur fossils and provides a comprehensive database of their specimens.

**Key Features:**
- Museum specimen catalog
- Collection metadata
- Type specimen information
- Images and media
- Field notes and historical documents

**Data Fields Provided:**
- `specimen_id`: Unique specimen identifier
- `catalog_number`: Museum catalog number (e.g., AMNH-5027)
- `genus`, `species`: Taxonomic names
- `collection`: Collection name
- `type_status`: Whether holotype, paratype, etc.
- `country`, `state_province`, `locality`: Location data
- `images`: URLs to specimen images

**Usage in Integration:**
- Museum collection tracking
- Type specimen identification
- High-quality specimen images

---

## 3. DinoData

**Website:** https://www.ipl.org/dinodata/

**Description:**  
A comprehensive online database offering scientific classification, fossil site data, maps, and detailed dinosaur information across 6,000+ pages of scholarly content.

**Key Features:**
- Detailed taxonomic data
- Physical characteristics (size, weight)
- Discovery information
- Etymology and naming
- Behavioral information

**Data Fields Provided:**
- `id`: Record identifier
- `genus`, `species`, `common_name`: Names
- `order`, `family`: Taxonomy
- `clade`: Major dinosaur group
- `period`: Geological period
- `country`, `locality`, `formation`: Location
- `length_m`, `height_m`, `weight_kg`: Measurements
- `diet`: Feeding behavior
- `locomotion`: Movement type
- `discovery_year`, `discoverer`: Discovery info
- `etymology`: Name meaning
- `description`: Detailed description

**Usage in Integration:**
- Physical characteristic data
- Discovery history
- Educational descriptions

---

## 4. Natural History Museum London - Dino Directory

**Website:** https://www.nhm.ac.uk/

**Description:**  
The Natural History Museum in London provides a curated directory of dinosaur species with educational content, images, and scientific information.

**Key Features:**
- Curated species information
- Educational descriptions
- Professional images
- Geographic and temporal data

**Data Fields Provided:**
- `id`: Record identifier
- `genus`, `species`, `common_name`: Names
- `order`, `family`: Taxonomy
- `period`: Geological period
- `country`: Discovery location
- `description`: Detailed description
- `images`: URLs to images
- `url`: Link to full record

**Usage in Integration:**
- Educational content
- High-quality images
- Verified species information

---

## 5. DinoAnimals Complete Dinosaur Database

**Website:** https://dinoanimals.com/dinosaurs/complete-dinosaurs-database/

**Description:**  
The largest, most complete, and regularly updated list of dinosaur genera and species, containing more than 1,900 species and 1,600 genera. Created by professional biologists and paleontologists.

**Key Features:**
- Most comprehensive species list
- Regular updates
- Size information
- Taxonomic validity tracking

**Data Fields Provided:**
- `id`: Record identifier
- `genus`, `species`: Taxonomic names
- `order`, `family`: Higher taxonomy
- `period`: Geological period
- `length`, `weight`: Size measurements
- `diet`: Feeding behavior
- `valid`: Whether name is currently valid
- `accepted_name`: Valid name if this is a synonym

**Usage in Integration:**
- Comprehensive species coverage
- Synonym tracking
- Size data

---

## 6. National Park Service Paleontology Archives

**Website:** https://www.nps.gov/subjects/fossils/

**Description:**  
The U.S. National Park Service maintains archives for fossil sites within national parks, including digital and physical records of discoveries.

**Key Features:**
- U.S. fossil site data
- Park location information
- Excavation history
- Management records

**Usage in Integration:**
- U.S. fossil site information
- Public land fossil data
- Excavation history

---

## Data Integration Strategy

### Mapping Strategy

Each data source has unique field names and structures. The integration system uses **adapters** to map source-specific fields to the unified schema:

```
PBDB 'cc' → Unified 'country'
PBDB 'max_ma' → Unified 'age_min_ma' (older age)
PBDB 'min_ma' → Unified 'age_max_ma' (younger age)

DinoData 'length_m' → Unified 'length_meters'
DinoData 'period' → Unified 'geological_period'

AMNH 'catalog_number' → Unified MuseumCollection
```

### Deduplication

Records are identified as duplicates using:
1. **Exact name matching**: Same scientific name
2. **Fuzzy matching**: Same genus + temporal/geographic overlap

### Conflict Resolution

When merging duplicate records:
- **Prefer more precise data**: Specific measurements over ranges
- **Combine references**: Keep all source references
- **Track provenance**: Maintain all data source information
- **Preserve completeness**: Never discard data during merge

### Data Quality

Quality is maintained through:
- **Validation rules**: Check for required fields
- **Range checks**: Validate measurements (no negative values)
- **Consistency checks**: Ensure temporal/geographic consistency
- **Source tracking**: Always know where data originated

---

## Extending with New Sources

To add a new data source:

1. **Create Adapter Class** in `adapters.py`:
```python
class NewSourceAdapter(BaseAdapter):
    def __init__(self):
        super().__init__("New Source Name")
    
    def parse_record(self, record):
        # Map fields to unified schema
        return Dinosaur(...)
```

2. **Register in Factory** in `AdapterFactory`:
```python
_adapters = {
    'newsource': NewSourceAdapter,
    ...
}
```

3. **Test Integration**:
```python
integrator.add_records_from_source('newsource', records)
```

---

## Data Source Credits and Licenses

- **PBDB**: Creative Commons CC-BY license
- **AMNH**: Copyright American Museum of Natural History
- **DinoData**: Educational use permitted
- **NHM London**: Copyright Natural History Museum
- **DinoAnimals**: Copyright DinoAnimals.com

**Important:** Always respect the original licenses and terms of use for each data source. This integration system is for research and educational purposes.

---

## API Endpoints (Future Enhancement)

Potential integration with live APIs:

- **PBDB API**: `https://paleobiodb.org/data1.2/occs/list.json`
- **GBIF API**: For PBDB data via GBIF
- **Wikidata SPARQL**: For taxonomic data

---

## References

1. The Paleobiology Database. https://paleobiodb.org/
2. American Museum of Natural History. https://www.amnh.org/
3. DinoData. https://www.ipl.org/dinodata/
4. Natural History Museum London. https://www.nhm.ac.uk/
5. DinoAnimals Complete Database. https://dinoanimals.com/
6. National Park Service Fossils. https://www.nps.gov/subjects/fossils/
