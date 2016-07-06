#Fill out all the information needed to create the dataset (fields that are in caps)
#To name the dataset use "find and replace" if your editor has it (ctrl-h) and replace DATASET_NAME with the name

import sys
sys.path.append("/home/cedric/WASABI02/post_hit") 

from post_hit.dataset import DataSet
import os

class DATASET_NAME(DataSet):
    """docstring for GTEx"""
    def __init__(self, dataset_path, data_path):

        data_representation = {"representation" : "KEY-LIST OR VECTOR (REQUIRED)",
                                "key": "KEY LOCATION (REQUIRED ONLY FOR KEY-LIST)",
                                "fields": ["FIELDS (REQUIRED)"],
                                "start": "START POSITION COLUMN NAME (REQUIRED ONLY FOR CSV/TSV)",
                                "end": "START POSITION COLUMN NAME (REQUIRED ONLY FOR CSV/TSV)",
                                "chrom": "START POSITION COLUMN NAME (REQUIRED ONLY FOR CSV/TSV)",
                                }

        ids = ["LIST OF IDS (Using a list comprehension is recommended)"]
        filenames = ["LIST OF FILENAMES (Using a list comprehension is recommended)"]
        download_links = ["LIST OF FILENAMES (Using a list comprehension is recommended)"]


        metadata = ["LIST OF DICT CONTAINING THE METADATA FOR THE EVERY IDS/FILES (Using a list comprehension is recommended)"]
        
        kwarg = {
            "project":  "PROJECT'S NAME(RECOMMENDED)",           
            "description": "PROJECT'S DESCRIPTION (RECOMMENDED)",
            "project_link": "PROJECT'S HOMEPAGE LINK (RECOMMENDED)",
            "version": 1, #(RECOMMENDED)
            "data_path": data_path,
            "protocole": "DOWNLOAD PROTOCOL (REQUIRED)",
            "file_type": "FILE TYPE (REQUIRED)",
            "metadata": metadata,
            "download_links": download_links,
            "filenames":filenames,
            "ids":ids,
            "data_representation":data_representation
            }

        super(DATASET_NAME, self).__init__(dataset_path, **kwarg)

def main():

    dataset_path = os.path.dirname(__file__) + "/../DATASET_NAME.json"
    data_path = os.path.dirname(__file__) + "/../../DATASET_NAME/"

    
    DATASET_NAME(dataset_path, data_path).create()

if __name__ == '__main__':
    main()