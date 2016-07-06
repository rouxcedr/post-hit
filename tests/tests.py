#!/usr/bin/env python
import unittest
import os
from tempfile import TemporaryDirectory

import pandas as pd
import numpy as np

import dataset, adapters
POST_HIT_PATH = os.path.abspath(".")+"/"


class TestDataSet(unittest.TestCase):

    def setUp(self):
         # Creating a temporary directory
        self.output_dir = TemporaryDirectory(prefix="post_hit_dataset_test_")

        selt.test_dataset()

    def test_dataset(self):

        self.assertTrue(isinstance(dataset.DataSet(dataset_path = "roadmap_epigenomic.json"), dataset.DataSet))
        self.assertTrue(isinstance(dataset.DataSet(dataset_path = "".join([POST_HIT_PATH,"data/datasets/phyloP100way.json"])), dataset.DataSet))
        self.assertTrue(isinstance(dataset.DataSet(dataset_path ="ensembl"), dataset.DataSet))
        self.assertTrue(isinstance(dataset.DataSet(dataset_path = "gtex.json"), dataset.DataSet))

        self.assertRaises(ValueError, dataset.DataSet,"gtex.txt")
        self.assertRaises(ValueError, dataset.DataSet,"dummy")
        self.assertRaises(ValueError, dataset.DataSet,"dummy.json")

        self.dummy_dataset = dataset.DataSet(dataset_path = "dummy.json",
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

        self.assertTrue(isinstance(dummy_dataset, dataset.DataSet))
        self.assertTrue(os.path.exists("tmp/DummyTest.gtf.gz"), dataset.DataSet)

        


    def tearDown(self):
        """Finishes the test."""
        # Deleting the output directory
        self.output_dir.cleanup()

class TestAdapter(unittest.TestCase):

    def setUp(self):
         # Creating a temporary directory
        self.output_dir = TemporaryDirectory(prefix="post_hit_adapter_test_")
    
    def teset_adapter():
        pass

    def tearDown(self):
        """Finishes the test."""
        # Deleting the output directory
        self.output_dir.cleanup()
