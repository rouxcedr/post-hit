from flask import Flask
import os
from package.dataset import DataSet
from flask import jsonify, request
import json

from gepyto.structures.region import Region


app =  Flask(__name__)

@app.route("/region/<string:region>/")
def get_region(region):

    return_data = []

    query_string = request.query_string.decode("utf-8")
    querys = query_string.split("&")


    datasets = []
    r = Region(region.split(":")[0], region.split(":")[1].split("-")[0],region.split("-")[1])
    for query in querys:
        if query.split("=")[0] == "dataset":
            dataset = DataSet(query.split("=")[1])

            data = dataset.get_region(r)
            dataset_name = os.path.splitext(os.path.basename(query.split("=")[1]))[0]

            return_data.append({dataset_name:data})

    return jsonify({"response":return_data, "sucess": 1})

@app.route("/resources/<string:dataset>/<string:id>")
def ressource(dataset, id):
    dataset = DataSet(dataset)

    with open(dataset.dataset_path) as json_file:
        dataset_json = json.load(json_file)

    metadata = dataset_json["dataset"]["metadata"]
    print(metadata)
    for data in metadata:
        if data["id"] == id:
            return jsonify(data)




if __name__ == '__main__':
    #get_region("19:45819671-45826235")
    app.run()