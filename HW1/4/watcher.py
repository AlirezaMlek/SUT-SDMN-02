#!/usr/bin/env python
import json

import create_flows as cf
import send_flows as sf
import create_net as cn
import spf
import time
import os
import copy


# caching previous
cache_graph = cf.load_graph()
cache_spf = cf.load_spf()
cache_flows = sf.loadTable('./flows.json')

# ports info
port_info = cf.load_info()

# number of switches
l = len(cache_graph)

# interval between loops
interval = 1

# names of nodes
names = ['r1', 's2', 's3', 'r4']


num_flows = [0 for _ in range(l)]
for rec in cache_flows:
    i = int(rec['br_id']) - 1
    num_flows[i] = num_flows[i]+1

active_ports = [[] for i in range(l)]
num_ports = [0 for _ in range(l)]
for rec in port_info['ports']:
    i = int(rec['name'][-1]) - 1
    num_flows[i] = num_flows[i]+1
    active_ports[i].append(rec['port'])


# up/down ports
def change_port_mod(br_id, port_id):
    for i in range(len(port_info['ports'])):
        r = port_info['ports'][i]
        if r['br_id']==br_id and r['id']==port_id:
            port_info['ports'].pop(i)

    with open('./flows.json') as f:
        json.dump(port_info,f)


def modify_rec(flow, _type, id):
    if _type=='json':
        flowJ = json.loads(flow)
        flowJ["flow"][0]['id'] = str(id)
        return json.dumps(flowJ)

    else:
        ind1 = flow.find('<id>')
        ind2 = flow.find('</id>')
        return flow[:ind1+4] + str(id) + flow[ind2:]


# up/down/create links
def update_link(br1, br2):

    port1 = '{}-eth{}'.format(br1, br2[-1])
    port2 = '{}-eth{}x'.format(br1, br2[-1])

    for rec in port_info['ports']:
        if rec['port']==port1 or rec['port']==port2:
            os.system('sh ifconfig {} up'.format(rec['port']))
            change_port_mod(br_id=rec['port'], port_id=rec['id'])
            return


    # both of bridges are not router
    if br1 in [1,l] and br2 in [1,l]:
        os.system('ovs-vsctl \
        -- add-port {} {} vlan_mode=trunk\
        -- set interface {} type=patch options:peer={} options:remote_ip=10.0.3.{}\
        -- add-port {} {} vlan_mode=trunk\
        -- set interface {} type=patch options:peer={} options:remote_ip=10.0.3.{}'.format(br1, port1, port1, port2,
                                                                                           br1, br2, port2, port2, port1, br2))

    # both of bridges are router
    else:
        os.system('ovs-vsctl \
            -- add-port {} {} vlan_mode=trunk\
            -- add-port {} {} vlan_mode=trunk'.format(br1, port1, br2, port2))

        pfx1 = 2 if br2==l else 1
        pfx2 = 2 if br1==l else 1

        os.system('ovs-vsctl \
        -- set interface {} type=patch options:peer={} options:remote_ip=10.0.3.{}\
        -- set interface {} type=patch options:peer=r1-eth4 options:remote_ip=10.0.3.{}'.format(port1, port2, pfx1,
                                                                                                     port2, port1, pfx2))

        os.system('ifconfig {} 10.0.3.{} up'.format(br1, pfx1))
        os.system('ifconfig {} 10.0.3.{} up'.format(br2, pfx2))


    # increase number of ports for the bridges
    num_ports[int(br1)] = num_ports[int(br1)]+1
    num_ports[int(br1)] = num_ports[int(br1)]+1

    port_info['ports'].append(cn.networkInfo(num_ports[int(br1)], names[int(br1)], port1))
    port_info['ports'].append(cn.networkInfo(num_ports[int(br2)], names[int(br2)], port2))





while True:
    # sleep between each interation
    time.sleep(interval)

    current_graph = cf.load_graph()

    # bypass operation
    if current_graph == cache_graph:
        continue


    print('Topology is changed')

    # update links
    for i in range(l):
        for j in range(l):
            if current_graph[i][j]==0 and cache_graph[i][j]!=0:
                update_link(names[i], names[j])

            elif current_graph[i][j]!=0 and cache_graph[i][j]==0:
                for p in port_info['ports']:
                    if p['port'][1]==str(i+1) and (p['port'][-1]==str(i+1) or p['port'][-2]==str(i+1)):
                        os.system('sh ifconfig {} down'.format(p['port']))
                        change_port_mod(br_id=p['port'], port_id=p['id'])



    # calculate new path
    current_spf = spf.shortestPath(current_graph)

    # delete redundant flows
    current_flows = cf.run()
    for rec in cache_flows:
        if rec not in current_flows:
            sf.del_flow(rec['br_id'], rec['flow_id'])

    # add newly added flows
    for rec in current_flows:
        if rec not in cache_flows:
            i = int(rec['br_id']) - 1
            num_flows[i] = num_flows[i] + 1
            rec['flow_id'] = str(num_flows[i])
            rec['flow'] = modify_rec(rec['flow'], rec['type'], num_flows[i])
            sf.send_flow(rec)

    # update cache
    cache_graph = copy.copy(current_graph)
    cache_spf = copy.copy(current_spf)
    cache_flows = copy.copy(current_flows)
