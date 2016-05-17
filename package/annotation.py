from __future__ import division

"""
Extract information from multiple databases for a given region.

This is useful for continuous epigenomic and conservation signals.

TODO list:

Easy
    [x] phyloP (from UCSC) (via downloaded copy)
    [] genes, transcripts, exons, UTRs (from Ensembl via gepyto)
    [] GWAS Catalog (UCSC, or download)
    [] Clinvar variants (UCSC)

Not so easy
    [x] Roadmap chromatin 15-state model
    [x] Roadmap imputed chromatin
    [] Seems like there is RNASeq data in ENCODE for different tissues
    [] Beerlab tool (http://www.nature.com/ng/journal/v47/n8/full/ng.3331.html)
    [] Sift and PolyPhen
    [] CADD
    [] Protein domains (from genomic coordinates)

"""


import os
import collections
import logging
logger = logging.getLogger(__name__)
from pprint import pprint
from collections import Counter
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle

import pandas as pd
import numpy as np
from gepyto.formats.wig import WiggleFile
from gepyto.db import ensembl 



try:
    from bokeh.plotting import figure, show, output_file
except ImportError:
    pass

from . import tools


class InvalidInstallation(Exception):
    pass


class GenericAnnotation(object):
    def __init__(self):
        """Initialize an annotation.

        The following properties are expected:

            - project: The data generating project.
            - description: A description of the annotation that is human
                           readable and sufficient for data interpretation.
            - version: The database version.

        """
        try:
            self.validate_installation()
        except Exception as e:
            raise InvalidInstallation(*e.args)

    def extract_region(self, region):
        """Get the results for a given region."""
        raise NotImplementedError()

    def validate_installation(self):
        """Validate that the provided directory structure is as expected."""
        raise NotImplementedError()


class Ensembl(GenericAnnotation):
    """docstring for Ensembl"""
    def __init__(self):
        self.project = "Ensembl"
        self.description = ("INSERT DESCRIPTION")

        self.version = None

        self.genes, self.transcript_df, self.cds_df, self.exon_df = (None,)*4

        super(Ensembl, self).__init__()
    
    def extract_region(self, region):
         

         # The URL and options
        url = "http://rest.ensembl.org/overlap/region/{species}/{region}"
        opt = ["feature=gene","feature=transcript","feature=cds","feature=exon","content-type=application/json"]
        

        # Constructing the final URL
        query_url = "{}?{}".format(url, ";".join(opt)).format(species="homo_sapiens",
                                                              region="{chr}:{start}-{end}".format(
                                                                chr=region.chrom, start=region.start, end=region.end
                                                                ))

        results = ensembl.query_ensembl(query_url)
        
        gene_data = []
        transcript_data = []
        cds_data = []
        exon_data = []

        for result in results:
            if result["feature_type"]  == "gene":
                gene_data.append(
                    (result["external_name"],result["gene_id"], result["start"], result["end"])
                    )
            if result["feature_type"]  == "transcript":
                transcript_data.append(
                    (result["external_name"],result["transcript_id"], result["start"], result["end"], result["biotype"])
                    )

            if result["feature_type"]  == "cds":
                cds_data.append(
                    (result["protein_id"], result["start"], result["end"])
                    )

            if result["feature_type"]  == "exon":
                exon_data.append(
                    (result["exon_id"], result["start"], result["end"])
                    )

        self.genes = pd.DataFrame(
            gene_data,
            columns = ["gene_name","gene_id","start","end"]
            )
        self.transcript_df = pd.DataFrame(
            transcript_data,
            columns = ["transcript_name","transcript_id","start","end","biotype"]
            )
        self.cds_df = pd.DataFrame(
            cds_data,
            columns = ["protein_id","start","end"]
            )
        self.exon_df = pd.DataFrame(
            exon_data,
            columns = ["exon_id","start","end"]
            )
        

    def plot_region(self, region):
        
        self.extract_region(region)

        fig = plt.figure(figsize = (80,60))

        renderer = fig.canvas.get_renderer()

        # The last bbox
        last_t_obj = {}
        last_end = defaultdict(int)

        up_down = 1
        for i in range(self.genes.shape[0]):
            gene_start = self.genes.iloc[i, :].start
            gene_end = self.genes.iloc[i, :].end
            gene_name = self.genes.iloc[i, :].gene_name

            # # Checking the starting position of the gene
            # if gene_start < start:
            #     gene_start = start
            gene_start /= 1e6

            # # Checking the ending position of the gene
            # if gene_end > end:
            #     gene_end = end
            gene_end /= 1e6

            # Updating the gene label
            gene_label = gene_name
            # if genes.iloc[i, :].strand == 1:
            #     gene_label = gene_name + r"$\rightarrow$"
            # else:
            #     gene_label = r"$\leftarrow$" + gene_name

            # We find the first j where we can put the line
            j = 0
            while True:
                if last_end[j] < gene_start:
                    break
                j -= 1

            # Trying to put the label there
            t = plt.text((gene_start + gene_end) / 2, j - 0.15*up_down, gene_label,
                              fontsize=6, ha="center", va="top")
            up_down = - up_down

            # Is there a bbox in this location?
            if j in last_t_obj:
                # Getting the bbox
                bb = t.get_window_extent(renderer=renderer)
                last_bb = last_t_obj[j].get_window_extent(renderer=renderer)

                while last_bb.overlaps(bb):
                    # BBoxes overlap
                    logging.debug("{} overlaps".format(gene_name))
                    j -= 1
                    t.set_y(j - 0.15)

                    # Last j?
                    if j not in last_t_obj:
                        break

                    # Need to update both bboxes
                    bb = t.get_window_extent(renderer=renderer)
                    last_bb = last_t_obj[j].get_window_extent(renderer=renderer)

            # Plotting the line
            logging.debug("Putting {} at position {}".format(gene_name, j))
            marker = "-"
            other_param = {}
            if (gene_end - gene_start) < 3e-3:
                # Too small
                marker = "s"
                other_param["ms"] = 1.8
            plt.plot([gene_start, gene_end], [j, j], marker, lw=2,
                          color="#000000", clip_on=False, **other_param)

            # Saving the last position (last end and bbox)
            last_end[j] = gene_end + 3e-3
            last_t_obj[j] = t


        # for idx, row in self.gene_df.iterrows():

        #     plt.plot((row.start + 1, row.end +1),(idx*2+1,idx*2+1), linewidth = 3, color = "black")
        #     plt.text((row.start + row.end) / 2, idx*2+1 - 0.15, row.gene_name,
        #                   fontsize=15, ha="center", va="top")
        axes = plt.gca()
        axes.set_ylim([-3,3])
        plt.show()





    def validate_installation(self):
        """Validate that the provided directory structure is as expected."""
        pass

class PhyloP100Way(GenericAnnotation):
    def __init__(self, data_path=None):
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
        self.version = None

        self.data_path = data_path

        super(PhyloP100Way, self).__init__()

    def extract_region(self, region):
        big_wig_to_wig = tools.BigWigToWig()
        wig = big_wig_to_wig.call(
            self.filename, chrom=("chr" + region.chrom),
            start=(region.start - 1), end=region.end
        )
        with WiggleFile(wig) as f:
            data = f.as_dataframe()

        return data

    def plot_region(self, region, smooth=0):
    
        data = self.extract_region(region)

        if smooth:
            data["value"] = np.convolve(
                data["value"].values,
                np.ones(smooth) / smooth,
                "same"
            )

        plt.figure(figsize=(50,50))

        plt.plot(
                data["pos"],
                data["value"],
                "b-"
            )

        plt.xlabel("chr{}:{}-{}".format(region.chrom, region.start,
                                                  region.end))
        plt.ylabel("PhyloP Score")
        plt.grid(True)


        plt.show()

    def validate_installation(self):
        self.filename = os.path.join(
            self.data_path,
            "hg19.100way.phyloP100way.bw"
        )

        assert (
            os.path.isfile(self.filename)
        ), "Could not find the PhyloP100Way file ('{}').".format(self.filename)


class CoreChromatinState(GenericAnnotation):
    def __init__(self, data_path=None, metadata_path=None):
        # Required fields.
        self.project = "Roadmap epigenomics project"
        self.description = (
            "A 15-state chromatin model that was generated using chromHMM "
            "over different histone modifications from the 111 reference "
            "epigenomes of the Roadmap Epigenomics project. A full "
            "of the different states is available at "
            "http://www.nature.com/nature/journal/v518/n7539/full/nature14248.html"
        )
        self.version = None

        # Path to data sources.
        self.data_path = data_path
        self.metadata_path = metadata_path
        self.filename_template = "{}_15_coreMarks_dense.bb"

        # State information.
        State = collections.namedtuple(
            "State",
            ("state_number", "mnemonic", "description", "color_name",
             "color_code")
        )
        self.states = {
            "1_TssA": State(1, "TssA", "Active TSS", "Red", "#FF0000"),
            "2_TssAFlnk": State(2, "TssAFlnk", "Flanking Active TSS",
                                "Orange Red", "#FF4500"),
            "3_TxFlnk": State(3, "TxFlnk", "Transcr. at gene 5' and 3'",
                              "LimeGreend", "#32CD32"),
            "4_Tx": State(4, "Tx", "Strong transcription", "Green", "#008000"),
            "5_TxWk": State(5, "TxWk", "Weak transcription", "Dark Green",
                            "#006400"),
            "6_EnhG": State(6, "EnhG", "Genic enhancers", "Green Yellow",
                            "#C2E150"),
            "7_Enh": State(7, "Enh", "Enhancers", "Yellow", "#FFFF00"),
            "8_ZNF/Rpts": State(8, "ZNF/Rpts", "ZNF genes & repeats",
                                "Medium Aquamarine", "#66CDAA"),
            "9_Het": State(9, "Het", "Heterochromatin", "Pale Turquoise",
                           "#8A91D0"),
            "10_TssBiv": State(10, "TssBiv", "Bivalent/Poised TSS",
                               "IndianRed", "#CD5C5C"),
            "11_BivFlnk": State(11, "BivFlnk", "Flanking Bivalent TSS/Enh",
                                "DarkSalmon", "#E9967A"),
            "12_EnhBiv": State(12, "EnhBiv", "Bivalent Enhancer", "DarkKhaki",
                               "#BDB76B"),
            "13_ReprPC": State(13, "ReprPC", "Repressed PolyComb", "Silver",
                               "#808080"),
            "14_ReprPCWk": State(14, "ReprPCWk", "Weak Repressed PolyComb",
                                 "Gainsboro", "#C0C0C0"),
            "15_Quies": State(15, "Quies", "Quiescent/Low", "White", "#FFFFFF")
        }

        # Validate the data structure.
        super(CoreChromatinState, self).__init__()

    def extract_region(self, region):
        chrom = region.chrom
        if not chrom.startswith("chr"):
            chrom = "chr{}".format(chrom)

        big_bed_to_bed = tools.BigBedToBed()
        cols = ("chrom", "chromStart", "chromEnd", "name", "score", "strand",
                "thickStart", "thickEnd", "itemRgb")

        data = []
        for eid, filename in self.data_files.items():
            bed = big_bed_to_bed.call(
                os.path.join(
                    self.data_path,
                    self.filename_template.format(eid)
                ),
                chrom=chrom, start=region.start, end=region.end
            )

            for line in bed:
                line = dict(zip(cols, line.rstrip().split()))
                data.append(
                    (eid, line["name"].decode("utf-8"), int(line["chromStart"]) + 1,
                     int(line["chromEnd"]) + 1)
                )

      
        return pd.DataFrame(
            data,
            columns=("eid", "chromatin_state", "start", "end")
        )

    def plot_region(self, region):
        """Create a static plot of the region."""
        print("starting plotting")

        plt.figure(figsize=(80,60))

        df = self.extract_region(region)

        metadata_df = pd.read_csv("package/data/roadmap_epigenomic/metadata/summary.tsv")
        sorter = metadata_df.eid.tolist()

        sorter_index = dict(zip(sorter, range(len(sorter))))
        df["eid_sorter"] = df.eid.map(sorter_index)
        df.sort_values("eid_sorter", axis = 0, ascending = True, inplace = True)

        cell_type = metadata_df[["eid","group","color"]]

        cell_type_count = dict(Counter(cell_type.group))


        for key in cell_type_count.keys():
            temp = cell_type.loc[metadata_df["group"] == key]
            y = 7 * sorter_index[temp.eid.iloc[0]]
            plt.axhspan(y, y+cell_type_count[key]*7, 
                facecolor = temp.color.iloc[0], alpha =  0.3)

        print("Starting data")
        for idx, row in df.iterrows():
            y = 7 * row.eid_sorter
            xmin = row.start + 1
            xmax = row.start + 1
            plt.plot((row.start + 1, row.end +1),(y,y), linewidth = 5, linestyle = "-", 
                color = self.states[row.chromatin_state].color_code)

        
            
        plt.show()

        # output_file("chromatin_state.html")

        # p = figure(plot_width=800, plot_height=600)
        # df = self.extract_region(region)

        # metadata_df = pd.read_csv("package/data/roadmap_epigenomic/metadata/summary.tsv")
        # sorter = metadata_df.eid.tolist()
        # cell_type = metadata_df.group.tolist()
        # cell_type_count = Counter(cell_type)
        # pprint(cell_type_count)
        # pprint(cell_type)

        # sorter_index = dict(zip(sorter, range(len(sorter))))
        # df["eid_sorter"] = df.eid.map(sorter_index)

        # df.sort_values("eid_sorter", axis = 0, ascending = True, inplace = True)





        # counter = 0
        # data = {"left": [], "right": [], "top": [], "bottom": [], "color": []}

        # for idx, row in df.iterrows():
        #     y = 7 * row.eid_sorter

        #     data["left"].append(row.start + 1)
        #     data["right"].append(row.end + 1)
        #     data["top"].append(y + 5)
        #     data["bottom"].append(y)

        #     data["color"].append(self.states[row.chromatin_state].color_code)

        

        # p.background_fill_color = "beige"
        # p.quad(line_color=None, **data)
        # p.line(x=[73628086, 73628086], y=[0, 5 * idx], line_width=1, line_color="#000000")
        

    def validate_installation(self):
        # Load and check metadata.
        metadata_filename = os.path.join(self.metadata_path, "summary.tsv")
        assert os.path.isfile(metadata_filename), (
            "Could not find metadata file ('{}') for Epigenomics Roadmap."
            "".format(metadata_filename)
        )

        self.metadata = pd.read_csv(
            metadata_filename,
            sep=",",
            header=0
        )

        #assert (
        #    set(self.metadata.columns) ==
        #    set(("eid", "group", "color", "epigenome_mnemonic",
        #         "std_epigenome_name", "epigenome_name", "anatomy"))
        #), "Incorrect format for metadata file."

        # Check the filenames for data.
        self.data_files = {}

        metadata_samples = set(self.metadata["eid"].values)
        observed_samples = set()
        expected = []
        for i in range(1, 129 + 1):
            eid = "E{}".format(str(i).rjust(3, "0"))
            if i in (60, 64):
                logger.info("Sample {} does not exist.".format(eid))
                continue

            filename = self.filename_template.format(eid)
            filename = os.path.join(self.data_path, filename)
            assert os.path.isfile(filename), "Could not find '{}'.".format(
                filename
            )

            observed_samples.add(eid)

            self.data_files[eid] = filename
        assert (
            metadata_samples == observed_samples
        ), "Metadata samples and observed samples are not identical."


class ImputedChromatinState(CoreChromatinState):
    def __init__(self, data_path=None, metadata_path=None):
        self.project = "Roadmap epigenomics project"
        self.description = (
            "A 25 state chromatin model generated from 12 histone marks on "
            "127 epigenomes. This is from imputed data which means that "
            "missing marks and values were guessed from other tissues and "
            "marks. A full description is available at "
            "http://egg2.wustl.edu/roadmap/web_portal/imputed.html"
        )
        self.version = None

        self.data_path = data_path
        self.metadata_path = metadata_path
        self.filename_template = "{}_25_imputed12marks_dense.bb"

        State = collections.namedtuple(
            "State",
            ("state_number", "mnemonic", "description", "color_name",
             "color_code")
        )

        self.states = {
            "1_TssA": State(1, "TssA", "Active TSS", "Red", "#FF0000"),
            "2_PromU": State(2, "PromU", "Promoter Upstream TSS", "Orange Red",
                             "#FF4500"),
            "3_PromD1": State(3, "PromD1", "Promoter Downstream TSS 1",
                              "Orange Red", "#FF4500"),
            "4_PromD2": State(4, "PromD2", "Promoter Downstream TSS 2",
                              "Orange Red", "#FF4500"),
            "5_Tx5'": State(5, "Tx5", "Transcribed - 5' preferential", "Green",
                           "#008000"),
            "6_Tx": State(6, "Tx", "Strong transcription", "Green", "#008000"),
            "7_Tx3'": State(7, "Tx3", "Transcribed - 3' preferential", "Green",
                           "#008000"),
            "8_TxWk": State(8, "TxWk", "Weak transcription", "Lighter Green",
                            "#009600"),
            "9_TxReg": State(9, "TxReg", "Transcribed & regulatory (Prom/Enh)",
                             "Electric Lime", "#C2E150"),
            "10_TxEnh5'": State(10, "TxEnh5",
                               "Transcribed 5' preferential and Enh",
                               "Electric Lime", "#C2E150"),
            "11_TxEnh3'": State(11, "TxEnh3",
                               "Transcribed 3' preferential and Enh",
                               "Electric Lime", "#C2E150"),
            "12_TxEnhW": State(12, "TxEnhW",
                               "Transcribed and Weak Enhancer Electric",
                               "Lime", "#C2E150"),
            "13_EnhA1": State(13, "EnhA1", "Active Enhancer 1", "Orange",
                              "#FFC34D"),
            "14_EnhA2": State(14, "EnhA2", "Active Enhancer 2", "Orange",
                              "#FFC34D"),
            "15_EnhAF": State(15, "EnhAF", "Active Enhancer Flank", "Orange",
                              "#FFC34D"),
            "16_EnhW1": State(16, "EnhW1", "Weak Enhancer 1", "Yellow",
                              "#FFFF00"),
            "17_EnhW2": State(17, "EnhW2", "Weak Enhancer 2", "Yellow",
                              "#FFFF00"),
            "18_EnhAc": State(18, "EnhAc", "Primary H3K27ac possible Enhancer",
                              "Yellow", "#FFFF00"),
            "19_DNase": State(19, "DNase", "Primary DNase", "Lemon",
                              "#FFFF66"),
            "20_ZNF/Rpts": State(20, "ZNF/Rpts", "ZNF genes & repeats",
                                 "Aquamarine", "#66CDAA"),
            "21_Het": State(21, "Het", "Heterochromatin", "Light Purple",
                            "#8A91D0"),
            "22_PromP": State(22, "PromP", "Poised Promoter", "Pink",
                              "#E6B8B7"),
            "23_PromBiv": State(23, "PromBiv", "Bivalent Promoter",
                                "Dark Purple", "#7030A0"),
            "24_ReprPC": State(24, "ReprPC", "Repressed Polycomb", "Gray",
                               "#808080"),
            "25_Quies": State(25, "Quies", "Quiescent/Low", "White",
                              "#FFFFFF"),
        }

        self.validate_installation()
