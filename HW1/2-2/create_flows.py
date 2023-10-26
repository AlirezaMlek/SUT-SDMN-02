#!/usr/bin/env python

import json

H1_IP = '10.0.1.1/32'
H1_MAC = '00:00:00:00:00:01'
H2_IP = '10.0.2.1/32'
H2_MAC = '00:00:00:00:00:02'
CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = '8181'
R0_MAC = "00:00:00:00:01:00"
R0_IP = "10.0.1.10/32"
BROADCAST = "ff:ff:ff:ff:ff:ff"

# matching in layer 2
def l2MatchingFlow(table_id, flow_id, in_port, dl_dst, out_port):
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

    return xml


# matching in layer 3
def l3MatchingFlow(table_id, flow_id, in_port, nw_dst, nw_src, out_port, dl_dst):
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

    return xml




# create arp flows
def arpFlow(table_id, flow_id, out_type):
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
</flow>""".format(flow_id, table_id, out_type)

    return xml



# create tables
def makeTables(switch_id, table_id, flows):
    url = 'http://' + CONTROLLER_IP + ':' + CONTROLLER_PORT + '/restconf/config/opendaylight-inventory:nodes/node/openflow:{}/table/{}/flow/'.format(
        switch_id,
        table_id
    )
    return (flows , url)


# create flows for bridges
def run():
    n = 3
    ovs_ids = [1, 2, 256]
    flow_list = [[] for _ in range(n+1)]
    flow_id_counter = [1 for _ in range(n)]

    ################################################################# S1 flows

    # forward packet to host
    flow_list[0].append(l2MatchingFlow(
        table_id=0,
        in_port=1,
        flow_id=flow_id_counter[0],
        dl_dst=H1_MAC,
        out_port=2
    ))
    flow_id_counter[0] = flow_id_counter[0] + 1

    # forward packet to router
    flow_list[0].append(l2MatchingFlow(
        table_id=0,
        in_port=2,
        flow_id=flow_id_counter[0],
        dl_dst=R0_MAC,
        out_port=1
    ))
    flow_id_counter[0] = flow_id_counter[0] + 1

    # flood action for arp
    flow_list[0].append(arpFlow(
        table_id=0,
        flow_id=flow_id_counter[0],
        out_type="FLOOD"
    ))
    flow_id_counter[0] = flow_id_counter[0] + 1

    ################################################################# S2 flows

    # forward packet to host
    flow_list[1].append(l2MatchingFlow(
        table_id=0,
        in_port=1,
        flow_id=flow_id_counter[1],
        dl_dst=H2_MAC,
        out_port=2
    ))
    flow_id_counter[1] = flow_id_counter[1] + 1

    # forward packet to router
    flow_list[1].append(l2MatchingFlow(
        table_id=0,
        in_port=2,
        flow_id=flow_id_counter[1],
        dl_dst=R0_MAC,
        out_port=1
    ))
    flow_id_counter[1] = flow_id_counter[1] + 1

    # flood action for arp
    flow_list[1].append(arpFlow(
        table_id=0,
        flow_id=flow_id_counter[1],
        out_type="FLOOD"
    ))
    flow_id_counter[1] = flow_id_counter[1] + 1

    ################################################################# R0 flows

    # flood action for arp
    flow_list[2].append(arpFlow(
        table_id=0,
        flow_id=flow_id_counter[2],
        out_type="FLOOD"
    ))
    flow_id_counter[2] = flow_id_counter[2] + 1

    # matching at layer 3
    flow_list[3].append(l3MatchingFlow(
        table_id=0,
        in_port=2,
        nw_src=H1_IP,
        nw_dst=H2_IP,
        flow_id=flow_id_counter[2],
        dl_dst=H2_MAC,
        out_port=1
    ))
    flow_id_counter[2] = flow_id_counter[2] + 1

    flow_list[3].append(l3MatchingFlow(
        table_id=0,
        in_port=1,
        nw_src=H2_IP,
        nw_dst=H1_IP,
        flow_id=flow_id_counter[2],
        dl_dst=H1_MAC,
        out_port=2
    ))
    flow_id_counter[2] = flow_id_counter[2] + 1



    # add flows to tables
    table_list = []
    for i in range(n):
        table_list.append(makeTables(
            switch_id=ovs_ids[i],
            table_id=0,
            flows=flow_list[i]
        ))

    with open('./tables1.json', 'w') as f:
        json.dump(table_list, f)



    table_list = []
    table_list.append(makeTables(
        switch_id=ovs_ids[2],
        table_id=0,
        flows=flow_list[3]
    ))

    with open('./tables2.json', 'w') as f:
        json.dump(table_list, f)


run()
