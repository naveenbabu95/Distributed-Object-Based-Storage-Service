from django.shortcuts import render
from django.core.cache import cache
import os, json, imp, shutil, signal
from dynamo import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import datetime
from .models import Bucket, File
import dynamo.settings
from sendfile import sendfile
from copy import copy

@csrf_exempt
def create_bucket(request):
    """
    checks whether bucket is already present, if yes returns false.
    if bucket is not present, first creates database entry and on success bucket is created.
    """
    if request.method == 'POST':
        bucketName = request.POST['bucketName']
        node = request.POST['node']
        if node != settings.NODE_NUMBER:
            database = 'nodedown'
        else:
            database = 'default'
        path =settings.MEDIA_ROOT + '//'+ node+ '//'+ bucketName
        try:
            bucket_instance = Bucket.objects.using(database).get(name=bucketName)
            response = {
            'success': False,
            'error': 'Bucket {} already exists.'.format(bucketName),
            'node': node
            }
        except:
            bucket_obj = Bucket.objects.create(
                name= bucketName,
                node_id= node)
            try:
                bucket_obj.save(using=database)
                if not os.path.exists(path):
                    os.makedirs(path)
                response = {
                'success' : True,
                'message' : 'Bucket {} created successfully!'.format(bucketName),
                'node' : node
                }
            except Exception as e:
                print(e)
                response = {
                'success' : False,
                'error': 'Bucket cannot be created',
                'node': node
                }

    return JsonResponse(response)

@csrf_exempt
def delete_bucket(request):
    """
    checks whether request bucket exists, if yes it is deleted and also db entry is removed.
    if bucket is not found it returns false.
    """
    if request.method == 'POST':
        bucketName = request.POST['bucketName']
        node = request.POST['node']
        if node != settings.NODE_NUMBER:
            database = 'nodedown'
        else:
            database = 'default'
        path =settings.MEDIA_ROOT + '//'+ node+ '//'+bucketName
        try:
            bucket_instance = Bucket.objects.using(database).get(name=bucketName)
            try:
                bucket_instance.delete(using=database)
                shutil.rmtree(path)
                response = {
                'success' : True,
                'message' : 'Bucket {} deleted successfully!'.format(bucketName),
                'node' : node
                }
            except:
                response = {
                'success' : False,
                'error': 'Bucket {} cannot be deleted.'.format(bucketName),
                'node': node
                }
        except:
            response = {
            'success' : False,
            'error': 'Bucket not found!',
            'node': node
            }

    return JsonResponse(response)


@csrf_exempt
def create_file(request):
    if request.method == 'POST':
        bucketName = request.POST['bucketName']
        fileName = request.POST['fileName']
        fileContent = request.FILES['fileContent']
        vector_1 = request.POST['vector_1']
        vector_2 = request.POST['vector_2']
        vector_3 = request.POST['vector_3']
        node = request.POST['node']
        if node != settings.NODE_NUMBER:
            database = 'nodedown'
        else:
            database = 'default'

        try:
            bucket_obj = Bucket.objects.using(database).get(name=bucketName)

            file_obj = File.objects.using(database).filter(bucket_id=bucket_obj, file_name= fileName)
            file_obj2 = file_obj.values_list('file_name', flat=True)

            if file_obj2:
                response = {
                'success' : False,
                'error' : 'File already exists!',
                'node' : node,
                'vector_1': file_obj[0].vector_1,
                'vector_2': file_obj[0].vector_2,
                'vector_3': file_obj[0].vector_3
                }
            else:
                file_obj = File.objects.create(
                    bucket_id= bucket_obj,
                    file_name= fileName,
                    file=fileContent,
                    vector_1= vector_1,
                    vector_2= vector_2,
                    vector_3= vector_3,
                    )
                try:
                    file_obj.save(using=database)
                    response = {
                    'success' : True,
                    'message' : 'File {} uploaded to {} successfully!'.format(fileName, bucketName),
                    'node' : node,
                    'vector_1': vector_1,
                    'vector_2' : vector_2,
                    'vector_3' : vector_3
                    }
                except:
                    response = {
                    'success' : False,
                    'error' : 'File could not be uploaded',
                    'node' : node
                    }
        except Exception as e:
            print(e)
            response = {
            'success' : False,
            'error' : 'Bucket not found.',
            'node' : node
            }

    return JsonResponse(response)

@csrf_exempt
def update_file(request):
    if request.method == 'POST':
        bucketName = request.POST['bucketName']
        fileName = request.POST['fileName']

        fileContent = request.FILES['fileContent']
        flag = request.POST['flag']
        vector_1 = int(request.POST['vector_1'])
        vector_2 = int(request.POST['vector_2'])
        vector_3 = int(request.POST['vector_3'])
        node = request.POST['node']
        if node != settings.NODE_NUMBER:
            database = 'nodedown'
        else:
            database = 'default'
        try:
            bucket_obj = Bucket.objects.using(database).get(name=bucketName)

            file_list = File.objects.using(database).filter(bucket_id=bucket_obj, file_name= fileName)
            if flag == 'rb':
                if vector_1 < file_list[0].vector_1:
                    vector_1 = file_list[0].vector_1
                    
                if vector_2 < file_list[0].vector_2:
                    vector_2 = file_list[0].vector_2

                if vector_3 < file_list[0].vector_2:
                    vector_3 = file_list[0].vector_3
            else:
                vector_1 = file_list[0].vector_1 + vector_1
                vector_2 = file_list[0].vector_2 + vector_2
                vector_3 = file_list[0].vector_3 + vector_3

            file_obj = File.objects.create(
                bucket_id= bucket_obj,
                file_name= fileName,
                file=fileContent,
                vector_1= vector_1,
                vector_2= vector_2,
                vector_3= vector_3
                )
            try:
                file_obj.save(using=database)
                try:
                    old_file_obj = File.objects.get(id=file_list[1].id)
                    print(file_list)
                    filepath =settings.MEDIA_ROOT + '//' + str(old_file_obj.file)
                    old_file_obj.delete()

                    os.remove(filepath)
                except:
                    print('File {} didnt exist'.format(fileName))

                print(file_obj.file_name)
                response = {
                'success' : True,
                'message' : 'File {} updated to {} successfully!'.format(fileName, bucketName),
                'node' : node,
                'vector_1': vector_1,
                'vector_2': vector_2,
                'vector_3': vector_3
                }
            except:
                response = {
                'success' : False,
                'error' : 'File could not be updated',
                'node' : node
                }
        except Exception as e:
            print(e)
            response = {
            'success' : False,
            'error' : 'Bucket not found.',
            'node' : node
            }

    return JsonResponse(response)

@csrf_exempt
def delete_file(request):
    if request.method == 'POST':
        bucketName = request.POST['bucketName']
        fileName = request.POST['fileName']
        node = request.POST['node']
        if node != settings.NODE_NUMBER:
            database = 'nodedown'
        else:
            database = 'default'
        filepath =settings.MEDIA_ROOT + '//'

        try:
            bucket_obj = Bucket.objects.using(database).get(name=bucketName)

            file_list = File.objects.using(database).filter(bucket_id=bucket_obj, file_name= fileName)
            old_file_obj = File.objects.using(database).get(id=file_list[0].id)
            file_obj = file_list.values_list('file_name', flat=True)
            try:
                filepath =settings.MEDIA_ROOT + '//' + str(old_file_obj.file)
                old_file_obj.delete(using=database)

                os.remove(filepath)
                response = {
                'success' : True,
                'message' : 'File deleted successfully!',
                'node' : node
                }
            except:
                response = {
                'success' : False,
                'error' : 'File does not exists',
                'node' : node
                }
        except:
            response = {
            'success' : False,
            'error' : 'Bucket not found.',
            'node' : node
            }

    return JsonResponse(response)

@csrf_exempt
def read_file(request):
    if request.method == 'POST':
        bucketName = request.POST['bucketName']
        fileName = request.POST['fileName']
        node = request.POST['node']
        if node != settings.NODE_NUMBER:
            database = 'nodedown'
        else:
            database = 'default'
        try:
            bucket_obj = Bucket.objects.using(database).get(name=bucketName)

            file_obj = File.objects.using(database).filter(bucket_id=bucket_obj, file_name= fileName)[0]
            filepath =settings.MEDIA_ROOT + '//' + str(file_obj.file)
            try:
                print(file_obj)
                print(request.POST)
                response = {
                'success' : True,
                'filename' : fileName,
                'node' : node,
                'vector_1': file_obj.vector_1,
                'vector_2': file_obj.vector_2,
                'vector_3': file_obj.vector_3
                }
            except:
                response = {
                'success' : False,
                'error' : 'File does not exists',
                'node' : node
                }
        except:
            response = {
            'success' : False,
            'error' : 'Bucket not found.',
            'node' : node
            }
    return JsonResponse(response)

@csrf_exempt
def get_file(request):
    bucketName = request.POST['bucketName']
    fileName = request.POST['fileName']
    node = request.POST['node']
    if node != settings.NODE_NUMBER:
        database = 'nodedown'
    else:
        database = 'default'
    bucket_obj = Bucket.objects.using(database).get(name=bucketName)

    file_obj = File.objects.using(database).filter(bucket_id=bucket_obj, file_name= fileName)[0]
    filepath =settings.MEDIA_ROOT + '//' + str(file_obj.file)

    return sendfile(request, filepath, attachment=True, mimetype='application/pdf') 
