from package import dataset
from gepyto.structures.region import Region
from pprint import pprint

def main():
	
	#dataset.DataSet().get_json_skeletton("data/datasets/skeletton.json")

	roadmap_epigenomic_dataset = dataset.DataSet()
	roadmap_epigenomic_dataset.load(dataset_name = "roadmap_epigenomic_dataset_v1.json")
	roadmap_epigenomic_dataset.download()

	phyloP100way_dataset = dataset.DataSet()
	phyloP100way_dataset.load(dataset_name = "phyloP100way_dataset_v1.json")

	ensembl_dataset = dataset.DataSet()
	ensembl_dataset.load(dataset_name = "ensembl_dataset_v1.json")

	r = Region("19", 45819671, 45826235)

	pprint(roadmap_epigenomic_dataset.get_region(r))

	#pprint(phyloP100way_dataset.get_region(r))

	#pprint(ensembl_dataset.get_region(r))




if __name__ == '__main__':
	main()