#!/usr/bin/env python
import json
import requests
import urllib.request
try:
    from . import adapters
except SystemError:
    import adapters
    
import sys
import os.path
import tarfile
from gepyto.db import index
import subprocess

POST_HIT_PATH = os.path.dirname(__file__) + "/"

class DataSet(object):

    """Manages the JSON datasets provided by the user.
    
        :param dataset_path: The path to the dataset, can be the filename 
                             if the dataset is already locally stored.
        :type dataset_path: str

        OPTIONAL PARAMETERS (All the information needed to create a JSON Dataset file)

        :param project: The project's name.
        :type project: str

        :param description: The project's description.
        :type description: str

        :param version: The version of the dataset.
        :type version: int

        :param data_path: The path to the data files.
        :type data_path: str

        :param protocole: The protocole to download the files (http or ftp)
        :type protocole: str

        :param file_type: The type of the data files
        :type file_type: str

        :param metadata: A dictionnary in wich the metadas are described (JSON/JSON-LD).
        :type metadata: dict

        :param ids: The list of the IDS for each files. (The filename without the extension for example)
                    (Must be in the same order than the download links and filenames)
        :type ids: tuple

        :param download_links: List of the download links for the files 
                                (Must be in the same order than the ids and filenames)
        :type download_links: tuple

        :param filenames: List of the filenames.
                          (Must be in the same order than the ids and download links)
        :type filenames: tuple

        :param data_representation: A dictionnary in wich the data representation is described (JSON/JSON-LD).
        :type data_representation: dict
        
        """
    
    def __init__(self, dataset_path, **kwargs):

        _OPTIONAL_PARAMETERS = {
        "project": str,
        "description": str,
        "project_link": str,
        "version": int,
        "data_path": str,
        "protocole": str,
        "file_type": str,
        "metadata": tuple,
        "ids": tuple,
        "download_links":tuple,
        "filenames":tuple,
        "data_representation":dict
        }

        self.dataset_path = dataset_path

        # Store the passed parameters.
        argument_passed = False
        for arg, val in kwargs.items():
            if arg not in _OPTIONAL_PARAMETERS:
                raise Exception("Unknown parameter {}.".format(arg))
            try:
                setattr(self, arg, _OPTIONAL_PARAMETERS[arg](val))
            except TypeError:
                raise TypeError("Invalid type for argument {}. Expected "
                    "a {}.".format(arg, _OPTIONAL_PARAMETERS[arg]))
            argument_passed = True

        if argument_passed:
            self.create()
            try:
                self.load()
            except Exception as e:
                pass
            
        else:
            self.load()


        super(DataSet, self).__init__()

    def create(self):

        """

        Creates a JSON dataset file with the information available. The class optionnal parameters needs to be passed as arguments when creating the dataset class.

        """

        if len(self.filenames) != len(self.download_links):
            print("Must have the same amount off file names than download links", file=sys.stderr)
            return None

        resources = []

        #Creating the resource dict
        for i in range(len(self.filenames)):
            resources.append(
                {
                    "id": self.ids[i],
                    "description":"",
                    "filename":self.filenames[i],
                    "download_link":self.download_links[i]
                  }
                )


        #The JSON
        data = {
              "dataset":{
                "project":self.project,
                "version":self.version,
                "description":self.description,
                "project_link":self.project_link,
                "data_path": self.data_path,
                "metadata": self.metadata,
                "files_type":self.file_type,
                "protocole":self.protocole,
                "resources":resources,
                "data_representation":self.data_representation
              }
            }
        with open(self.dataset_path, "w") as json_file:
            json_file.write(json.dumps(data))


    def load(self):

        """
            Loads the dataset : 

                - If the JSON file does not not exist locally it creates a local copy of the JSON file. And then sets the dataset_path to the local copy of the JSON dataset.
                
                - Sets the dataset_path to the absolute path if only the name of an already existing JSON file is passed as the argument

                - And finaly calls the proper adapter depending on the file type described in the JSON file.
        """
        
        if os.path.splitext(self.dataset_path)[1] == "":
            self.dataset_path = "".join([self.dataset_path, ".json"])

        if os.path.splitext(self.dataset_path)[1] != ".json":
            raise ValueError("File must be a JSON file")
        if os.path.exists(self.dataset_path):
            if os.path.basename(self.dataset_path) != "":
                dataset_name = os.path.basename(self.dataset_path)
                with open(self.dataset_path) as user_json:
                    dataset = json.load(user_json)
                self.dataset_path = "".join([POST_HIT_PATH,"/data/datasets/",  dataset_name])
                with open(self.dataset_path, "w") as json_file:
                    json_file.write(json.dumps(dataset))
            else:
                raise ValueError("The dataset path has no filename")

        #If only the JSON filename is given we check if this filename exist in our database

        elif os.path.exists("".join([POST_HIT_PATH, "/data/datasets/", self.dataset_path])):
            self.dataset_path = "".join([POST_HIT_PATH, "/data/datasets/", self.dataset_path])
        else:
            raise ValueError("The dataset path or name given is not valid")

        #Call the proper adapter

        with open(self.dataset_path) as dataset_file:
            dataset = json.load(dataset_file)

            for resource in dataset["dataset"]["resources"]:
                if not os.path.exists("".join([POST_HIT_PATH, dataset["dataset"]["data_path"],
                                                    resource["filename"]])):
                    self.download()

            if dataset["dataset"]["files_type"] == "bb":
                self.adapter = adapters.BigBedAdapter(self.dataset_path)

            if dataset["dataset"]["files_type"] == "bw":
                self.adapter = adapters.BigWigAdapter(self.dataset_path)

            if dataset["dataset"]["files_type"] == "gtf":
                self.adapter = adapters.GTFAdapter(self.dataset_path)

            if dataset["dataset"]["files_type"] == "csv":
                self.adapter = adapters.XsvAdapter(self.dataset_path, ",")
            if dataset["dataset"]["files_type"] == "tsv":
                self.adapter = adapters.XsvAdapter(self.dataset_path, "\t")


        


    def download(self):

        """
            Download the files from the dataset and, if needed, extract them from a .tar compressed archive.
        """

        with open(self.dataset_path) as dataset_file:
            dataset = json.load(dataset_file)

            path = "".join([POST_HIT_PATH, dataset["dataset"]["data_path"]])
            if not os.path.exists(path):
                os.makedirs(path)

            protocole =  dataset["dataset"]["protocole"]

            download_links = []

            for resource in dataset["dataset"]["resources"]:
                file_path = "".join([path, resource["filename"]])

                #Check if the the download link has not been used before (One download link for all)
                if resource["download_link"] not in download_links:
                    
                    print("DOWNLOADING : {}".format(resource["filename"]))
                    f = urllib.request.urlopen(resource["download_link"])
                    data = f.read()
                    with open(file_path, "wb") as donwload_file:
                        donwload_file.write(data)

                    download_links.append(resource["download_link"])

                            
                    #Extract all files from the tar archives if necessary
                    if tarfile.is_tarfile(file_path):
                        tf = tarfile.open(file_path)
                        tf.exractall()

    def get_region(self, region):

        """
            Calls the get_region function of the adapter.

            :param region: The region where the data is to be extracted.
            :type region: gepyto.structures.region.Region
        """

        return self.adapter.get_region(region)    




        #file_compression = ""
                    # magic_dict = {
                    # b"\x1f\x8b\x08": "gz",
                    # b"\x42\x5a\x68": "bz2",
                    # b"\x50\x4b\x03\x04": "zip"
                    # }
                    # 

                    # max_len = max(len(x) for x in magic_dict)
                    # with open(file_path, "rb") as f:
                    #     file_start = f.read(max_len)
                    # for magic, filetype in magic_dict.items():
                    #     if file_start.startswith(magic):
                    #         file_compression = filetype
                    # split_ext = file_path.split(".")
                    # extension = split_ext[len(split_ext) -1]
                    # if(file_compression == "zip"):
                    #     if extension != "zip":
                    #         subprocess.call("mv {} {}.zip".format(file_path, file_path).split())
                    #     subprocess.call("unzip {} -d .".format(file_path).split())
                    # if(file_compression == "bz2"):
                    #     if extension != "bz2":
                    #         subprocess.call("mv {} {}.bz2".format(file_path,file_path).split())
                    #     subprocess.call("bzip2 -df {}".format(file_path).split())
                    # if(file_compression == "gz"):
                    #     if extension != "gz":
                    #         subprocess.call("mv {} {}.gz".format(file_path,file_path).split())
                    #     subprocess.call("gzip -df {}".format(file_path).split())