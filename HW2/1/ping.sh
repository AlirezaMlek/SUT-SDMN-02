#!/bin/bash

if [ $# -ne 2 ];
then
  echo "$0: Invalid arguments: enter two end-points  h1 --ping--> h2"
  exit 1
fi


num_hosts=4
num_hosts_sub=$((num_hosts / 2))

for (( i=0; i<$num_hosts; i++ ))
do

   host_name=node$(($i+1))
   if [ $2 == $host_name ];
   then
	if [ $i -lt $num_hosts_sub ];
	then
	   addr_dst=172.0.0.$(($i+2))
	else
	   addr_dst=10.10.0.$(($i+2-$num_hosts_sub))
	fi
	
   elif [ $1 == $host_name ];
   then
   	src=$host_name
   fi
   
done


# change env to new namespace
sudo ip netns exec $src ping -c 3 $addr_dst

# back to root namespace
exit
