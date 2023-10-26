
import create_net
import os

g = create_net.load_graph()

l = len(g)


for i in range(l):
    if i==0 or i==l-1:
        prf = 'r' + str(i+1)
    else:
        prf = 's' + str(i+1)

        os.system('ovs-ofctl --protocol OpenFlow13 del-flows {}'.format(prf))
