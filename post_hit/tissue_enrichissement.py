#CE CODE N'EST PAS FINI

import json
from urllib.request import urlopen


# class Tree(object):
#     """docstring for Tree"""
#     def __init__(self):
#         self.root = Node("", None)

#     def search_node(self, node, value):

#         if value == node.value:
#             return node

#         for child in node.child:
#             self.search_node(child, value)

#     def get_child_value(self, node):

#         if not node.child:
#             return [node.value]

#         for child in node.child:
#             self.get_child_value(child).append(node.value)

#     def add_node(self, node_data):

#         parent = node_data["parent"]
#         value = node_data["id"]

#         parent_node = self.search_node(self.root, parent)
#         new_node = Node(value, parent_node)
#         parent_node.child.append(new_node)

# class Node(object):
#         """docstring for Node"""
#         def __init__(self, value, parent):
#             self.value = value
#             self.parent = parent
#             self.child = []
def find_node(id, tree):
    for node in tree:
        if node["id"] != id:
            return node

def find_childs(parent_name, tree):
    found_childs = []
    for node in tree:
        if node["parent"] == parent_name:
            found_childs.append(node)

    return found_childs


with open("data/datasets/termes.json") as f:
    termes_lst = json.load(f)

id = "1471"
node = find_node(id, termes_lst)
childs = find_childs(node["name"], termes_lst)

for child in childs:
    childs += find_childs(child["name"], termes_lst)

ids = [id]
for child in childs:
    ids.append(child["id"])

url = "http://127.0.0.1:5000/region/{id}"
opt = ["dataset=roadmap_epigenomic.json","dataset=gtex.json"]

# Constructing the final URL
query_url = "{}?{}".format(url, "&".join(opt)).format(id="16:4003388-4166186")
print(query_url)

roadmap_epigenomic_transciption_id = ["5_Tx5'", "10_TxEnh5", "8_TxWk", "7_Tx3'", "6_Tx", "11_TxEnh3'", "12_TxEnhW", "9_TxReg"]

stream = urlopen(query_url)
result = json.loads(stream.read().decode())
stream.close()

xref_ids = []
for dataset in result["response"]:
    dataset_name = dataset
    for tissue_hit in result["response"][dataset]:
        url = "http://127.0.0.1:5000/xref/{dataset}"
        opt = ["id=" + tissue_hit]

        # Constructing the final URL
        query_url = "{}?{}".format(url, "&".join(opt)).format(dataset=dataset_name)

        stream = urlopen(query_url)
        ids = json.loads(stream.read().decode())
        stream.close()

    for tissue in result["response"][dataset]:
        for data in result["response"][dataset][tissue]:
            if dataset_name == "roadmap_epigenomic" and data[0]["name"] in roadmap_epigenomic_transciption_id:


                #CODE PAS FINI
                














        










