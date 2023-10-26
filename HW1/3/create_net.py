#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
import json

def networkInfo(port_id, router, port, ip = None, mode = 'trunk'):
    return { "id": port_id, "name": router, "port": port, "ip": ip, 'mode': mode }

# class of router
class MyRouter(OVSKernelSwitch):

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(MyRouter, self).terminate()


def load_graph():
    g=[]
    with open('./graph.json', 'r') as f:
        gJ = json.load(f)
        for i in range(len(gJ)):
            g.append(gJ[str(i)])
    return g

def topology(g):
    "Create a network."
    net = Mininet(controller=RemoteController, link=TCLink,
                  switch=OVSKernelSwitch)

    l = len(g)

    names = []
    switches = []
    # add bridges
    for i in range(l):
        if i==0:
            switches.append(net.addSwitch(name='r1', cls=MyRouter, ip='10.0.1.10/24', protocols='OpenFlow13', arp_responder=True))
            names.append('r1')
        elif i==l-1:
            switches.append(net.addSwitch(name='r'+str(l), cls=MyRouter, ip='10.0.2.10/24', protocols='OpenFlow13', arp_responder=True))
            names.append('r'+str(l))
        else:
            switches.append(net.addSwitch('s'+str(i+1), protocols='OpenFlow13'))
            names.append('s'+str(i+1))


    port_info = []
    port_counter = [0 for _ in range(l)]

    # add links
    for i in range(l):
        for j in range(l):
            if g[i][j] != 0 and i != j:
                port_counter[i] = port_counter[i] + 1
                port_counter[j] = port_counter[j] + 1
                if i==0:
                    if j!=l-1:
                        int1 = 'r{}-eth{}'.format(i+1, j+1)
                        int2 = 's{}-eth{}x'.format(j+1, i+1)
                        net.addLink(switches[i], switches[j], intfName1=int1, intfName2=int2, delay=g[i][j],
                                    cls=TCLink, protocols='OpenFlow13')


                        port_info.append(networkInfo(port_counter[i], names[i], int1))
                        port_info.append(networkInfo(port_counter[j], names[j], int2))

                    # set ips when both bridges are router
                    else:
                        int1 = 'r{}-eth{}'.format(i+1, j+1)
                        int2 = 'r{}-eth{}x'.format(j+1, i+1)
                        ip1 = '10.0.3.1/32'
                        ip2 = '10.0.3.2/32'
                        net.addLink(switches[i], switches[j], intfName1=int1, intfName2=int2, delay=g[i][j],
                                    params1={'ip': ip1}, params2={'ip': ip2},
                                    cls=TCLink, protocols='OpenFlow13')

                        port_info.append(networkInfo(port_counter[i], names[i], int1, ip1))
                        port_info.append(networkInfo(port_counter[j], names[j], int2, ip2))
                        # sub = sub + 2

                elif i == l-1:
                    if j != 0:
                        int1 = 'r{}-eth{}'.format(i+1, j+1)
                        int2 = 's{}-eth{}x'.format(j+1, i+1)
                        net.addLink(switches[i], switches[j], intfName1=int1, intfName2=int2, delay=g[i][j],
                                    cls=TCLink, protocols='OpenFlow13')

                        port_info.append(networkInfo(port_counter[i], names[i], int1))
                        port_info.append(networkInfo(port_counter[j], names[j], int2))

                    # set ips when both bridges are router
                    else:
                        int1 = 'r{}-eth{}'.format(i + 1, j + 1)
                        int2 = 'r{}-eth{}x'.format(j + 1, i + 1)
                        ip1 = '10.0.3.2/32'
                        ip2 = '10.0.3.1/32'
                        net.addLink(switches[i], switches[j], intfName1=int1, intfName2=int2, delay=g[i][j],
                                    params1={'ip': ip1}, params2={'ip': ip2}, cls=TCLink, protocols='OpenFlow13')

                        port_info.append(networkInfo(port_counter[i], names[i], int1, ip1))
                        port_info.append(networkInfo(port_counter[j], names[j], int2, ip2))

                else:
                    int1 = 's{}-eth{}'.format(i + 1, j + 1)
                    if j==0 or j==l-1:
                        int2 = 'r{}-eth{}x'.format(j+1, i+1)
                    else:
                        int2 = 's{}-eth{}x'.format(j+1, i+1)

                    net.addLink(switches[i], switches[j], intfName1=int1, intfName2=int2,
                                cls=TCLink, protocols='OpenFlow13', delay=g[i][j])

                    port_info.append(networkInfo(port_counter[i], names[i], int1))
                    port_info.append(networkInfo(port_counter[j], names[j], int2))



    # add hosts
    h1 = net.addHost('h1', ip='10.0.1.1/32', mac='00:00:00:00:00:01',
                     defaultRoute='via 10.0.1.10')
    h2 = net.addHost('h2', ip='10.0.2.1/32', mac='00:00:00:00:00:02',
                     defaultRoute='via 10.0.2.10')

    ip1 = '10.0.1.10/32'
    int1 = 'r1-ethe'
    net.addLink(switches[0], h1, params1={'ip': ip1}, intfName1=int1, intfName2='h1-eth1')
    port_info.append(networkInfo(port_counter[0]+1, names[0], int1, ip1, 'access'))

    ip1 = '10.0.2.10/32'
    int1 = 'r{}-ethe'.format(l)
    net.addLink(switches[l-1], h2, params1={'ip': ip1}, intfName1=int1, intfName2='h2-eth1')
    port_info.append(networkInfo(port_counter[l-1]+1, names[l-1], int1, ip1, 'access'))

    mac_info = []
    mac_info.append({'name': names[0], 'mac': '00:00:00:00:01:00'})
    mac_info.append({'name': names[-1], 'mac': '00:00:00:00:02:00'})

    info = {'ports': port_info, 'macs': mac_info}


    with open('./info.json', 'w') as f:
        json.dump(info, f)

    c1 = net.addController('c1', controller=RemoteController,
                           ip="127.0.0.1", port=6653, protocols='OpenFlow13')

    net.build()
    net.start()


    print("*** Running CLI")

    for i in range(l):
        switches[i].start([c1])

    net.start()
    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(load_graph())
