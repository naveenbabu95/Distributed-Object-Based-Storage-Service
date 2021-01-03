import json
import hashlib

nodeList = []

def generate_hashvalue(key):
	return int(hashlib.sha1(key.encode('utf-8')).hexdigest(), 16) % 10 ** 8 # 4 digit hash value mod 3
	# print(type(key))
	#Read from json file later
	# nodeList = ['http://192.168.56.101:8000', 'http://192.168.56.102:8000', 'http://192.168.56.103:8000']


def get_ip_list_from_json():
	with open('dynamo_env.json') as json_file:
		data = json.load(json_file)
	nodeList.append(data["node1"])
	nodeList.append(data["node2"])
	nodeList.append(data["node3"])

def get_node_number(value):
	return (generate_hashvalue(value) % 12)%3
