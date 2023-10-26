#!/usr/bin/env python
import json

import requests
from requests.auth import HTTPBasicAuth

# send flows to the controller
def sendTables(contentType, dest):
    load_file = loadTable(dest)
    for element in load_file:
        url = element[1]
        xml = element[0]

        headers = {
            'Content-Type': 'application/{}'.format(contentType),
            'Accept': '*/*'
        }

        bias = 2 if contentType=='json' else 1

        for i in range(len(xml)):
            print xml[i]
            print(requests.put(
                url=url+str(i+bias),
                data=xml[i],
                headers=headers,
                auth=HTTPBasicAuth('admin', 'admin')
            ))

def loadTable(dest):
    with open(dest, 'r') as f:
        return json.load(f)


sendTables('xml', './tables1.json')
sendTables('json', './tables2.json')