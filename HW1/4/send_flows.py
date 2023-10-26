#!/usr/bin/env python
import json

import requests
from requests.auth import HTTPBasicAuth


CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = '8181'


def create_url(br_id, flow_id, table_id=0):
    url = 'http://' + CONTROLLER_IP + ':' + CONTROLLER_PORT + '/restconf/config/opendaylight-inventory:nodes/node/openflow:{}/table/{}/flow/{}'.format(
        br_id, table_id, flow_id
    )
    return url

def loadTable(dest):
    with open(dest, 'r') as f:
        return json.load(f)

def sendTables(dest):
    load_file = loadTable(dest)
    for flow in load_file:
        send_flow(flow)




def send_flow(flow):
    headers = {
        'Content-Type': 'application/{}'.format(flow['type']),
        'Accept': '*/*'
    }
    print(requests.put(
        url=create_url(flow['br_id'], flow['flow_id'], flow['table_id']),
        data=flow['flow'],
        headers=headers,
        auth=HTTPBasicAuth('admin', 'admin')
    ))

def del_flow(br_id, flow_id):
    headers = {
        'Accept': '*/*'
    }
    url = create_url(br_id=br_id, flow_id=flow_id)

    print(requests.delete(
        url=url,
        headers=headers,
        auth=HTTPBasicAuth('admin', 'admin')
    ))


# send list of flows
sendTables('./flows.json')
