#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import os
from mininet.log import info, setLogLevel
def push_flow(flows_dir):

    setLogLevel('info')

    with open(flows_dir, "r") as f:
        data = json.load(f)

    for flow in data:
        # add flows with ovs-ofctl
        comm = "ovs-ofctl add-flow {0} \"idle_timeout={1},priority={2},{3},actions={4}\"". \
            format(flow["dev"], flow["idle_timeout"], flow["priority"], flow["other"], flow["actions"])
        os.system(comm)

        info("*** add new entry to {0}: {1}\n".format(flow["dev"],flow["other"]))


dir = str(sys.argv[1])
push_flow(dir)
