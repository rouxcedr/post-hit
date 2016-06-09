import json
from . import tools
from gepyto.formats.wig import WiggleFile
from gepyto.db import ensembl 
import os
from collections import defaultdict

import re
from pprint import pprint
import pandas as pd
import numpy as np

class Adapter(object):
	"""docstring for Adapter"""
	def __init__(self, dataset_path):

		self.dataset_path = dataset_path

		with open(self.dataset_path) as json_file:
			self.dataset = json.load(json_file)

		super(Adapter, self).__init__()

	def  get_region(self, region):
		"""Get the results for a given region."""
		raise NotImplementedError()

	def get_values(self, df):

		result = defaultdict(list)

		if self.dataset["dataset"]["data_representation"]["representation"] == "key-list":

			if isinstance(df, pd.DataFrame):

				for idx, row in df.iterrows():

					value = defaultdict(list)

					key_loc = self.dataset["dataset"]["data_representation"]["key"]

					if len(key_loc.split("/")) == 1:

						key = row[key_loc]
					else:
						key = re.search(key_loc.split("/")[1] + ".?\"(.+?)\";", row[key_loc.split("/")[0]]).group(1)

					for field in self.dataset["dataset"]["data_representation"]["fields"]:
						if len(field.split("/")) == 1:
							value[field] = row[field]
						else:
							value[field.split("/")[0]] = re.search(field.split("/")[1] + "\"(.+?)\";", row[field.split("/")[0]]).group(1)

					try:
						start = self.dataset["dataset"]["data_representation"]["start"]
						end = self.dataset["dataset"]["data_representation"]["end"]
					except ValueError:
						start = "start"
						end = "end"

					result[key].append(tuple([value, row[start], row[end]]))

			else:
				raise ValueError("")

		elif self.dataset["dataset"]["data_representation"]["representation"]  == "vector":
 	
			if len(self.dataset["dataset"]["data_representation"]["fields"]) == 1:

				key = "chr{}:{}-{}".format(self.region.chrom, self.region.start, self.region.end)
				value = df[self.dataset["dataset"]["data_representation"]["fields"][0]].tolist()

				result[key] = value

			else : 
				raise ValueError("Can't have more than one value field for a vector representation")
		else:
			raise ValueError("Data representation not recognised") 

		return result

		

class BigBedAdapter(Adapter):
	"""docstring for BigBedAdapter"""
	def __init__(self, dataset_path):

		super(BigBedAdapter, self).__init__(dataset_path)
		
	def get_region(self, region):

		self.region = region
		chrom = self.region.chrom
		if not chrom.startswith("chr"):
		    chrom = "chr{}".format(chrom)

		big_bed_to_bed = tools.BigBedToBed()
		
		data = []
		data_path = self.dataset["dataset"]["data_path"]

		for resource in self.dataset["dataset"]["resources"]:

			filename = resource["filename"]
			bed = big_bed_to_bed.call(os.path.join(
				data_path,
				filename
				),chrom=chrom, start=self.region.start, end=self.region.end
			)
			key = self.dataset["dataset"]["data_representation"]["key"]
			if key.split("/")[0] == "resource":
				data.append(self.get_values(bed, resource[key.split("/")[1]]))
			else:
				data.append(self.get_values(bed, key))

		return data

	def get_values(self, bed, key):
		result = defaultdict(list)
		cols = ("chrom", "chromStart", "chromEnd", "name", "score", "strand",
		        "thickStart", "thickEnd", "itemRgb")

		for line in bed:

			line = dict(zip(cols, line.rstrip().split()))

			value = {field:line[field].decode("utf-8") for field in self.dataset["dataset"]["data_representation"]["fields"]}	
			key = line[key] if key == self.dataset["dataset"]["data_representation"]["key"] else key

			result[key].append(tuple([value, int(line["chromStart"]) + 1,
				                         int(line["chromEnd"]) + 1]))

		return result

class BigWigAdapter(Adapter):
	"""docstring for  BigWigAdapter"""
	def __init__(self, dataset_path):

		super( BigWigAdapter, self).__init__(dataset_path)

	def get_region(self,region):

		self.region = region

		data = []
		data_path = self.dataset["dataset"]["data_path"]
		for resource in self.dataset["dataset"]["resources"]:
			filename = resource["filename"]
			big_wig_to_wig = tools.BigWigToWig()
			wig = big_wig_to_wig.call(
				os.path.join(
				data_path,
				filename
				), 
				chrom=("chr" + self.region.chrom),
				start=(self.region.start - 1), 
				end=self.region.end
			)
			with WiggleFile(wig) as f:
				df = f.as_dataframe()

			data.append(self.get_values(df))

		return data
        



class GTFAdapter(Adapter):
	"""docstring for GTFAdapter"""
	def __init__(self, dataset_path):

		super(GTFAdapter, self).__init__(dataset_path)

	def get_region(self, region):

		self.region = region

		data = []
		gtf_col_names = ['seqname', 'source', 'feature', 'start', 
						'end', 'score', 'strand', 'frame', 'attribute']

		dtypes = {'seqname':str, 'source':str, 'feature':str, 'start':int, 
				'end':int, 'score':str, 'strand':str, 'frame':str,'attribute':str}

		for resource in self.dataset["dataset"]["resources"]:

			df = pd.read_csv("".join([self.dataset["dataset"]["data_path"],
						resource["filename"]]),  index_col=False, sep=b"\t",
						names=gtf_col_names, comment=b"#", compression="gzip", dtype=dtypes)
			
			result_df = df[(df.seqname == self.region.chrom) & 
						(df.start >= self.region.start) & 
						(df.end <= self.region.end)]

			data.append(self.get_values(result_df))
		return data

class XsvAdapter(Adapter):
	def __init__(self, dataset_path):

		super(XsvAdapter, self).__init__(dataset_path)

	def get_region(self, region):

		self.region = region

		data = []
		for resource in self.dataset["dataset"]["resources"]:

			df = pd.read_csv("".join([self.dataset["dataset"]["data_path"],
						resource["filename"]]),  index_col=False, sep=b"\t",
						comment=b"#")
			
			result_df = df[(df[self.dataset["dataset"]["data_representation"]["chrom"]] == int(self.region.chrom)) & 
						(df[self.dataset["dataset"]["data_representation"]["start"]] >= self.region.start) & 
						(df[self.dataset["dataset"]["data_representation"]["end"]] <= self.region.end)]

			
			data.append(self.get_values(result_df))
		return data