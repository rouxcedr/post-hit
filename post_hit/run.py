from flask import Flask
import os
from dataset import DataSet
from flask import jsonify, request
from flask import render_template
import json
from collections import defaultdict

from gepyto.structures.region import Region


app =  Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/test")
def test():
    return render_template('test.html')

@app.route("/week_temperature_sf.csv")
def csv():
    return open("templates/week_temperature_sf")

@app.route("/region/<string:region>/")
def get_region(region):

    """
        The main endpoint to get the information on the given region
    
        :param region: The genomic region who's data is to be extracted. ( chrom:start-end )
        :type: str
        
        ADDITIONAL PARAMETERS of the endpoint :
        These parameters are to be added to the query url as so : /region/<string:region> **?param=<string>**

        :param dataset: Name of the dataset in which the region's data is to be fetched.
        :type: str


        :return: A JSONify dict with the the formated data under the "response" key.
        :rtype: dict

    """

    return_data = defaultdict(list)

    query_string = request.query_string.decode("utf-8")
    querys = query_string.split("&")


    datasets = []
    r = Region(region.split(":")[0], region.split(":")[1].split("-")[0],region.split("-")[1])
    for query in querys:
        if query.split("=")[0] == "dataset":
            dataset = DataSet(query.split("=")[1])

            data = dataset.get_region(r)
            dataset_name = os.path.splitext(os.path.basename(query.split("=")[1]))[0]

            return_data[dataset_name] = data


    return jsonify({"response":return_data, "sucess": 1})

@app.route("/resources/<string:dataset>/")
def ressource(dataset):
    """
        Gets the metadata information described in the JSON.

        :param dataset: The dataset name where the information is to be fetched.
        :type: str

        :param id: The id of the queried information (ex : E001 for roadmap_epigenomics).
        :type: str
    
    """

    query_string = request.query_string.decode("utf-8")
    ids = [query.split("=")[1] for query in query_string.split("&")]
    ids = [id.replace("%27", "'") if "%27" in id else id for id in ids ]
    print(ids)
    dataset = DataSet(dataset)

    with open(dataset.dataset_path) as json_file:
        dataset_json = json.load(json_file)

    result = []

    metadata = dataset_json["dataset"]["metadata"]
    for data in metadata:
        if data["id"] in ids:
            result.append(data)
    if len(result) == 1:
        print(result)
        return jsonify(result[0])
    else:
        return jsonify({"response":result, "sucess": 1})

@app.route("/xref/<string:dataset>/")
def xref(dataset):
    """
        Gets the metadata information described in the JSON.

        :param dataset: The dataset name where the information is to be fetched.
        :type: str

        :param x_ref_id: The id of the queried information (ex : E001 for roadmap_epigenomics).
        :type: str
    
    """

    query_string = request.query_string.decode("utf-8")
    print(query_string)
    ids = [query.split("=")[1] for query in query_string.split("&")]
    ids = [id.replace("%27", "'") if "%27" in id else id for id in ids ]
    dataset = DataSet(dataset)

    with open(dataset.dataset_path) as json_file:
        dataset_json = json.load(json_file)

    result = []

    metadata = dataset_json["dataset"]["metadata"]
    for data in metadata:
        if data["id"] in ids:
            result.append({"name": data["id"], "id":data["x_ref_id"]})
    
    if len(result) == 1:
        print(result)
        return jsonify([result[0]])
    else:
        return jsonify([result])




if __name__ == '__main__':
    #ressource("roadmap_epigenomic.json", "E017")
    #get_region("19:45819671-45826235")
    app.run()