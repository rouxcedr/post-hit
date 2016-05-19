from eve import Eve
import os
from dataset import *
from flask import jsonify, request

from gepyto.structures.region import Region


app = Eve()


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


	return jsonify({"return_data":return_data})




if __name__ == '__main__':
	#get_region("19:45819671-45826235")
	app.run()