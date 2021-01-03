from .utils import *
import random
import requests
from rest_framework import status

responseCounts = [0]*3

def start_gossip(nodeNumber, noOfRounds):
    if noOfRounds == 3:
        return
    noOfRounds += 1
    count = 1
    while count <= 4:
        while True:
            newNodeNumber = random.randint(1,12)
            if nodeNumber != newNodeNumber:
                break
        count += 1
        print(responseCounts)
        print("Round " + str(noOfRounds))
        print("Virtual node number " + str(newNodeNumber))
        print("VM no " + nodeList[int((newNodeNumber-1)/4)])
        # responseCounts[int((newNodeNumber-1)/4)] += 1
        response = send_gossip_request((newNodeNumber-1)/4)
        if not response['Exception']:
            responseCounts[int((newNodeNumber-1)/4)] += 1
        start_gossip(newNodeNumber, noOfRounds)

def send_gossip_request(nodeNumber):
    response = {}
    try:
        API_ENDPOINT = nodeList[int(nodeNumber)] + "/gossip_message/"
        jsondata = {'node_number': nodeNumber}
        api_response = requests.post(url = API_ENDPOINT, data = jsondata)
        response = json.loads(api_response.text)
        response.update({'Exception': False})
    except:
        response = {
            "success" : False,
            "error" : "An error occured at Node " + str(nodeNumber),
            "Exception" : True
        }
    return response
    
