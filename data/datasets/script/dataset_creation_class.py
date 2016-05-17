from /post_hit/package/ import dataset


class CoreChromatinState(DataSet):
	"""docstring for CoreChromatinState"""
	def __init__(self, data_path= None, metadata_path=None, dataset_path = None, version = None, epigenome_nbr = 129):

		# Required fields.
		self.project = "Roadmap epigenomics project"
		self.description = (
		    "A 15-state chromatin model that was generated using chromHMM "
		    "over different histone modifications from the 111 reference "
		    "epigenomes of the Roadmap Epigenomics project. A full "
		    "of the different states is available at "
		    "http://www.nature.com/nature/journal/v518/n7539/full/nature14248.html"
		)

		self.project_link = "http://www.nature.com/nature/journal/v518/n7539/full/nature14248.html"

		self.version = version
		self.dataset_path = dataset_path
		self.data_path = data_path
		self.metadata_path = metadata_path
		self.filename_template = "{}_15_coreMarks_dense.bb"
		self.download_link_template = (
				"http://egg2.wustl.edu/roadmap/data/byFileType/"
				"chromhmmSegmentations/ChmmModels/coreMarks/"
				"jointModel/final/{}_15_coreMarks_dense.bb"
				)

		self.protocole = "http"
		self.file_type = "bb"

		self.ids = ["E{0:03}".format(i) for i in range(epigenome_nbr + 1 )]
		self.download_links = [self.download_link_template.format(i) for i in self.ids]
		self.file_names = [self.filename_template.format(i) for i in self.ids]

		super(CoreChromatinState, self).__init__()

	

		
class ImputedChromatinState(DataSet):
	"""docstring for RoadmapEpigenomic_Dataset"""
	def __init__(self, data_path= None, metadata_path=None, dataset_path = None, version = None, epigenome_nbr = 129):

		self.project = "Roadmap epigenomics project"
		self.description = (
		    "A 25 state chromatin model generated from 12 histone marks on "
		    "127 epigenomes. This is from imputed data which means that "
		    "missing marks and values were guessed from other tissues and "
		    "marks. A full description is available at "
		    "http://egg2.wustl.edu/roadmap/web_portal/imputed.html"
		)

		self.project_link = "http://egg2.wustl.edu/roadmap/web_portal/imputed.html"
		self.version = version

		self.data_path = data_path
		self.dataset_path = dataset_path
		self.metadata_path = metadata_path
		self.filename_template = "{}_25_imputed12marks_dense.bb"
		self.download_link_template = (
				"http://egg2.wustl.edu/roadmap/data/byFileType/"
				"chromhmmSegmentations/ChmmModels/imputed12marks/"
				"jointModel/final/{}_25_imputed12marks_dense.bb"
				)
		self.protocole = "http"
		self.file_type = "bb"

		self.ids = ["E{0:03}".format(i) for i in range(1,epigenome_nbr + 1 )]
		self.download_links = [self.download_link_template.format("E001") + ".2"] + \
			[self.download_link_template.format(i) for i in self.ids if i != "E001"]
		self.filenames = [self.filename_template.format(i) for i in self.ids]
		super(ImputedChromatinState, self).__init__()


class PhyloP(DataSet):
	"""docstring for PhyloP"""
	def __init__(self, data_path=None, dataset_path = None, version = None):

		self.project = "UCSC"
		self.description = (
		    "PhyloP is a tool that computes conservation or acceleration "
		    "p-values based on multiples sequence alignments and a model of "
		    "neutral evolution. The reported score is -log(p-value). Positive "
		    "values indicate conservation and negative values indicate "
		    "acceleration.\n"
		    "In this case, the results represent values from 100 way "
		    "alignements as computed by UCSC. A full description of the "
		    "integrated species is availables at "
		    "http://hgdownload.cse.ucsc.edu/goldenpath/hg19/phyloP100way/"
		)

		self.project_link = "http://hgdownload.cse.ucsc.edu/goldenpath/hg19/phyloP100way/"
		self.version = version
		self.metadata_path = None
		self.dataset_path = dataset_path

		self.protocole = "http"
		self.file_type = "bw"

		self.data_path = data_path
		self.filenames = ["hg19.100way.phyloP100way.bw"]
		self.download_links = [
				("http://hgdownload.cse.ucsc.edu/goldenpath/hg19/"
					"phyloP100way/hg19.100way.phyloP100way.bw")]

		self.ids = ["phyloP100way"]




		super(PhyloP, self).__init__()

class Ensembl(DataSet):
	"""docstring for Ensembl"""
	def __init__(self, data_path=None, dataset_path = None, version = None):

		self.project = "Ensembl"
		self.description = (
		    ""
		)

		self.project_link = "http://grch37.ensembl.org/Homo_sapiens/Info/Index"
		self.version = version
		self.metadata_path = None
		self.dataset_path = dataset_path

		self.protocole = "ftp"
		self.file_type = "gtf"

		self.data_path = data_path
		self.filenames = ["Homo_sapiens.GRCh37.75.gtf.gz"]
		self.download_links = [
				("ftp://ftp.ensembl.org/pub/release-75//gtf/homo_sapiens/Homo_sapiens.GRCh37.75.gtf.gz")]

		self.ids = ["Homo_sapiens.GRCh37.75"]




		super(Ensembl, self).__init__()