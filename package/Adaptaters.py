import json
from tools import *
from gepyto.formats.wig import WiggleFile
from gepyto.db import ensembl 
import os

import re
from pprint import pprint
import pandas as pd
import numpy as np

class Adaptater(object):
	"""docstring for Adaptater"""
	def __init__(self):

		super(Adaptater, self).__init__()




	def  get_region(region):
		"""Get the results for a given region."""
		raise NotImplementedError()


		

class BigBedAdaptater(Adaptater):
	"""docstring for BigBedAdaptater"""
	def __init__(self, dataset_path):

		self.dataset_path = dataset_path

		with open(dataset_path) as json_file:
			self.dataset = json.load(json_file)

		super(BigBedAdaptater, self).__init__()
		
	def get_region(self, region):

		chrom = region.chrom
		if not chrom.startswith("chr"):
		    chrom = "chr{}".format(chrom)

		big_bed_to_bed = BigBedToBed()
		cols = ("chrom", "chromStart", "chromEnd", "name", "score", "strand",
		        "thickStart", "thickEnd", "itemRgb")

		data = []
		data_path = self.dataset["dataset"]["data_path"]

		for resource in self.dataset["dataset"]["resources"]:
			eid = resource["id"]
			filename = resource["filename"]
			bed = big_bed_to_bed.call(os.path.join(
				data_path,
				filename
				),chrom=chrom, start=region.start, end=region.end
			)
			temp = []
			for line in bed:
				line = dict(zip(cols, line.rstrip().split()))
				temp.append(
				    [line["name"].decode("utf-8"), int(line["chromStart"]) + 1,
				                         int(line["chromEnd"]) + 1]
				)
			data.append({eid:tuple(temp)})

		return data




class BigWigAdaptater(Adaptater):
	"""docstring for  BigWigAdaptater"""
	def __init__(self, dataset_path):

		self.dataset_path = dataset_path
		with open(dataset_path) as json_file:
			self.dataset = json.load(json_file)

	def get_region(self,region):

		result = []
		data_path = self.dataset["dataset"]["data_path"]
		for resource in self.dataset["dataset"]["resources"]:
			filename = resource["filename"]
			big_wig_to_wig = BigWigToWig()
			wig = big_wig_to_wig.call(
				os.path.join(
				data_path,
				filename
				), 
				chrom=("chr" + region.chrom),
				start=(region.start - 1), 
				end=region.end
			)
			with WiggleFile(wig) as f:
				data = f.as_dataframe()

			result.append({"chr{}:{}-{}".format(region.chrom, region.start, region.end):\
				tuple(data["value"].tolist())})
		return result
        


		super( BigWigAdaptater, self).__init__(region)

class GTFAdaptater(Adaptater):
	"""docstring for GTFAdaptater"""
	def __init__(self, dataset_path):

		self.dataset_path = dataset_path
		with open(dataset_path) as json_file:
			self.dataset = json.load(json_file)

		super(GTFAdaptater, self).__init__()

	def get_region(self, region):

		data = []
		gtf_col_names = ['seqname', 'source', 'feature', 'start', 
						'end', 'score', 'strand', 'frame', 'attribute']

		dtypes = {'seqname':str, 'source':str, 'feature':str, 'start':int, 
				'end':int, 'score':str, 'strand':str, 'frame':str,'attribute':str}

		for resource in self.dataset["dataset"]["resources"]:

			df = pd.read_csv("".join([self.dataset["dataset"]["data_path"],
						resource["filename"]]),  index_col=False, sep=b"\t",
						names=gtf_col_names, comment=b"#", compression="gzip", dtype=dtypes)

			result_df_genes = df[(df.seqname == region.chrom) & 
								(df.start >= region.start) & 
								(df.end <= region.end) & 
								(df.feature == "gene")]


			for idx, row in result_df_genes.iterrows():
				attribute = row.attribute
				gene_name = re.search("gene_name \"(.+?)\";", attribute).group(1)
				gene_id = re.search("gene_id \"(.+?)\";", attribute).group(1)
				result_df = df[(row.seqname == df.seqname) & 
							(df.start >= row.start) & 
							(df.end <= row.end) & 
							(df.attribute.str.contains(gene_id))]

				temp = []

				for idx_result, row_result in result_df.iterrows():

					temp.append([row_result.feature, row_result.start, row_result.end])

				data.append({gene_name:tuple(temp)})
					

		return data