import json
import sys
import os.path
from pprint import pprint
import requests

def main():

	database_path = "data/database.json"

	download_links = ["http://hgdownload.cse.ucsc.edu/goldenpath/hg19/phyloP100way/hg19.100way.phyloP100way/hg19.100way.phyloP100way.bw"]
	file_names = ["hg19.100way.phyloP100way.bw"]
	name = "phyloP100way"
	path = "data/phyloP100way/"
	#database_path = "data/roadmap_epigenomic/database.json"
	file_type = "bw"
	protocole = "http"
	database_creator(database_path,name, path, protocole, file_type, download_links, file_names)
	#database_downloader(database_path)

	download_link = "http://egg2.wustl.edu/roadmap/data/byFileType/chromhmmSegmentations/ChmmModels/imputed12marks/jointModel/final/E{}_25_imputed12marks_dense.bb"
	epigenome_nbr = ["{0:03}".format(i) for i in range(1,130)]
	download_links = [download_link.format(i) for i in epigenome_nbr]
	file_name = "E{}_25_imputed12marks_dense.bb"
	file_names = [file_name.format(i) for i in epigenome_nbr]
	name = "Roadmap Epigenomic"
	path = "data/roadmap_epigenomic/"
	#database_path = "data/roadmap_epigenomic/database.json"
	file_type = "bb"
	protocole = "http"
	database_creator(database_path,name, path, protocole, file_type, download_links, file_names)
	#database_downloader(database_path)



# def database_creator(database_path,dataset_name, path, protocole, file_type, download_links, 
# 	file_names):

# 	"""Creates a JSON database

# 		Args : 
# 			database_path : The path to the json file that will be used to store data (str)
# 			dataset_name : The name of the dataset that is going to be added to the database (str)
# 			path : Path to the folder where the data is going to be stored (str)
# 			protocole : Protocole for downloading the data ("http", "ftp", "scp", etc...) (str)
# 			file_type : Type of files added to the dataset (str)
# 			download_links : Links to download the files (list)
# 			file_names : Name of the files (list)

# 	"""

# 	data = {"dataset":{"name":dataset_name,"path":path,"ressources":
# 				{"type":file_type,"protocole":protocole,"download_links":
# 					{file_names[i]:download_links[i] for i in range (len(file_names))}
# 				}}}

# 	if len(file_names) != len(download_links):
# 		print("Must have the same amount off file names than download links", file=sys.stderr)
# 		return None

# 	if not os.path.isfile(database_path):
# 		with open(database_path, "w") as json_file:
# 			json_file.write(json.dumps([data]))
# 	else:
# 		with open(database_path) as json_file:
# 			feed = json.load(json_file)
# 		feed.append(data)
# 		with open(database_path, "w") as json_file:
# 			json_file.write(json.dumps(feed))		



# def database_downloader(database_path, dataset_names = None):
# 	"""Downloads files in the database

# 		Args : 
# 			database_path : Path to the JSON database file
# 			dataset_names = List of the dataset names to be downloaded

# 	"""
	 
# 	with open(database_path) as data_file:
# 	 	data = json.load(data_file)

# 	 	for dataset in data:

# 	 		if dataset_names is None or dataset["dataset"]["name"] in dataset_names :
# 			 	path = dataset["dataset"]["path"]

# 			 	protocole =  dataset["dataset"]["ressources"]["protocole"]
# 			 	file_type =  dataset["dataset"]["ressources"]["type"]

# 			 	for file_name, download_link in dataset["dataset"]["ressources"]["download_links"].items():
# 			 		print("DOWNLOADING : {}".format(file_name))
# 			 		query = requests.get(download_link)
# 			 		with open("".join([path, file_name]), "wb") as donwload_file:
# 			 			donwload_file.write(query.content)
	

if __name__ == '__main__':
	main()
