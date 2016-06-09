import json
import requests
import urllib.request
from . import Adapters
import sys
import os.path

class DataSet(object):
	"""Creates the appropriate dataset"""
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
			self.load()
		else:
			self.load()


		super(DataSet, self).__init__()


	def get_json_skeletton( self ):

		skeletton_dataset = DataSet(dataset_path = self.dataset_path,
									project= "",
						            description= "",
						            project_link= "",
						            version= 0,
						            data_path= "",
						            filename_template= "",
						            protocole= "",
						            file_type= "",
						            ids=[],
						            download_links=[],
						            filenames=[],
						            metadata= [])


		skeletton_dataset.create()

	def create(self):

		"""Creates a JSON database

		Args : 
			dataset_path : The path to the json file that will be used to store data (str)

		"""

		if len(self.filenames) != len(self.download_links):
			print("Must have the same amount off file names than download links", file=sys.stderr)
			return None

		resources = []

		if len(self.filenames) == 0:
			resources.append(
				{
			        "id": self.ids,
			        "description":"",
			        "filename":self.filenames,
			        "download_link":self.download_links
			      }
				)

		for i in range(len(self.filenames)):
			resources.append(
				{
			        "id": self.ids[i],
			        "description":"",
			        "filename":self.filenames[i],
			        "download_link":self.download_links[i]
			      }
				)


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
		if os.path.exists(self.dataset_path):
			
			if os.path.basename(self.dataset_path) != "":
				dataset_name = os.path.basename(self.dataset_path)
				with open(self.dataset_path) as user_json:
					dataset = json.load(user_json)
				self.dataset_path = "/home/cedric/WASABI02/post_hit/data/datasets/{}".format(dataset_name)
				with open(self.dataset_path, "w") as json_file:
					json_file.write(json.dumps(dataset))
			else :
				raise ValueError("This path has no filename")

		elif os.path.exists("/home/cedric/WASABI02/post_hit/data/datasets/{}".format(self.dataset_path)):
			self.dataset_path = "/home/cedric/WASABI02/post_hit/data/datasets/{}".format(self.dataset_path)
		else:
			raise ValueError("The dataset path or name given is not valid")

		


	def download(self):

		with open(self.dataset_path) as dataset_file:
			dataset = json.load(dataset_file)

			path = dataset["dataset"]["data_path"]
			if not os.path.exists(path):
				os.makedirs(path)

			protocole =  dataset["dataset"]["protocole"]

			for resource in dataset["dataset"]["resources"]:
				print("DOWNLOADING : {}".format(resource["filename"]))
				f = urllib.request.urlopen(resource["download_link"])
				data = f.read()
				with open("".join([path, resource["filename"]]), "wb") as donwload_file:
				    donwload_file.write(data)

	def get_region(self, region):
		
		with open(self.dataset_path) as dataset_file:
			dataset = json.load(dataset_file)
			if dataset["dataset"]["files_type"] == "bb":
				data = Adapters.BigBedAdapter(self.dataset_path).get_region(region)

			if dataset["dataset"]["files_type"] == "bw":
				data = Adapters.BigWigAdapter(self.dataset_path).get_region(region)

			if dataset["dataset"]["files_type"] == "gtf":
				data = Adapters.GTFAdapter(self.dataset_path).get_region(region)

			if dataset["dataset"]["files_type"] in ("csv", "tsv"):
				data = Adapters.XsvAdapter(self.dataset_path).get_region(region)

		return data
	
