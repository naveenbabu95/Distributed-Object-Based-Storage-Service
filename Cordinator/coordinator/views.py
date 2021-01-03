from django.shortcuts import render
from django.core.cache import cache
import os, json, imp, shutil
from dynamo import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import datetime
import requests
from rest_framework import status
from copy import copy
from .utils import *
from .gossip import *

get_ip_list_from_json()


@csrf_exempt
def create_bucket(request):
	response = {}
	try:
		jsondata = json.loads(json.dumps(request.POST))
		print(jsondata)

		replica1 = get_node_number(jsondata["bucketName"])
		replica2 = (replica1 + 1)%3

		# ******************* For Testing *******************
		replica1 = 0
		replica2 = 1
		jsondata.update({'node': 'node' + str(replica1+1)})
		response1 = send_request(request, replica1, nodeList[replica1],jsondata, False)
		print(response1)
		if response1['Exception']:
			# handoff_manager(request, replica1, nodeList[(replica1 + 1)%3],jsondata, fileContent)
			response1 = send_request(request, replica2, nodeList[replica2], jsondata, False) # Temp

		jsondata.update({'node': 'node' + str(replica2+1)})
		response2 = send_request(request, replica2, nodeList[replica2],jsondata, False)
		if response2['Exception']:
			# handoff_manager(request, replica1, nodeList[(replica1 + 1)%3],jsondata, fileContent)
			response2 = send_request(request, replica1, nodeList[replica1], jsondata, False)

		response = {
			"response1" : response1,
			"response2" : response2
		}
	except Exception as e:
		response = {
			"success" : False,
			"error" : "An error occured",
			"Exception" : str(e)
		}
	return response

@csrf_exempt
def delete_bucket(request):
	response = {}
	try:
		jsondata = json.loads(json.dumps(request.POST))

		replica1 = 0
		replica2 = 1

		# print(nodeList[2])
		# Delete bucktes from all replicas
		fileContent = request.FILES['fileContent'] if 'fileContent' in request.FILES else False

		jsondata.update({'node': 'node' + str(replica1+1)})
		response1 = send_request(request, replica1, nodeList[replica1],jsondata, False)
		print(response1)
		if response1['Exception']:
			# handoff_manager(request, replica1, nodeList[(replica1 + 1)%3],jsondata, fileContent)
			response1 = send_request(request, replica2, nodeList[replica2], jsondata, False) # Temp

		jsondata.update({'node': 'node' + str(replica2+1)})
		response2 = send_request(request, replica2, nodeList[replica2],jsondata, False)
		if response2['Exception']:
			# handoff_manager(request, replica1, nodeList[(replica1 + 1)%3],jsondata, fileContent)
			response2 = send_request(request, replica1, nodeList[replica1], jsondata, False)
		# response3 = send_request(request, 2, nodeList[2],jsondata, fileContent)

		response = {
			"response1" : response1,
			"response2" : response2,
			# "response3" : response3
		}

	except Exception as e:
		response = {
			"success" : False,
			"error" : "An error occured",
			"Exception" : e
		}
	return JsonResponse(response)

@csrf_exempt
def create_file(request):
	response = {}
	try:
		jsondata = json.loads(json.dumps(request.POST))
		fileContent = request.FILES['fileContent'] if 'fileContent' in request.FILES else False
		# replica1 = get_node_number(jsondata["bucketName"] + jsondata["fileName"])
		# replica2 = (replica1 + 1)%3
		replica1 = 0
		replica2 = 1

		# ******************* For Testing *******************
		temprequest = copy(request)
		temprequest.path = '/bucket/create_bucket/'

		jsondata.update({'node': 'node' + str(replica1+1)})
		response1 = send_request(request, replica1, nodeList[replica1], jsondata, fileContent)
		print("request 1 done")
		print(response1)

		if response1['Exception']:
			response1 = send_request(request, replica2, nodeList[replica2], jsondata, fileContent)
			if "error" in response1:
				if "bucket" in response1["error"].lower():
					# create bucket
					send_request(temprequest, replica2, nodeList[replica2], jsondata, fileContent)
					print(jsondata)
					print(request.path)
					# create file in that bucket
					response1 = send_request(request, replica2, nodeList[replica2],jsondata, fileContent)
		elif "error" in response1:
			if "bucket" in response1["error"].lower():
				# create bucket
				send_request(temprequest, replica1, nodeList[replica1], jsondata, fileContent)
				# create file in that bucket
				response1 = send_request(request, replica1, nodeList[replica1],jsondata, fileContent)

		print("request 1 done")
		jsondata['vector_1'] = int(response1['vector_1'])
		jsondata['vector_2'] = int(response1['vector_2']) + 1
		jsondata['vector_3'] = int(response1['vector_3'])
		jsondata.update({'node': 'node' + str(replica2+1)})
		response2 = send_request(request, replica2, nodeList[replica2], jsondata, fileContent)
		print("request 2 done")

		if response2['Exception']:
			response2 = send_request(request, replica1, nodeList[replica1], jsondata, fileContent)
			if "error" in response2:
				if "bucket" in response2["error"].lower():
					# create bucket
					send_request(temprequest, replica1, nodeList[replica1], jsondata, fileContent)
					# create file in that bucket
					response2 = send_request(request, replica1, nodeList[replica1],jsondata, fileContent)
		elif "error" in response2:
			if "bucket" in response2["error"].lower():
				# create bucket
				send_request(temprequest, replica2, nodeList[replica2], jsondata, fileContent)
				# create file in that bucket
				response1 = send_request(request, replica2, nodeList[replica2],jsondata, fileContent)


		response = {
			"response1" : response1,
			"response2" : response2
		}
		print("inside create file")
		print(response)
	except Exception as e:
		print(e)
		response = {
			"success" : False,
			"Exception" : e
		}
	return JsonResponse(response)

@csrf_exempt
def delete_file(request):
	try:
		jsondata = json.loads(json.dumps(request.POST))
		fileContent = request.FILES['fileContent'] if 'fileContent' in request.FILES else False
		# delete in all replicas
		replica1 = 0
		replica2 = 1

		jsondata.update({'node': 'node' + str(replica1+1)})
		response1 = send_request(request, replica1, nodeList[replica1],jsondata, False)
		print(response1)
		print("response1 fcking done")
		if response1['Exception']:
			print("shitty code")
			# handoff_manager(request, replica1, nodeList[(replica1 + 1)%3],jsondata, fileContent)
			response1 = send_request(request, replica2, nodeList[replica2], jsondata, False) # Temp

		jsondata.update({'node': 'node' + str(replica2+1)})
		print(jsondata)
		print("request 1 done")
		response2 = send_request(request, replica2, nodeList[replica2],jsondata, False)
		if response2['Exception']:
			print("shitty code 2")
			# handoff_manager(request, replica1, nodeList[(replica1 + 1)%3],jsondata, fileContent)
			response2 = send_request(request, replica1, nodeList[replica1], jsondata, False)

		response = {
			"response1" : response1,
			"response2" : response2
		}
	except Exception as e:
		print(e)
		response = {
			"success" : False,
			"Exception" : e
		}
	return JsonResponse(response)


@csrf_exempt
def update_file(request):
	try:
		jsondata = json.loads(json.dumps(request.POST))
		fileContent = request.FILES['fileContent'] if 'fileContent' in request.FILES else False
		replica1 = get_node_number(jsondata["bucketName"] + jsondata["fileName"])
		replica2 = (replica1 + 1)%3

		# ******************* For Testing *******************
		replica1 = 0
		replica2 = 1
		jsondata.update({'flag': 'wb'})
		# temprequest = copy(request)
		# temprequest.path = '/bucket/create_bucket/'

		jsondata.update({'node': 'node' + str(replica1+1)})
		response1 = send_request(request, replica1, nodeList[replica1], jsondata, fileContent)
		print("request 1 done")
		print(response1)

		if response1['Exception']:
			response1 = send_request(request, replica2, nodeList[replica2], jsondata, fileContent)
			if "error" in response1:
				if "bucket" in response1["error"].lower():
					# create bucket
					print("no update happens")
		elif "error" in response1:
			if "bucket" in response1["error"].lower():
				# create bucket
				print("no update happens")

		print("request 1 done")
		if 'vector_1' in response1:
			jsondata['vector_1'] = response1['vector_1']
			jsondata['vector_2'] = response1['vector_2'] + 1
			jsondata['vector_3'] = response1['vector_3']
		jsondata.update({'node': 'node' + str(replica2+1)})
		response2 = send_request(request, replica2, nodeList[replica2], jsondata, fileContent)
		print("request 2 done")

		if response2['Exception']:
			response2 = send_request(request, replica1, nodeList[replica1], jsondata, fileContent)
			if "error" in response2:
				if "bucket" in response2["error"].lower():
					# create bucket
					print("no update happens")
		elif "error" in response2:
			if "bucket" in response2["error"].lower():
				# create bucket
				print("no update happens")


		response = {
			"response1" : response1,
			"response2" : response2
		}
		print("inside create file")
		print(response)
	except Exception as e:
		print(e)
		response = {
			"success" : False,
			"Exception" : e
		}
	return JsonResponse(response)


@csrf_exempt
def gossip(request):

	# get_ip_list_from_json()
	print(nodeList)
	now = datetime.datetime.now()

	start_gossip(random.randint(1, 12), 0) #choose source node and select no of roounds
	print(responseCounts)
	deadnodes = [i+1 for i in range(len(responseCounts)) if responseCounts[i] < 20]
	response = {
		"Response Counts" : responseCounts,
		"List Of Dead Nodes" : ["node "+ str(deadnodes[i]) for i in range(len(deadnodes))]
	}
	return JsonResponse(response)

def send_request(request, nodeNumber, ipAddress, jsondata, fileContent):
	response = {}
	print("send_request " + ipAddress)
	try:

		# ******************* For Testing *******************
		# API_ENDPOINT = "http://192.168.56.102:8000" + request.path.replace("coordinator","bucket")
		API_ENDPOINT = ipAddress + request.path.replace("coordinator","bucket")
		files = {}
		if fileContent != False:
			files = {'fileContent': fileContent}

		api_response = requests.post(url = API_ENDPOINT, files = files, data = jsondata)

		# if api_response.status_code == '200':
		if status.is_success(api_response.status_code):
			print(api_response.text)
			response = json.loads(api_response.text)
			response.update({'Exception': False})
			print(type(response))
		else:
			print("else")
			print(api_response.status_code)
			response = {
				"success" : False,
				"Exception": False
				# "status_code" : api_response.status_code
			}
	except:
		print("except")
		response = {
			"success" : False,
			"error" : "An error occured at Node with ip" + ipAddress,
			"Exception" : True
		}
	return response
