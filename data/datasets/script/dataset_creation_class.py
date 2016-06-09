import sys
sys.path.append("/home/cedric/WASABI02/post_hit") 

from package.dataset import DataSet
import os

class CoreChromatinState(DataSet):
	"""docstring for CoreChromatinState"""
	def __init__(self,dataset_path, data_path):

		data_representation = {"representation" : "key-list",
								"fields":["name"],
								"key":"resource/id"}

		download_link_template = (
				"http://egg2.wustl.edu/roadmap/data/byFileType/"
				"chromhmmSegmentations/ChmmModels/coreMarks/"
				"jointModel/final/{}_15_coreMarks_dense.bb"
				)

		ids = ["E{0:03}".format(i) for i in range(1,130)]
		download_links = [download_link_template.format(i) for i in ids]
		filenames = [filename_template.format(i) for i in ids]

		kwarg = {
			"project":  "Roadmap epigenomics project",			
			"description": (
		    "A 15-state chromatin model that was generated using chromHMM "
		    "over different histone modifications from the 111 reference "
		    "epigenomes of the Roadmap Epigenomics project. A full "
		    "of the different states is available at "
		    "http://www.nature.com/nature/journal/v518/n7539/full/nature14248.html"
			),
			"project_link": "http://www.nature.com/nature/journal/v518/n7539/full/nature14248.html",
			"version": 1,
			"data_path": data_path,
			"protocole": "http",
			"file_type": "bb",
			"metadata": {},
			"ids": ids,
			"download_links":download_links,
			"filenames":filenames,
			"data_representation":data_representation
			}

		super(CoreChromatinState, self).__init__(dataset_path, **kwarg)

	

		
class ImputedChromatinState(DataSet):
	"""docstring for RoadmapEpigenomic_Dataset"""
	def __init__(self, dataset_path, data_path) :

		data_representation = {"representation" : "key-list",
								"fields":["name"],
								"key":"resource/id"}

		filename_template = "{}_25_imputed12marks_dense.bb"
		download_link_template = (
				"http://egg2.wustl.edu/roadmap/data/byFileType/"
				"chromhmmSegmentations/ChmmModels/imputed12marks/"
				"jointModel/final/{}_25_imputed12marks_dense.bb"
				)

		ids = ["E{0:03}".format(i) for i in range(1,130 )]
		download_links = [download_link_template.format("E001") + ".2"] + \
			[download_link_template.format(i) for i in ids if i != "E001"]
		filenames = [filename_template.format(i) for i in ids]

		kwarg = {
			"project":  "Roadmap epigenomics project",			
			"description": (
		    "A 25 state chromatin model generated from 12 histone marks on "
		    "127 epigenomes. This is from imputed data which means that "
		    "missing marks and values were guessed from other tissues and "
		    "marks. A full description is available at "
		    "http://egg2.wustl.edu/roadmap/web_portal/imputed.html"
			),
			"project_link": "http://egg2.wustl.edu/roadmap/web_portal/imputed.html",
			"version": 1,
			"data_path": data_path,
			"protocole": "http",
			"file_type": "bb",
			"metadata": {},
			"ids": ids,
			"download_links":download_links,
			"filenames":filenames,
			"data_representation":data_representation
			}

		super(ImputedChromatinState, self).__init__(dataset_path, **kwarg)



class PhyloP(DataSet):
	"""docstring for PhyloP"""
	def __init__(self, dataset_path, data_path):


		data_representation = {"representation" : "vector",
								"fields":["value"],
								}
		filenames = ["hg19.100way.phyloP100way.bw"]
		download_links = [
				("http://hgdownload.cse.ucsc.edu/goldenpath/hg19/"
					"phyloP100way/hg19.100way.phyloP100way.bw")]

		ids = ["phyloP100way"]

		kwarg = {
			"project":  "UCSC",			
			"description": (
		    "PhyloP is a tool that computes conservation or acceleration "
		    "p-values based on multiples sequence alignments and a model of "
		    "neutral evolution. The reported score is -log(p-value). Positive "
		    "values indicate conservation and negative values indicate "
		    "acceleration.\n"
		    "In this case, the results represent values from 100 way "
		    "alignements as computed by UCSC. A full description of the "
		    "integrated species is availables at "
		    "http://hgdownload.cse.ucsc.edu/goldenpath/hg19/phyloP100way/"
			),
			"project_link": "http://hgdownload.cse.ucsc.edu/goldenpath/hg19/phyloP100way/",
			"version": 1,
			"data_path": data_path,
			"protocole": "http",
			"file_type": "bw",
			"metadata": {},
			"ids": ids,
			"download_links":download_links,
			"filenames":filenames,
			"data_representation":data_representation
			}


		super(PhyloP, self).__init__(dataset_path, **kwarg)

class Ensembl(DataSet):
	"""docstring for Ensembl"""
	def __init__(self, dataset_path, data_path):
		
		data_representation = {"representation" : "key-list",
								"fields":["feature"],
								"key": "attribute/gene_name"
								}

		kwarg = {
			"project":  "Ensembl",			
			"description": (""
			),
			"project_link": "http://grch37.ensembl.org/Homo_sapiens/Info/Index",
			"version": 1,
			"data_path": data_path,
			"protocole": "ftp",
			"file_type": "gtf",
			"metadata": {},
			"ids": ["Homo_sapiens.GRCh37.75"],
			"download_links":["ftp://ftp.ensembl.org/pub/release-75//gtf/homo_sapiens/Homo_sapiens.GRCh37.75.gtf.gz"],
			"filenames":["Homo_sapiens.GRCh37.75.gtf.gz"],
			"data_representation":data_representation
			}




		super(Ensembl, self).__init__(dataset_path, **kwarg)

class GTEx(DataSet):
	"""docstring for GTEx"""
	def __init__(self, dataset_path, data_path):

		data_representation = {"representation" : "key-list",
								"fields":["rs_id_dbSNP142_GRCh37p13"],
								"start":"snp_pos",
								"end":"snp_pos",
								"chrom":"snp_chrom",
								"key":"gene_name"
								}

		filenames = [filename for filename in os.listdir(data_path) if filename != "GTEx_Analysis_V6_eQTLs.tar.gz"]
		ids = [os.path.basename(filename) for filename in filenames]
		download_link = "http://www.gtexportal.org/static/datasets/gtex_analysis_v6/single_tissue_eqtl_data/GTEx_Analysis_V6_eQTLs.tar.gz"
		
		kwarg = {
			"project":  "The Genotype-Tissue Expression project",			
			"description": (""
			),
			"project_link": "http://grch37.ensembl.org/Homo_sapiens/Info/Index",
			"version": 1,
			"data_path": data_path,
			"protocole": "http",
			"file_type": "tsv",
			"metadata": {},
			"download_links":[download_link for i in range(len(filenames))],
			"filenames":filenames,
			"ids":ids,
			"data_representation":data_representation
			}

		super(GTEx, self).__init__(dataset_path, **kwarg)

def main():
	
	print("ImputedChromatinState")
	ImputedChromatinState("/home/cedric/WASABI02/post_hit/data/datasets/roadmap_epigenomic.json", "/home/cedric/WASABI02/post_hit/data/roadmap_epigenomic/").create()
	print("PhyloP")
	PhyloP("/home/cedric/WASABI02/post_hit/data/datasets/phyloP100way.json", "/home/cedric/WASABI02/post_hit/data/phyloP100way/").create()
	print("Ensembl")
	Ensembl("/home/cedric/WASABI02/post_hit/data/datasets/ensembl.json", "/home/cedric/WASABI02/post_hit/data/ensembl/").create()
	print("GTEx")
	GTEx("/home/cedric/WASABI02/post_hit/data/datasets/gtex.json", "/home/cedric/WASABI02/post_hit/data/gtex/").create()

if __name__ == '__main__':
	main()