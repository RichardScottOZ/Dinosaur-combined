"""
Unit tests for the Dinosaur Database Integration System
"""

import unittest
import json
import os
import subprocess
import sys
import tempfile
from schema import (
    Dinosaur, TaxonomicClassification, GeographicLocation,
    StratigraphicInfo, PhysicalCharacteristics, DataSource,
    DinosaurClade, GeologicalPeriod, DinosaurDatabase
)
from adapters import (
    PBDBAdapter, DinoDataAdapter, AMNHAdapter, AdapterFactory
)
from integrator import DataIntegrator


class TestSchema(unittest.TestCase):
    """Test the unified schema"""
    
    def test_dinosaur_creation(self):
        """Test creating a basic dinosaur record"""
        dino = Dinosaur(
            record_id="test_001",
            scientific_name="Tyrannosaurus rex"
        )
        self.assertEqual(dino.scientific_name, "Tyrannosaurus rex")
        self.assertEqual(dino.record_id, "test_001")
        self.assertEqual(dino.clade, DinosaurClade.UNKNOWN)
    
    def test_dinosaur_with_taxonomy(self):
        """Test dinosaur with complete taxonomy"""
        taxonomy = TaxonomicClassification(
            genus="Tyrannosaurus",
            species="rex",
            family="Tyrannosauridae",
            order="Theropoda"
        )
        
        dino = Dinosaur(
            record_id="test_002",
            scientific_name="Tyrannosaurus rex",
            taxonomy=taxonomy,
            clade=DinosaurClade.THEROPODA
        )
        
        self.assertEqual(dino.taxonomy.genus, "Tyrannosaurus")
        self.assertEqual(dino.taxonomy.family, "Tyrannosauridae")
        self.assertEqual(dino.clade, DinosaurClade.THEROPODA)
    
    def test_dinosaur_to_dict(self):
        """Test converting dinosaur to dictionary"""
        dino = Dinosaur(
            record_id="test_003",
            scientific_name="Velociraptor mongoliensis",
            common_name="Velociraptor"
        )
        
        dino_dict = dino.to_dict()
        self.assertIn('record_id', dino_dict)
        self.assertIn('scientific_name', dino_dict)
        self.assertEqual(dino_dict['scientific_name'], "Velociraptor mongoliensis")
    
    def test_database_operations(self):
        """Test database add and query operations"""
        db = DinosaurDatabase()
        
        dino1 = Dinosaur(
            record_id="test_004",
            scientific_name="Triceratops horridus",
            clade=DinosaurClade.ORNITHISCHIA
        )
        
        dino2 = Dinosaur(
            record_id="test_005",
            scientific_name="Stegosaurus stenops",
            clade=DinosaurClade.ORNITHISCHIA
        )
        
        db.add_dinosaur(dino1)
        db.add_dinosaur(dino2)
        
        # Test retrieval
        self.assertEqual(len(db.dinosaurs), 2)
        
        found = db.get_by_name("Triceratops horridus")
        self.assertIsNotNone(found)
        self.assertEqual(found.record_id, "test_004")
        
        # Test by clade
        ornithischians = db.get_by_clade(DinosaurClade.ORNITHISCHIA)
        self.assertEqual(len(ornithischians), 2)


class TestAdapters(unittest.TestCase):
    """Test data source adapters"""
    
    def test_pbdb_adapter(self):
        """Test PBDB adapter parsing"""
        adapter = PBDBAdapter()
        
        record = {
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
            'formation': 'Hell Creek'
        }
        
        dinosaur = adapter.parse_record(record)
        
        self.assertIsNotNone(dinosaur)
        self.assertEqual(dinosaur.scientific_name, "Tyrannosaurus rex")
        self.assertEqual(dinosaur.taxonomy.genus, "Tyrannosaurus")
        self.assertEqual(dinosaur.taxonomy.species, "rex")
        self.assertEqual(dinosaur.location.country, "US")
        self.assertEqual(dinosaur.stratigraphy.geological_period, GeologicalPeriod.CRETACEOUS)
        self.assertEqual(len(dinosaur.data_sources), 1)
        self.assertEqual(dinosaur.data_sources[0].source_database, "Paleobiology Database (PBDB)")
    
    def test_dinodata_adapter(self):
        """Test DinoData adapter parsing"""
        adapter = DinoDataAdapter()
        
        record = {
            'id': '2001',
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
            'diet': 'Carnivore'
        }
        
        dinosaur = adapter.parse_record(record)
        
        self.assertIsNotNone(dinosaur)
        self.assertEqual(dinosaur.scientific_name, "Velociraptor mongoliensis")
        self.assertEqual(dinosaur.common_name, "Velociraptor")
        self.assertEqual(dinosaur.characteristics.length_meters, 2.0)
        self.assertEqual(dinosaur.characteristics.weight_kg, 15.0)
        self.assertEqual(dinosaur.characteristics.diet, "Carnivore")
        self.assertEqual(dinosaur.clade, DinosaurClade.THEROPODA)
    
    def test_amnh_adapter(self):
        """Test AMNH adapter parsing"""
        adapter = AMNHAdapter()
        
        record = {
            'specimen_id': '3001',
            'catalog_number': 'AMNH-5027',
            'genus': 'Tyrannosaurus',
            'species': 'rex',
            'collection': 'Vertebrate Paleontology',
            'type_status': 'holotype',
            'country': 'United States'
        }
        
        dinosaur = adapter.parse_record(record)
        
        self.assertIsNotNone(dinosaur)
        self.assertEqual(dinosaur.scientific_name, "Tyrannosaurus rex")
        self.assertEqual(len(dinosaur.collections), 1)
        self.assertEqual(dinosaur.collections[0].catalog_number, "AMNH-5027")
        self.assertTrue(dinosaur.collections[0].holotype)
    
    def test_adapter_factory(self):
        """Test adapter factory"""
        # Test getting adapters by different names
        pbdb1 = AdapterFactory.get_adapter('pbdb')
        pbdb2 = AdapterFactory.get_adapter('paleobiology_database')
        
        self.assertIsInstance(pbdb1, PBDBAdapter)
        self.assertIsInstance(pbdb2, PBDBAdapter)
        
        # Test invalid source
        with self.assertRaises(ValueError):
            AdapterFactory.get_adapter('invalid_source')


class TestIntegration(unittest.TestCase):
    """Test the integration engine"""
    
    def test_basic_integration(self):
        """Test basic record integration"""
        integrator = DataIntegrator()
        
        records = [
            {
                'occurrence_no': '1001',
                'genus': 'Tyrannosaurus',
                'species': 'rex',
                'order': 'Theropoda',
                'interval': 'Cretaceous'
            }
        ]
        
        count = integrator.add_records_from_source('pbdb', records)
        self.assertEqual(count, 1)
        self.assertEqual(len(integrator.database.dinosaurs), 1)
    
    def test_deduplication(self):
        """Test that duplicate records are merged"""
        integrator = DataIntegrator()
        
        # Add same dinosaur from two sources
        pbdb_record = {
            'occurrence_no': '1001',
            'genus': 'Tyrannosaurus',
            'species': 'rex',
            'order': 'Theropoda',
            'interval': 'Cretaceous',
            'cc': 'US'
        }
        
        dinodata_record = {
            'id': '2001',
            'genus': 'Tyrannosaurus',
            'species': 'rex',
            'order': 'Theropoda',
            'period': 'Cretaceous',
            'length_m': 12.0
        }
        
        integrator.add_records_from_source('pbdb', [pbdb_record])
        integrator.add_records_from_source('dinodata', [dinodata_record])
        
        # Should only have 1 record, merged from both sources
        self.assertEqual(len(integrator.database.dinosaurs), 1)
        
        trex = integrator.database.get_by_name("Tyrannosaurus rex")
        self.assertIsNotNone(trex)
        
        # Should have data from both sources
        self.assertEqual(len(trex.data_sources), 2)
        self.assertEqual(trex.location.country, "US")  # From PBDB
        self.assertEqual(trex.characteristics.length_meters, 12.0)  # From DinoData
    
    def test_statistics(self):
        """Test statistics generation"""
        integrator = DataIntegrator()
        
        # Add some diverse records
        pbdb_records = [
            {'occurrence_no': '1', 'genus': 'T1', 'species': 's1', 'order': 'Theropoda', 'interval': 'Cretaceous'},
            {'occurrence_no': '2', 'genus': 'T2', 'species': 's2', 'order': 'Ornithischia', 'interval': 'Jurassic'},
            {'occurrence_no': '3', 'genus': 'T3', 'species': 's3', 'order': 'Sauropodomorpha', 'interval': 'Jurassic'},
        ]
        
        integrator.add_records_from_source('pbdb', pbdb_records)
        
        stats = integrator.get_statistics()
        
        self.assertEqual(stats['unique_species'], 3)
        self.assertIn('by_period', stats)
        self.assertIn('by_clade', stats)
    
    def test_export_import(self):
        """Test JSON export and import"""
        integrator = DataIntegrator()
        
        records = [
            {
                'occurrence_no': '1001',
                'genus': 'Triceratops',
                'species': 'horridus',
                'order': 'Ornithischia',
                'interval': 'Cretaceous'
            }
        ]
        
        integrator.add_records_from_source('pbdb', records)
        
        # Export
        test_file = '/tmp/test_export.json'
        integrator.export_to_json(test_file)
        
        # Verify file exists and contains data
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('dinosaurs', data)
        self.assertIn('metadata', data)
        self.assertEqual(len(data['dinosaurs']), 1)


class TestCLI(unittest.TestCase):
    """Test the command-line interface"""

    def test_module_entry_point_generates_sample_database(self):
        """Test running the CLI module entry point"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'sample_database.json')
            result = subprocess.run(
                [sys.executable, '-m', 'dinosaur_cli', 'sample', '--output', output_path],
                capture_output=True,
                text=True,
                check=False
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, 'r') as output_file:
                data = json.load(output_file)

            self.assertIn('dinosaurs', data)
            self.assertIn('metadata', data)
            self.assertIsInstance(data['dinosaurs'], list)
            self.assertGreater(len(data['dinosaurs']), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestAdapters))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
