import requests
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from rest_framework import status
from django.http import JsonResponse, HttpResponse

@csrf_exempt
def failback(request):
	response = {}
	try:
		with open('dynamo_env.json') as json_file:
			data = json.load(json_file)

		jsondata = json.loads(json.dumps(request.POST))

		fromNode = jsondata["fromNode"]
		toNode = jsondata["toNode"]

		API_ENDPOINT = data[toNode] + "/bucket/node_up/"
		api_response = requests.post(url = API_ENDPOINT)

		if status.is_success(api_response.status_code):
			# send api request
			API_ENDPOINT = data[fromNode] + "/bucket/handoff_node/"
			request = {
				'flag' : 1
			}
			api_response = requests.post(url = API_ENDPOINT, data = request)
			response = json.loads(api_response.text)
		else:
			response = {
				"success" : False,
				"error" : toNode + " did not respond"
			}
		
	except Exception as e:
		response = {
			"success" : False,
			"error" : "An error occured",
			"Exception" : e
		}

	return JsonResponse(response)

@csrf_exempt
def handoff_node(request):
	response = {}
	try:
		with open('dynamo_env.json') as json_file:
			data = json.load(json_file)
		jsondata = json.loads(json.dumps(request.POST))
		# print(jsondata)
		API_ENDPOINT = data[jsondata["nodeNumber"]] + "/bucket/handoff_node/"
		resrec = requests.post(url = API_ENDPOINT)
		# Add response
		response = json.loads(resrec.text)
	except Exception as e:
		response = {
			"success" : False,
			"error" : "An error occured",
			"Exception" : e
		}
	return JsonResponse(response)

