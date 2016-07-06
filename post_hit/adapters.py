#!/usr/bin/env python
import json
try:
    from . import tools
except SystemError:
    import tools
    
from gepyto.formats.wig import WiggleFile
from gepyto.db import ensembl 
import os
from collections import defaultdict

import re
from pprint import pprint
import pandas as pd
import numpy as np
from gepyto.db import index
import subprocess

POST_HIT_PATH = os.path.dirname(__file__) + "/"
# print(POST_HIT_PATH)

class Adapter(object):
    """
        Creates an adapter to the file type to be able to extract the data from the files.

        :param dataset_path: The path to the local JSON dataset file.
        :type dataset_path: str

    """
    def __init__(self, dataset_path):

        self.dataset_path = dataset_path
        with open(self.dataset_path) as json_file:
            self.dataset = json.load(json_file)

        super(Adapter, self).__init__()

    def  get_region(self, region):
        """Get the data for a given region.

            :param region: The region where the data is to be extracted.
            :type region: gepyto.structures.region.Region

        """
        raise NotImplementedError()

    def get_values(self):

        """
            Extracts and formats the data depending how the different adapters extract the region from the file.

            There is 2 formats in wich the data is extracted : 

                - "key-list" : {key1 : ( ({field1 : data1, field2 : data2}, start, end), ({field1 : data1, field2 : data2}, start, end) ),
                                key2 : ( ({field1 : data1, field2 : data2}, start, end), ({field1 : data1, field2 : data2}, start, end) ), ...}

                - "vector" : {key1 : (position, position, position, position, position),
                              key2 : (position, position, position, position, position)}

            :return result: The formated data as described.
            :rtype: dict

        """
        raise NotImplementedError()
     

class BigBedAdapter(Adapter):
    """Adapter for BigBed (.bb) files"""
    def __init__(self, dataset_path):

        super(BigBedAdapter, self).__init__(dataset_path)
        
    def get_region(self, region):

        self.region = region
        chrom = self.region.chrom
        if not chrom.startswith("chr"):
            chrom = "chr{}".format(chrom)

        big_bed_to_bed = tools.BigBedToBed()
        
        data = defaultdict(list)
        data_path = "".join([POST_HIT_PATH,self.dataset["dataset"]["data_path"]])

        for resource in self.dataset["dataset"]["resources"]:

            filename = resource["filename"]
            bed = big_bed_to_bed.call(os.path.join(
                data_path,
                filename
                ),chrom=chrom, start=self.region.start, end=self.region.end
            )
            key = self.dataset["dataset"]["data_representation"]["key"]
            if key.split("/")[0] == "resource":
                result = self.get_values(bed, resource[key.split("/")[1]])
            else:
                result = self.get_values(bed, key)

            for key in result:
                data[key] = result[key]

        return data

    def get_values(self, bed, key):

        """
            :param bed: Open file with pointer on the starting position of the region.
            :type: post_hit.package.tools.ResultsIterator

            :param key: key or column where the key can be find.
        """

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
    """Adapter for BigWig (.bw) files"""
    def __init__(self, dataset_path):

        super( BigWigAdapter, self).__init__(dataset_path)

    def get_region(self,region):

        self.region = region

        data = defaultdict(list)
        data_path = "".join([POST_HIT_PATH,self.dataset["dataset"]["data_path"]])
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

            result = self.get_values(df)
            for key in result:
                data[key] = result[key]

        return data

    def get_values(self, df):

        """
            :param df: Dataframe containing the region's data.
            :type: pandas.core.frame.DataFrame

        """

        result = defaultdict(list)

        if self.dataset["dataset"]["data_representation"]["representation"] == "key-list":

            for idx, row in df.iterrows():

                value = defaultdict(list)
                key_loc = self.dataset["dataset"]["data_representation"]["key"]
                key = row[key_loc]
                value = {field : row[field] for field in self.dataset["dataset"]["data_representation"]["fields"]}

                result[key].append(tuple([value, row["pos"], row["pos"]]))

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

        



class GTFAdapter(Adapter):
    """Adapter for GTF compressed (.gtf.gz) files"""
    def __init__(self, dataset_path):

        super(GTFAdapter, self).__init__(dataset_path)

    def get_region(self, region):
        self.region = region

        data = defaultdict(list)
        gtf_col_names = ['seqname', 'source', 'feature', 'start', 
                        'end', 'score', 'strand', 'frame', 'attribute']

        dtypes = {'seqname':str, 'source':str, 'feature':str, 'start':int, 
                'end':int, 'score':str, 'strand':str, 'frame':str,'attribute':str}

        for resource in self.dataset["dataset"]["resources"]:

            df = pd.read_csv("".join([POST_HIT_PATH, self.dataset["dataset"]["data_path"],
                        resource["filename"]]),  index_col=False, sep=b"\t",
                        names=gtf_col_names, comment=b"#", compression="gzip", dtype=dtypes)

            start_inside = (df.start >= region.start) & (df.start <= region.end)
            end_inside = (df.end >= region.start) & (df.end <= region.end)
            gene_inside = (df.end >= region.start) & (df.start <= region.end)
            good_chrom = df.seqname == self.region.chrom

            
            result_df = df[good_chrom & (start_inside | end_inside | gene_inside)]

            result = self.get_values(result_df)
            for key in result:
                data[key] = result[key]
        return data

    def get_values(self, df):

        
        """
            :param df: Dataframe containing the region's data.
            :type: pandas.core.frame.DataFrame

        """

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
                    except KeyError:
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

class XsvAdapter(Adapter):
    """
        Adapter for X Separated Values files where X is a seperator.
        example : Coma Separated Values files (.csv) or Tab Separated Values files (.tsv)
        
        :param sep: The separator of the values in the file.
        :type: str

    """
    def __init__(self, dataset_path, sep):

        super(XsvAdapter, self).__init__(dataset_path)
        self.sep = sep
        self.index_files()

       

    def get_region(self, region):

        self.region = region
        data_path = self.dataset["dataset"]["data_path"]
        data = defaultdict(list)
        for resource in self.dataset["dataset"]["resources"]:

            index_var = index.get_index("".join([POST_HIT_PATH, data_path, resource["filename"]]))
            key = self.dataset["dataset"]["data_representation"]["key"]
            with open("".join([POST_HIT_PATH, data_path, resource["filename"]])) as f:
                cols = f.readline().rstrip().split(self.sep)
                index.goto(f, index_var, region.chrom, region.start)

                if key.split("/")[0] == "resource":      
                    result = self.get_values(f, cols, resource[key.split("/")[1]])
                    if bool(result) :
                        for key in result:
                            data[key] = result[key]
                else :
                    result = self.get_values(f, cols, key)
                    if bool(result) :
                        for key in result:
                            data[key] = result[key]
        return data

    def get_values(self, f, cols, key):
        """
            :param f: Open file with pointer on the starting position of the region.
            :type: io.TextIOWrapper

            :param key: key or column where the key can be find.
            :type: str

            :param cols: List of the columns name (Header)
            :type: list


        """
        chrom = self.dataset["dataset"]["data_representation"]["chrom"]
        start = self.dataset["dataset"]["data_representation"]["start"]
        end = self.dataset["dataset"]["data_representation"]["end"]

        result = defaultdict(list)
        for line in f :
            line = dict(zip(cols, line.rstrip().split()))
            if int(line[start]) <= self.region.start:
                continue
            if int(line[chrom]) != int(self.region.chrom) :
                break
            if int(line[start]) >= self.region.end and int(line[end]) >= self.region.end:
                break
                  
            value = {field:line[field] for field in self.dataset["dataset"]["data_representation"]["fields"]}   
            key = line[key] if key == self.dataset["dataset"]["data_representation"]["key"] else key

            result[key].append(tuple([value, int(line[start]),
                                         int(line[end])]))
        return result
    def index_files(self):

        """
            Indexes the files for faster data queries.

            Uses gepyto.db.index module to index the files and subprocess package to sort the files to be indexed. 

            (ONLY COMPATIBLE WITH UNIX BASED SYSTEMS)

        """
        for resource in self.dataset["dataset"]["resources"]:

            path = "".join([POST_HIT_PATH, self.dataset["dataset"]["data_path"], resource["filename"]])

            try:
                index_file = resource["index_file"]
            except KeyError:                     

                chrom_col = open(path, "r") \
                            .readline() \
                            .split(self.sep) \
                            .index(self.dataset["dataset"]["data_representation"]["chrom"])
                pos_col = open(path, "r") \
                                .readline() \
                                .split(self.sep) \
                                .index(self.dataset["dataset"]["data_representation"]["start"]) 

                header = open(path, "r").readline()
                output = open("".join([POST_HIT_PATH, "tmp/temp.txt"]), "a")
                output.write(header)
                output.flush()
                removing_header_args = ["tail", "-n", "+2", path]
                sorting_args = ["sort", "-t\t", "-k", "{},{}n".format(chrom_col +1,chrom_col+1), "-k", "{},{}n".format(pos_col+1,pos_col+1)]
            
                rm_header = subprocess.Popen(removing_header_args, stdout = subprocess.PIPE)
                subprocess.call(sorting_args, stdin = rm_header.stdout, stdout = output )
                
                output.close()

                subprocess.call(["mv", "".join([POST_HIT_PATH, "tmp/temp.txt"]), path])
                resource["index_file"] = index.build_index(path, 
                                                        chrom_col, pos_col, 
                                                        delimiter = self.sep, 
                                                        skip_lines = 1, 
                                                        ignore_startswith = "#")

                with open (self.dataset_path, 'w') as json_file:
                   json.dump(self.dataset, json_file)

