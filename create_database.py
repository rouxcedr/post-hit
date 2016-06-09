from package import dataset
from gepyto.structures.region import Region
from pprint import pprint

def main():
	
	#dataset.DataSet(dataset_path = "data/datasets/skeletton.json").get_json_skeletton()

	roadmap_epigenomic_dataset = dataset.DataSet(dataset_path = "roadmap_epigenomic.json")

	phyloP100way_dataset = dataset.DataSet(dataset_path = "data/datasets/phyloP100way.json")

	ensembl_dataset = dataset.DataSet(dataset_path ="ensembl.json")

	gtex_dataset = dataset.DataSet(dataset_path = "gtex.json")

	r = Region("19", 45719671, 45826235)

	#pprint(roadmap_epigenomic_dataset.get_region(r))

	#pprint(phyloP100way_dataset.get_region(r))

	#pprint(ensembl_dataset.get_region(r))

	pprint(gtex_dataset.get_region(r))




if __name__ == '__main__':
	main()