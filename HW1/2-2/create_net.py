#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
import os


class MyRouter(OVSKernelSwitch):
    """A Node with IP forwarding enabled."""

    def config(self, **params):
        super(MyRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')
        os.system('ovs-vsctl add-port r0 r0-eth2 vlan_mode=trunk')
        os.system('ovs-vsctl add-port r0 r0-eth1 vlan_mode=trunk')
        os.system('ifconfig r0 10.0.1.10 up')
        os.system('ifconfig r0 10.0.2.10 up')
        os.system('ovs-vsctl set bridge r0 other-config:hwaddr=00:00:00:00:01:00')

    def clear(self):
        os.system('ovs-ofctl --protocol OpenFlow13 del-flows r0')
        os.system('ovs-ofctl --protocol OpenFlow13 del-flows s1')
        os.system('ovs-ofctl --protocol OpenFlow13 del-flows s2')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(MyRouter, self).terminate()


# create topology
def topology():
    "Create a network."
    net = Mininet(controller=RemoteController, link=TCLink,
                  switch=OVSKernelSwitch)

    # create bridges
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')
    r1 = net.addSwitch(name='r0', cls=MyRouter, ip='10.0.1.10/24', protocols='OpenFlow13', arp_responder=True)

    # add links
    net.addLink(s1, r1, intfName2='r0-eth1', intfName1='s1-eth1',
                params2={'ip': '10.0.1.10/24'}, cls=TCLink, protocols='OpenFlow13')  # for clarity
    net.addLink(s2, r1, intfName2='r0-eth2', intfName1='s2-eth1',
                params2={'ip': '10.0.2.10/24'}, cls=TCLink, protocols='OpenFlow13')

    # add hosts
    h1 = net.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01',
                     defaultRoute='via 10.0.1.10')
    h2 = net.addHost('h2', ip='10.0.2.1/24', mac='00:00:00:00:00:02',
                     defaultRoute='via 10.0.2.10')

    net.addLink(h1, s1)
    net.addLink(h2, s2)

    c1 = net.addController('c1', controller=RemoteController,
                           ip="127.0.0.1", port=6653, protocols='OpenFlow13')

    net.build()
    net.start()


    print("*** Running CLI")

    c1.start()
    s1.start([c1])
    s2.start([c1])
    r1.start([c1])
    net.start()
    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
