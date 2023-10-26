#!/usr/bin/env python

import json
import os

with open('./info.json', 'r') as f:
    info = json.load(f)

visited=[]

# links up
for rec in info['ports']:
    print(rec)
    if rec['name'][0] == 'r' and rec['ip'] != None:
        if rec['mode'] == 'trunk':
            os.system('ovs-vsctl add-port {} {} vlan_mode={}'.format(rec['name'], rec['port'], rec['mode']))
        else:
            os.system('ovs-vsctl add-port {} {}'.format(rec['name'], rec['port']))

        os.system('ifconfig {} {} up'.format(rec['name'], rec['ip']))


# interfaces up
for rec in info['macs']:
    os.system('ovs-vsctl set bridge {} other-config:hwaddr={}'.format(rec['name'], rec['mac']))

# delete initial flows
for rec in info['ports']:
    name = rec['name']
    if name not in visited:
        os.system('ovs-ofctl --protocol OpenFlow13 del-flows {}'.format(name))
        visited.append(name)
