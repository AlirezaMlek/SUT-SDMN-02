#!/bin/bash

num_hosts=4

echo "delete namespaces and links..."

for (( i=0; i<$num_hosts; i++ ))
do
   hosts[i]="node$(($i+1))"
   sudo ip netns delete ${hosts[i]}
   
done

sudo ip netns delete router
sudo ip link delete s1
sudo ip link delete s2

echo done
