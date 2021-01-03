from django.shortcuts import render
from django.core.cache import cache
import os, json, imp, shutil
from dynamo import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import datetime
from .models import Bucket, File
import dynamo.settings
import delegator
from .handoff import handler
from .node_is_alive import is_alive

@csrf_exempt
def create_db_backup(request):
	database_name = request.POST['node']

	response = delegator.run('PGPASSWORD={} pg_dump -h localhost -U {} {} > {}.sql'.format(database_name,database_name,database_name, database_name))

	return HttpResponse("backup taken completed successfully")

@csrf_exempt
def restore_db(request):
	database_name = request.POST['node']

	response = delegator.run('PGPASSWORD={} psql -h localhost -U {} {} < {}.sql'.format(database_name,database_name,database_name, database_name))

	print(response)

	return HttpResponse("db restored")

@csrf_exempt
def handoff_node(request):
    # Tell Python to run the handler() function when SIGINT is recieved
    if request.method == 'POST':
        flag=1
        handler(flag)
        response = {
        'success' : True
        }
    return JsonResponse(response)

@csrf_exempt
def node_up(request):
    if request.method == 'POST':
        if is_alive():
            response = {
            'success' : True
            }
        else:
            response = {
            'success' : False 
            }
    return JsonResponse(response)
