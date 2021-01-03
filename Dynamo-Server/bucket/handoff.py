import signal
import os, json
from sys import exit
from dynamo import settings
import delegator
import requests

filepath = settings.BASE_DIR + "/dynamo_env.json"
with open(filepath) as json_file:
	data = json.load(json_file)
file_name = ''
ip_add = ''

def handler(flag):
    """
    flag: 0 or 1
    0: backup is taken of current node
    1: backup is taken of node which needs to be restored
    """
    # Handle any cleanup here    
    if flag == 0: 
    	filepath = settings.MEDIA_ROOT + "/" + data["handoff_name"]
    	file_name = data["handoff_name"]
    	ip_add = data["handoff_ip"]
    else:
    	filepath = settings.MEDIA_ROOT + "/" + (data["send_back_name"])
    	file_name = data["send_back_name"]
    	ip_add = data["send_back_ip"]

    cmd1 = 'tar -zcvf '+ file_name + '.tar.gz ' + filepath
    cmd2 = 'scp ' + file_name + '.tar.gz ' + ip_add + ':/' + settings.MEDIA_ROOT 

    # copyig database dump
    database_name = file_name
    delegator.run('PGPASSWORD={} pg_dump -h localhost -U {} {} > {}.sql'.format(database_name,database_name,database_name, database_name))
        
    cmd3 = 'scp ' + file_name + '.sql ' + ip_add + ':/' + settings.MEDIA_ROOT

    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)
    print('File transfered suceesfully')
    send_signal(requests, flag)
    #cmd1='tar -zcvf /home/abhayrajj/dynamoDb/test.tar.gz /home/abhayrajj/dynamoDb/tohandoff'
    #cmd2='scp /home/abhayrajj/dynamoDb/test.tar.gz abhayrajj@192.168.56.102:/home/abhayrajj/dynamoDb/recvhandoff'

    # ByPass password to transfer files https://www.youtube.com/watch?v=Uq5xp6gh_FA  
    #transfer files: 

    #convert directory to tar:


    print('SIGINT or CTRL-C detected. Exiting gracefully')
    cmd3 = 'cd '+ filepath
    cmd4 = 'rm '+ file_name+'.tar.gz '
    cmd5 = 'rm ' + file_name + '.sql'
    os.system(cmd3)
    os.system(cmd4)
    os.system(cmd5)

def send_signal(requests, flag):
    if flag == 0:
        ip_add = data["handoff_ip_port"]
    else:
        ip_add = data["send_back_ip_port"]

    API_ENDPOINT = "http://" + ip_add + "/bucket/untar_file/"
    if flag == 0:
        jsondata ={
    	   "failBack" : False
        }
    else:
        jsondata ={
           "failBack" : True
        }

    print(API_ENDPOINT)
    resrec = requests.post(url=API_ENDPOINT, data = jsondata)
    print(resrec)