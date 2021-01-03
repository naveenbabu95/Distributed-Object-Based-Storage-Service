from django.shortcuts import render
from django.core.cache import cache
import os, json, imp, shutil #, stat
from dynamo import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from copy import copy
import requests
from .utils import *


@csrf_exempt
def read_file(request):
		fail_list = []
		try:
			# initializing final response which will have latest version of file out of all node
			response_final = {
			'success': True,
			'filename': 'temp',
			'vector_1': 0,
			'vector_2': 0,
			'vector_3': 0,
			'node' : 'node'
			}

			jsondata = json.loads(json.dumps(request.POST))

			# forwarding read request to node1
			response1 = send_request(request, nodeList[0],jsondata)
			print(response1)
			if response1['success']:
				# if file is found, checks for the version
				get_latest_version(request, response1, response_final)
			else:
				# adds to failed list due to either bucket not found or file not found
				fail_list.append({'request': request, 'response': response1})

			# forwarding read request to node2
			jsondata['node'] = 'node2'
			response2 = send_request(request, nodeList[1],jsondata)

			if response2['success']:
				# if file is found, checks for the version
				get_latest_version(request, response2, response_final)
			else:
				# adds to failed list due to either bucket not found or file not found
				fail_list.append({'request': request, 'response': response2})

			# forwarding read request to node2
			# response3 = send_request(request, nodeList[2],jsondata)

			# if response3['success']:
			# 	# if file is found, checks for the version
			# 	get_latest_version(request, response3, response_final)
			# else:
			# 	# adds to failed list due to either bucket not found or file not found
			# 	fail_list.append({'request': request, 'response': response3})

			# for the nodes who don't have bucket or file, this will update that node with latest info
			update_response = {}
			for node in fail_list:
				update_response = get_latest_version(node['request'], node['response'], response_final)

			print("oiuygf")
			response = {
				"node1" : response1,
				"node2" : response2,
				# "node3" : response3,
				"selectedFile" : response_final,
				"updateNodeResponse" : update_response # to make sure update is successful or not
			}

		except Exception as e:
			print(e)
			response = {
				"success" : False,
				"error" : "An unexpected error occured!",
				"Exception" : str(type(e))
			}

		return JsonResponse(response)

@csrf_exempt
def get_file(request, updated_node, old_node, response_final, path):
	jsondata = json.loads(json.dumps(request.POST))
	request.path = '/bucket/get_file/'
	API_ENDPOINT = nodeList[int(updated_node.replace('node','')) - 1] + request.path
	file_response = requests.post(url = API_ENDPOINT, data = jsondata)

	jsondata['node'] = old_node
	update_request = copy(request)
	update_request.path = path
	API_ENDPOINT = nodeList[int(old_node.replace('node','')) - 1] + update_request.path

	filename = jsondata['fileName'] + '.pdf'
	with open(filename, 'wb+') as temp:
		temp.write(file_response.content)

	file = {'fileContent': open(filename,'rb')}
	jsondata.update({'vector_1': response_final['vector_1'], 'vector_2': response_final['vector_2'], 'vector_3': response_final['vector_3']})
	response = requests.post(url = API_ENDPOINT, files = file, data = jsondata)

	# os.chmod(filename, stat.S_IWRITE)
	# os.remove(filename)
	return HttpResponse(response)

@csrf_exempt
def create_bucket(request, node):
	print("oh yeahhh")
	jsondata = json.loads(json.dumps(request.POST))
	request.path = '/bucket/create_bucket/'
	API_ENDPOINT = nodeList[node - 1] + request.path
	response = requests.post(url = API_ENDPOINT, data = jsondata)
	return HttpResponse(response)

def send_request(request, ipAddress, jsondata):
	try:
		API_ENDPOINT = ipAddress + request.path.replace("coordinator","bucket")

		response = requests.post(url = API_ENDPOINT, data = jsondata)
		return json.loads(response.text)
	except Exception as e:
		print('exception')
		response = {
			"success" : False,
			"error" : "An error occured at Node with ip" + ipAddress,
			"exception" : str(type(e))
		}
	return response


def get_latest_version(request, response, response_final):
	if response['success']:
		path = '/bucket/update_file/'
		filename = response['filename']
		cur_version = True
		final_version = True
		if (int(response['vector_1']) != response_final['vector_2'] and int(response['vector_1']) != response_final['vector_3']):
			if int(response['vector_1']) > response_final['vector_1']:
				response_final['vector_1'] = response['vector_1']
				cur_version = True
				final_version = False
			elif int(response['vector_1']) < response_final['vector_1']:
				final_version = True
				cur_version = False
				response['vector_1'] = int(response_final['vector_1'])

		if (int(response['vector_2']) != response_final['vector_1'] and int(response['vector_2']) != response_final['vector_3']):
			if int(response['vector_2']) > response_final['vector_2']:
				response_final['vector_2'] = response['vector_2']
				cur_version = True
				final_version = False
			elif int(response['vector_2']) < response_final['vector_2']:
				final_version = True
				cur_version = False
				response['vector_2'] = int(response_final['vector_2'])

		if (int(response['vector_3']) != response_final['vector_2'] and int(response['vector_3']) != response_final['vector_1']):
			if int(response['vector_3']) > response_final['vector_3']:
				response_final['vector_3'] = response['vector_3']
				cur_version = True
				final_version = False
			elif int(response['vector_3']) < response_final['vector_3']:
				final_version = True
				cur_version = False
				response['vector_3'] = int(response_final['vector_3'])

		print(cur_version, final_version)
		print(cur_version > final_version)
		if cur_version and not final_version:
			response_final['filename'] = response['filename']
			print(type(response_final['node']))
			if response_final['node'] != 'node':
				get_file(request, response['node'], response_final['node'], response_final, path)
			response_final['vector_1'] = response['vector_1']
			response_final['vector_2'] = response['vector_2']
			response_final['vector_3'] = response['vector_3']
			print("vihsgfjb")
			response_final['node'] = response['node']

		elif final_version and not cur_version:
			
			get_file(request, response_final['node'], response['node'], response_final, path)
	
	elif 'bucket' in response['error'].lower():
		print("does nothing")
		# path = '/bucket/create_file/'
		# jsondata = json.loads(json.dumps(request.POST))

		# print(path)
		# bucket_response = create_bucket(request, response['node'])

		# if bucket_response.status_code == 200:
		# 	print("yes t is")
		# 	get_file(request, response_final['node'], response['node'], response_final['version'], path)

	elif 'file' in response['error'].lower():
		path = '/bucket/create_file/'
		jsondata = json.loads(json.dumps(request.POST))

		get_file(request, response_final['node'], response['node'], response_final, path)

