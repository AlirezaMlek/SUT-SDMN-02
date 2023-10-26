#!/usr/bin/env python

import json

H1_IP = '10.0.1.1/32'
H1_MAC = '00:00:00:00:00:01'
H2_IP = '10.0.2.1/32'
H2_MAC = '00:00:00:00:00:02'
R1_MAC = "00:00:00:00:01:00"
R2_MAC = "00:00:00:00:02:00"

def l2MatchingFlow(br_id, table_id, flow_id, in_port, dl_dst, out_port):
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
    <id>{}</id>
    <priority>65535</priority>
    <table_id>{}</table_id>
    <match>
        <in-port>{}</in-port>
        <ethernet-match>
            <ethernet-destination>
                <address>{}</address>
            </ethernet-destination>
        </ethernet-match>
    </match>
    <idle-timeout>1000</idle-timeout>
    <cookie>0</cookie>
    <flags></flags>
    <hard-timeout>0</hard-timeout>
    <instructions>
        <instruction>
            <order>0</order>
            <apply-actions>
                <action>
                    <order>0</order>
                    <output-action>
                        <output-node-connector>{}</output-node-connector>
                        <max-length>0</max-length>
                    </output-action>
                </action>
            </apply-actions>
        </instruction>
    </instructions>
</flow>""".format(flow_id, table_id, in_port, dl_dst, out_port)

    return {'br_id': br_id, 'flow': xml, 'type': 'xml', 'table_id': table_id, "flow_id": flow_id}


def l3MatchingFlow(br_id, table_id, flow_id, in_port, nw_dst, nw_src, out_port, dl_dst):
    xml = """{
    "flow": [
        {
            "id": "%(flow_id)s",
            "table_id": "%(table_id)s",
            "match": {
                "ethernet-match": {
                    "ethernet-type": {
                        "type": "0x0800"
                    }
                },
                "ipv4-destination": "%(nw_dst)s",
                "ipv4-source": "%(nw_src)s",
                "in-port": %(in_port)d,
                "ip-match": {
                    "ip-protocol": "1"
                }
            },
            "instructions": {
                "instruction": [
                    {
                        "order": "0",
                        "apply-actions": {
                            "action": [
                                {
                                    "order": "0",
                                    "set-dl-dst-action": {
                                        "address": "%(dl_dst)s"
                                    }
                                },
                                {
                                    "order": "1",
                                    "output-action": {
                                        "output-node-connector": "%(out_port)d",
                                        "max-length": "65535"
                                    }
                                }
                            ]
                        }
                    }
                ]
            },
            "priority": "65535"
        }
    ]
}""" % {"flow_id": flow_id, "table_id": table_id, "nw_dst": nw_dst, "nw_src": nw_src, "in_port": in_port,
        "dl_dst": dl_dst, "out_port": out_port}

    return {'br_id': br_id, 'flow': xml, 'type': 'json', 'table_id': table_id, "flow_id": flow_id}





def arpFlow(br_id, table_id, flow_id, in_port, output):
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
    <id>{}</id>
    <priority>65535</priority>
    <table_id>{}</table_id>
    <match>
        <ethernet-match>
            <ethernet-type>
                <type>2054</type>
            </ethernet-type>
        </ethernet-match>
        <in-port>{}</in-port>
    </match>
    <idle-timeout>1000</idle-timeout>
    <cookie>0</cookie>
    <flags></flags>
    <hard-timeout>0</hard-timeout>
    <instructions>
        <instruction>
            <order>0</order>
            <apply-actions>
                <action>
                    <order>0</order>
                    <output-action>
                        <output-node-connector>{}</output-node-connector>
                        <max-length>60</max-length>
                    </output-action>
                </action>
            </apply-actions>
        </instruction>
    </instructions>
</flow>""".format(flow_id, table_id, in_port, output)

    return {'br_id': br_id, 'flow': xml, 'type': 'xml', 'table_id': table_id, "flow_id": flow_id}

def dropFlow(br_id, flow_id, table_id, in_port):
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <flow xmlns="urn:opendaylight:flow:inventory">
        <id>{}</id>
        <priority>1</priority>
        <table_id>{}</table_id>
        <match>
            <in-port>{}</in-port>
        </match>
        <idle-timeout>1000</idle-timeout>
        <cookie>0</cookie>
        <flags></flags>
        <hard-timeout>0</hard-timeout>
        <instructions>
            <instruction>
                <order>0</order>
                <apply-actions>
                </apply-actions>
            </instruction>
        </instructions>
    </flow>""".format(flow_id, table_id, in_port)

    return {'br_id': br_id, 'flow': xml, 'type': 'xml', 'table_id': table_id, "flow_id": flow_id}

def load_graph():
    g=[]
    with open('./graph.json', 'r') as f:
        gJ = json.load(f)
        for i in range(len(gJ)):
            g.append(gJ[str(i)])
    return g

def load_spf():
    with open('./spf.json', 'r') as f:
        return json.load(f)
def load_info():
    with open('./info.json', 'r') as f:
        return json.load(f)

def find_port_num(info, name):
    for rec in info['ports']:
        if rec['port']==name:
            return rec['id']
    print('err')

def find_br_id(names, br_name):
    for i in range(len(names)):
        if br_name==names[i]: return i+1


def run():
    g = load_graph()
    l = len(g)

    names = []
    for i in range(l):
        if i==0 or i==l-1:
            names.append('r'+str(i+1))
        else:
            names.append('s'+str(i+1))

    flow_list = []
    flow_id_counter = [1 for _ in range(l)]

    paths = load_spf()
    info = load_info()

    p = [paths['1'][str(l)], paths[str(l)]['1']]

    ############################## router ---> host

    port_name_out = names[0]+'-ethe'
    num_out = find_port_num(info, port_name_out)
    port_name_in = '{}-eth{}x'.format(names[0], p[1][-2])
    num_in = find_port_num(info, port_name_in)
    flow_list.append(l3MatchingFlow(br_id='1', table_id=0, flow_id=flow_id_counter[0], in_port=num_in,
                                    nw_src=H2_IP, nw_dst=H1_IP, out_port=num_out, dl_dst=H1_MAC))
    flow_id_counter[0] = flow_id_counter[0] + 1

    port_name_out = names[-1] + '-ethe'
    num_out = find_port_num(info, port_name_out)
    port_name_in = '{}-eth{}x'.format(names[-1], p[0][-2])
    num_in = find_port_num(info, port_name_in)
    flow_list.append(l3MatchingFlow(br_id=str(l), table_id=0, flow_id=flow_id_counter[l - 1], in_port=num_in,
                                    nw_src=H1_IP, nw_dst=H2_IP, out_port=num_out, dl_dst=H2_MAC))
    flow_id_counter[l-1] = flow_id_counter[l-1] + 1

    ############################## host ---> router

    port_name_in = names[0] + '-ethe'
    num_in = find_port_num(info, port_name_in)
    port_name_out = '{}-eth{}'.format(names[0], p[0][1])
    num_out = find_port_num(info, port_name_out)
    flow_list.append(l3MatchingFlow(br_id='1', table_id=0, flow_id=flow_id_counter[0], in_port=num_in,
                                    nw_src=H1_IP, nw_dst=H2_IP, out_port=num_out, dl_dst=R2_MAC))
    flow_id_counter[0] = flow_id_counter[0] + 1

    port_name_in = names[-1] + '-ethe'
    num_in = find_port_num(info, port_name_in)
    port_name_out = '{}-eth{}'.format(names[-1], p[1][1])
    num_out = find_port_num(info, port_name_out)
    flow_list.append(l3MatchingFlow(br_id=str(l), table_id=0, flow_id=flow_id_counter[l - 1], in_port=num_in,
                                    nw_src=H2_IP, nw_dst=H1_IP, out_port=num_out, dl_dst=R1_MAC))
    flow_id_counter[l - 1] = flow_id_counter[l - 1] + 1



    ############################## v-switch ---> v-switch

    macs = [R2_MAC, R1_MAC]

    for k in range(2):
        path = p[k]
        for i in range(1, len(path)-1):
            port_name_out = 's{}-eth{}'.format(path[i], path[i+1])
            num_out = find_port_num(info, port_name_out)
            port_name_in = 's{}-eth{}x'.format(path[i], path[i-1])
            num_in = find_port_num(info, port_name_in)
            flow_list.append(l2MatchingFlow(br_id=path[i], table_id=0, flow_id=flow_id_counter[path[i] - 1], in_port=num_in,
                                            dl_dst=macs[k], out_port=num_out))

            flow_id_counter[path[i] - 1] = flow_id_counter[path[i]-1] + 1



    ############################## ARPs

    for k in range(2):
        path = p[k]
        for i in range(1, len(path)-1):
            port_name_out = 's{}-eth{}'.format(path[i], path[i + 1])
            num_out = find_port_num(info, port_name_out)
            port_name_in = 's{}-eth{}x'.format(path[i], path[i - 1])
            num_in = find_port_num(info, port_name_in)

            flow_list.append(arpFlow(br_id=path[i], table_id=0, flow_id=flow_id_counter[path[i] - 1], in_port=num_in,
                                     output=num_out))

            flow_id_counter[path[i] - 1] = flow_id_counter[path[i]-1] + 1




        num_in = find_port_num(info, 'r1-ethe')
        flow_list.append(arpFlow(br_id=1, table_id=0, flow_id=flow_id_counter[0], in_port=num_in,
                                 output='FLOOD'))
        flow_id_counter[0] = flow_id_counter[0] + 1

        num_in = find_port_num(info, 'r4-ethe')
        flow_list.append(arpFlow(br_id=l, table_id=0, flow_id=flow_id_counter[l-1], in_port=num_in,
                                 output='FLOOD'))
        flow_id_counter[l-1] = flow_id_counter[l-1] + 1

        for rec in info['ports']:
            if rec['port'][-1]=='x' and rec['port'][0]=='r':
                br_id = 1 if rec['port'][1]=='1' else l
                num_out = find_port_num(info, 'r{}-ethe'.format(br_id))
                flow_list.append(arpFlow(br_id=br_id, table_id=0, flow_id=flow_id_counter[br_id - 1], in_port=rec['id'],
                                         output=num_out))
                flow_id_counter[br_id - 1] = flow_id_counter[br_id - 1] + 1

    ############################## DROPs

    for rec in info['ports']:
        if rec['port'][-1] not in ['x','e']:
            if rec['mod']=='up':
                br_id = find_br_id(names, rec['name'])
                flow_list.append(dropFlow(br_id=br_id, flow_id=flow_id_counter[br_id- 1], table_id=0, in_port=rec['id']))
                flow_id_counter[br_id - 1] = flow_id_counter[br_id - 1] + 1

    with open('./flows.json', 'w') as f:
        json.dump(flow_list, f)

    return flow_list



run()
