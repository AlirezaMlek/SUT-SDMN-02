#!/usr/bin/env python
import json

import requests
from requests.auth import HTTPBasicAuth


CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = '8181'

def create_url(flow):
    url = 'http://' + CONTROLLER_IP + ':' + CONTROLLER_PORT + '/restconf/config/opendaylight-inventory:nodes/node/openflow:{}/table/{}/flow/{}'.format(
        flow['br_id'],
        flow['table_id'],
        flow['flow_id']
    )
    return url

def loadTable(dest):
    with open(dest, 'r') as f:
        return json.load(f)

def sendTables(dest):
    load_file = loadTable(dest)
    for flow in load_file:

        headers = {
            'Content-Type': 'application/{}'.format(flow['type']),
            'Accept': '*/*'
        }

        print(requests.put(
            url= create_url(flow),
            data= flow['flow'],
            headers=headers,
            auth=HTTPBasicAuth('admin', 'admin')
        ))




sendTables('./flows.json')
