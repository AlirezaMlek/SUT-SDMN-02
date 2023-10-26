#!/usr/bin/env python

from mininet.log import setLogLevel, info
from mininet.topo import Topo


class MyTopo1(Topo):
    "Minimal topology with a single switch and two hosts"

    def build(self):
        setLogLevel('info')

        print("\n")
        info("*** Topo1:          host 1 <--> s1 <--> s2 <--> h2 \n\n")

        # Create two hosts.
        h1 = self.addHost(name='h1', ip="10.0.0.1/24", mac="00:00:00:00:00:01")
        h2 = self.addHost(name='h2', ip="10.0.0.2/24", mac="00:00:00:00:00:02")

        # Create a switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links between the switch and each host
        self.addLink(s1, h1)
        self.addLink(s2, h2)
        self.addLink(s1, s2)


# Allows the file to be imported using `mn --custom <filename> --topo minimal`
topos = {
    'topo1': MyTopo1
}
