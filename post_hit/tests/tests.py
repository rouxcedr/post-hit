#!/usr/bin/env python
import unittest
import os, shutil
from tempfile import TemporaryDirectory
import pandas as pd
import numpy as np
from .. import dataset
from gepyto.structures.region import Region
from .. import adapters

POST_HIT_PATH = os.path.abspath(__file__ + "/../../") + "/"

print(POST_HIT_PATH)



class TestDataSet(unittest.TestCase):

    def setUp(self):
         # Creating a temporary directory
        self.output_dir = TemporaryDirectory(prefix="post_hit_dataset_test_")

    def test_dataset(self):

        self.assertTrue(isinstance(dataset.DataSet(dataset_path = "roadmap_epigenomic.json"), dataset.DataSet))
        self.assertTrue(isinstance(dataset.DataSet(dataset_path = "".join([POST_HIT_PATH,"data/datasets/phyloP100way.json"])), dataset.DataSet))
        self.assertTrue(isinstance(dataset.DataSet(dataset_path ="ensembl"), dataset.DataSet))
        self.assertTrue(isinstance(dataset.DataSet(dataset_path = "gtex.json"), dataset.DataSet))

        self.assertRaises(ValueError, dataset.DataSet,"gtex.txt")
        self.assertRaises(ValueError, dataset.DataSet,"dummy")
        self.assertRaises(ValueError, dataset.DataSet,"dummy.json")

        self.dummy_dataset = dataset.DataSet(dataset_path = POST_HIT_PATH + "tmp/dummy_test.json",
                                    project= "TEST",
                                    description= "Dummy Test JSON FILE",
                                    project_link= "dummy.test",
                                    version= 0,
                                    data_path= "tmp/",
                                    protocole= "ftp",
                                    file_type= "gtf",
                                    ids=["DummyTest"],
                                    download_links=["ftp://ftp.ensembl.org/pub/release-75//gtf/homo_sapiens"],
                                    filenames=["DummyTest.gtf.gz"],
                                    metadata= [],
                                    data_representation={})

        self.assertTrue(isinstance(self.dummy_dataset, dataset.DataSet))
        self.assertTrue(os.path.exists(POST_HIT_PATH + "tmp/DummyTest.gtf.gz"), dataset.DataSet)
        folder = POST_HIT_PATH + 'tmp/'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): 
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)


    def tearDown(self):
        """Finishes the test."""
        # Deleting the output directory
        self.output_dir.cleanup()

class TestAdapter(unittest.TestCase):

    def setUp(self):
         # Creating a temporary directory
        self.output_dir = TemporaryDirectory(prefix="post_hit_adapter_test_")
        self.region = Region("19", 45819671, 45826235)

        self.bbadapter = adapters.BigBedAdapter(dataset_path = "".join([POST_HIT_PATH,"data/datasets/roadmap_epigenomic.json"]))
        self.bwadapter = adapters.BigWigAdapter(dataset_path = "".join([POST_HIT_PATH,"data/datasets/phyloP100way.json"]))
        self.gtfadapter = adapters.GTFAdapter(dataset_path ="".join([POST_HIT_PATH,"data/datasets/ensembl.json"]))
        self.xsvadapter = adapters.XsvAdapter(dataset_path = "".join([POST_HIT_PATH,"data/datasets/gtex.json"]), sep = "\t")

        self.bbadapter_error = adapters.BigBedAdapter(dataset_path = "".join([POST_HIT_PATH,"data/datasets/gtex.json"]))

    
    def test_adapter(self):
        self.assertTrue(isinstance(self.bbadapter, adapters.Adapter))
        self.assertTrue(isinstance(self.bwadapter, adapters.Adapter))
        self.assertTrue(isinstance(self.gtfadapter, adapters.Adapter))
        self.assertTrue(isinstance(self.xsvadapter, adapters.Adapter))

    def test_get_region(self):
        
        result = self.bbadapter.get_region(self.region)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(bool(result))

        result = self.bwadapter.get_region(self.region)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(bool(result))

        result = self.gtfadapter.get_region(self.region)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(bool(result))

        result = self.xsvadapter.get_region(self.region)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(bool(result))

    def tearDown(self):
        """Finishes the test."""
        # Deleting the output directory
        self.output_dir.cleanup()
