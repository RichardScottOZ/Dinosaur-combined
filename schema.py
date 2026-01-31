"""
Unified Schema for Dinosaur Archives Integration

This module defines the comprehensive schema that integrates data from multiple
major dinosaur databases including:
- The Paleobiology Database (PBDB)
- American Museum of Natural History (AMNH)
- DinoData
- Natural History Museum (London) Dino Directory
- DinoAnimals Complete Dinosaur Database
- National Park Service Paleontology Archives
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class DinosaurClade(Enum):
    """Major dinosaur clades"""
    THEROPODA = "Theropoda"
    SAUROPODOMORPHA = "Sauropodomorpha"
    ORNITHISCHIA = "Ornithischia"
    UNKNOWN = "Unknown"


class GeologicalPeriod(Enum):
    """Geological time periods"""
    TRIASSIC = "Triassic"
    JURASSIC = "Jurassic"
    CRETACEOUS = "Cretaceous"
    UNKNOWN = "Unknown"


class FossilQuality(Enum):
    """Quality assessment of fossil remains"""
    EXCELLENT = "Excellent"  # Complete or near-complete skeleton
    GOOD = "Good"  # Substantial remains
    MODERATE = "Moderate"  # Fragmentary but diagnostic
    POOR = "Poor"  # Limited fragmentary remains
    UNKNOWN = "Unknown"


@dataclass
class TaxonomicClassification:
    """Complete taxonomic classification"""
    kingdom: str = "Animalia"
    phylum: str = "Chordata"
    class_name: str = "Reptilia"
    superorder: str = "Dinosauria"
    order: Optional[str] = None
    suborder: Optional[str] = None
    infraorder: Optional[str] = None
    superfamily: Optional[str] = None
    family: Optional[str] = None
    subfamily: Optional[str] = None
    genus: Optional[str] = None
    species: Optional[str] = None
    

@dataclass
class GeographicLocation:
    """Geographic information for fossil discovery"""
    country: Optional[str] = None
    state_province: Optional[str] = None
    locality: Optional[str] = None
    formation: Optional[str] = None  # Geological formation
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = None  # in meters
    paleolocation: Optional[str] = None  # Ancient geographic location
    

@dataclass
class StratigraphicInfo:
    """Stratigraphic and temporal information"""
    geological_period: GeologicalPeriod = GeologicalPeriod.UNKNOWN
    epoch: Optional[str] = None
    stage: Optional[str] = None
    age_min_ma: Optional[float] = None  # Minimum age in millions of years
    age_max_ma: Optional[float] = None  # Maximum age in millions of years
    formation_name: Optional[str] = None
    member_name: Optional[str] = None
    

@dataclass
class PhysicalCharacteristics:
    """Physical characteristics and measurements"""
    length_meters: Optional[float] = None
    height_meters: Optional[float] = None
    weight_kg: Optional[float] = None
    diet: Optional[str] = None  # Carnivore, Herbivore, Omnivore
    locomotion: Optional[str] = None  # Bipedal, Quadrupedal
    distinctive_features: List[str] = field(default_factory=list)
    

@dataclass
class Reference:
    """Bibliographic reference"""
    reference_id: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[int] = None
    title: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    

@dataclass
class MuseumCollection:
    """Museum collection information"""
    institution: Optional[str] = None
    collection_code: Optional[str] = None
    catalog_number: Optional[str] = None
    specimen_count: Optional[int] = None
    holotype: bool = False  # Is this the type specimen?
    

@dataclass
class DataSource:
    """Tracks the origin of data"""
    source_database: str  # PBDB, AMNH, DinoData, etc.
    source_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    data_quality: Optional[str] = None
    url: Optional[str] = None
    

@dataclass
class Dinosaur:
    """
    Comprehensive dinosaur record integrating data from all major archives.
    
    This is the primary data model that combines information from:
    - Paleobiology Database (PBDB)
    - American Museum of Natural History
    - DinoData
    - Natural History Museum London
    - DinoAnimals Database
    - National Park Service archives
    """
    
    # Core identification
    record_id: str  # Unique identifier in combined database
    scientific_name: str  # Full binomial name
    common_name: Optional[str] = None
    
    # Taxonomic information
    taxonomy: TaxonomicClassification = field(default_factory=TaxonomicClassification)
    clade: DinosaurClade = DinosaurClade.UNKNOWN
    
    # Geographic and stratigraphic data
    location: GeographicLocation = field(default_factory=GeographicLocation)
    stratigraphy: StratigraphicInfo = field(default_factory=StratigraphicInfo)
    
    # Physical characteristics
    characteristics: PhysicalCharacteristics = field(default_factory=PhysicalCharacteristics)
    
    # Fossil information
    fossil_quality: FossilQuality = FossilQuality.UNKNOWN
    fossil_elements: List[str] = field(default_factory=list)  # skull, femur, vertebrae, etc.
    
    # Museum and collection data
    collections: List[MuseumCollection] = field(default_factory=list)
    
    # References and sources
    references: List[Reference] = field(default_factory=list)
    data_sources: List[DataSource] = field(default_factory=list)
    
    # Additional metadata
    discovery_year: Optional[int] = None
    discoverer: Optional[str] = None
    etymology: Optional[str] = None  # Name meaning/origin
    description: Optional[str] = None
    images: List[str] = field(default_factory=list)  # URLs to images
    
    # Validity and taxonomy status
    valid_name: bool = True  # False if synonym or invalid
    accepted_name: Optional[str] = None  # If this is a synonym, what's the valid name
    
    # Notes and additional data
    notes: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"{self.scientific_name} ({self.clade.value})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'record_id': self.record_id,
            'scientific_name': self.scientific_name,
            'common_name': self.common_name,
            'taxonomy': {
                'genus': self.taxonomy.genus,
                'species': self.taxonomy.species,
                'family': self.taxonomy.family,
                'order': self.taxonomy.order,
            },
            'clade': self.clade.value,
            'location': {
                'country': self.location.country,
                'locality': self.location.locality,
                'formation': self.location.formation,
            },
            'stratigraphy': {
                'period': self.stratigraphy.geological_period.value,
                'age_min_ma': self.stratigraphy.age_min_ma,
                'age_max_ma': self.stratigraphy.age_max_ma,
            },
            'characteristics': {
                'length_meters': self.characteristics.length_meters,
                'diet': self.characteristics.diet,
            },
            'valid_name': self.valid_name,
            'data_sources': [s.source_database for s in self.data_sources],
        }


@dataclass
class FossilSite:
    """
    Information about a fossil site/locality
    """
    site_id: str
    site_name: str
    location: GeographicLocation = field(default_factory=GeographicLocation)
    stratigraphy: StratigraphicInfo = field(default_factory=StratigraphicInfo)
    dinosaurs_found: List[str] = field(default_factory=list)  # List of dinosaur record_ids
    excavation_history: Optional[str] = None
    references: List[Reference] = field(default_factory=list)
    data_sources: List[DataSource] = field(default_factory=list)


@dataclass
class DinosaurDatabase:
    """
    The complete integrated database
    """
    dinosaurs: Dict[str, Dinosaur] = field(default_factory=dict)  # keyed by record_id
    sites: Dict[str, FossilSite] = field(default_factory=dict)  # keyed by site_id
    
    def add_dinosaur(self, dinosaur: Dinosaur) -> None:
        """Add a dinosaur record to the database"""
        self.dinosaurs[dinosaur.record_id] = dinosaur
    
    def add_site(self, site: FossilSite) -> None:
        """Add a fossil site to the database"""
        self.sites[site.site_id] = site
    
    def get_by_name(self, scientific_name: str) -> Optional[Dinosaur]:
        """Find dinosaur by scientific name"""
        for dinosaur in self.dinosaurs.values():
            if dinosaur.scientific_name == scientific_name:
                return dinosaur
        return None
    
    def get_by_period(self, period: GeologicalPeriod) -> List[Dinosaur]:
        """Get all dinosaurs from a specific geological period"""
        return [d for d in self.dinosaurs.values() 
                if d.stratigraphy.geological_period == period]
    
    def get_by_clade(self, clade: DinosaurClade) -> List[Dinosaur]:
        """Get all dinosaurs from a specific clade"""
        return [d for d in self.dinosaurs.values() if d.clade == clade]
    
    def stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_dinosaurs': len(self.dinosaurs),
            'total_sites': len(self.sites),
            'by_period': {
                period.value: len(self.get_by_period(period))
                for period in GeologicalPeriod
            },
            'by_clade': {
                clade.value: len(self.get_by_clade(clade))
                for clade in DinosaurClade
            }
        }
