import unittest
import os
from tempfile import TemporaryDirectory
from package import dataset, Adapter
import pandas as pd
import numpy as np

class TestDataSet(unittest.TestCase):

    def setUp(self):
         # Creating a temporary directory
        self.output_dir = TemporaryDirectory(prefix="post_hit_dataset_test_")

        self.dataset = dataset.DataSet()

    def tearDown(self):
        """Finishes the test."""
        # Deleting the output directory
        self.output_dir.cleanup()
