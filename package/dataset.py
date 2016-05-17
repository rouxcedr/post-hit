import json
import requests
import urllib.request
from . import Adaptaters
import sys
import os.path

class DataSet(object):
	"""Creates the appropriate dataset"""
	def __init__(self):

		super(DataSet, self).__init__()

	def get_json_skeletton(self, skeletton_path):
		
		self.project = ""
		self.description = ""

		self.project_link = ""
		self.version = ""
		self.data_path = ""
		self.metadata_path = ""
		self.filename_template = ""
		self.download_link_template = ""

		self.protocole = ""
		self.file_type = ""

		self.ids = [""]
		self.download_links = [""]
		self.filenames = [""]

		self.dataset_path = skeletton_path

		self.create()

	def create(self):

		"""Creates a JSON database

		Args : 
			dataset_path : The path to the json file that will be used to store data (str)

		"""

		if len(self.filenames) != len(self.download_links):
			print("Must have the same amount off file names than download links", file=sys.stderr)
			return None

		resources = []

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
			    "metadata_path": self.metadata_path,
			    "files_type":self.file_type,
			    "protocole":self.protocole,
			    "resources":resources
			  }
			}
		with open(self.dataset_path, "w") as json_file:
			json_file.write(json.dumps(data))


	def load(self, user_dataset_path = None, dataset_name = None):
		
		if dataset_name is not None and user_dataset_path is not None :
			if "data/datasets/{}".format(dataset_name) == user_dataset_path:

				self.dataset_path = user_dataset_path

			else: 

				if os.path.exists(user_dataset_path):
					self.dataset_path = "data/datasets/{}".format(dataset_name)
					with open(user_dataset_path) as user_json:
						dataset = json.load(user_json)
					with open(self.dataset_path) as json_file:
						json_file.write(json.dumps(dataset))
				else :
					raise ValueError("This path doesn't exist")

		elif dataset_name is not None and user_dataset_path is None:
			if os.path.exists("data/datasets/{}".format(dataset_name)):
				self.dataset_path = "data/datasets/{}".format(dataset_name)

			else :
				raise ValueError("This DataSet name doesn't exist in our bank")

		elif user_dataset_path is not None and dataset_name is None:

			if os.path.exists(user_dataset_path) : 
				dataset_name = os.path.basename(user_dataset_path)
				self.dataset_path = "data/datasets/{}".format(dataset_name)
				with open(user_dataset_path) as user_json:
					dataset = json.load(user_json)
				with open(self.dataset_path) as json_file:
					json_file.write(json.dumps(dataset))
			else :
				raise ValueError("This path doesn't exist")
		else:
			raise ValueError("Please give the DataSet path or name")

		


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
				data = Adaptaters.BigBedAdaptater(self.dataset_path).get_region(region)

			if dataset["dataset"]["files_type"] == "bw":
				data = Adaptaters.BigWigAdaptater(self.dataset_path).get_region(region)

			if dataset["dataset"]["files_type"] == "gtf":
				data = Adaptaters.GTFAdaptater(self.dataset_path).get_region(region)

		return data
	
