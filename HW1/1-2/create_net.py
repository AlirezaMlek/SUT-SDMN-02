# #!/usr/bin/env python
#
# """
# linuxrouter.py: Example network with Linux IP router
# This example converts a Node into a router using IP forwarding
# already built into Linux.
# The example topology creates a router and three IP subnets:
#     - 192.168.1.0/24 (r0-eth1, IP: 192.168.1.1)
#     - 172.16.0.0/12 (r0-eth2, IP: 172.16.0.1)
#     - 10.0.0.0/8 (r0-eth3, IP: 10.0.0.1)
# Each subnet consists of a single host connected to
# a single switch:
#     r0-eth1 - s1-eth1 - h1-eth0 (IP: 192.168.1.100)
#     r0-eth2 - s2-eth1 - h2-eth0 (IP: 172.16.0.100)
#     r0-eth3 - s3-eth1 - h3-eth0 (IP: 10.0.0.100)
# The example relies on default routing entries that are
# automatically created for each router interface, as well
# as 'defaultRoute' parameters for the host interfaces.
# Additional routes may be added to the router or hosts by
# executing 'ip route' or 'route' commands on the router or hosts.
# """

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import OVSKernelSwitch
import os

class MyRouter(OVSKernelSwitch):
    """A Node with IP forwarding enabled.
	Means that every packet that is in this node, comunicate freely with its interfaces."""

    def config(self, **params):
        super(MyRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

        os.system('ovs-vsctl add-port r0 r0-eth1 vlan_mode=trunk')
        os.system('ovs-vsctl add-port r0 r0-eth2 vlan_mode=trunk')
        os.system('ifconfig r0 10.0.1.10 up')
        os.system('ifconfig r0 10.0.2.10 up')
        os.system('ovs-vsctl set bridge r0 other-config:hwaddr=00:00:00:00:01:00')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(MyRouter, self).terminate()

class MyTopo2(Topo):

    # pylint: disable=arguments-differ
    def build(self, **_opts):

        # Create switch
        s1 = self.addSwitch('s1', tag=1)
        s2 = self.addSwitch('s2', tag=2)
        r1 = self.addSwitch(name='r0', cls=MyRouter, ip='10.0.1.10/24', arp_responder=True)

        # create link with ip
        self.addLink(s1, r1, intfName2='r0-eth1', intfName1='s1-eth1',
                     params2={'ip': '10.0.1.10/24'}, cls=TCLink)  # for clarity
        self.addLink(s2, r1, intfName2='r0-eth2', intfName1='s2-eth1',
                     params2={'ip': '10.0.2.10/24'}, cls=TCLink)

        # add hosts and assign their gateway
        h1 = self.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01',
                          defaultRoute='via 10.0.1.10', tag=1)
        h2 = self.addHost('h2', ip='10.0.2.1/24', mac='00:00:00:00:00:02',
                          defaultRoute='via 10.0.2.10', tag=2)

        self.addLink(h1, s1, intfName2='s1-eth2')
        self.addLink(h2, s2, intfName2='s2-eth2')


# Allows the file to be imported using `mn --custom <filename> --topo topo2`
topos = {
    'topo2': MyTopo2
}