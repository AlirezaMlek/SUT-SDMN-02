#!/bin/bash



###### add hosts

num_hosts=4

echo -e "\nadd $numHosts nodes..."

for (( i=0; i<$num_hosts; i++ ))
do
   hosts[i]="node$(($i+1))"
   sudo ip netns add ${hosts[i]}
   echo ${hosts[i]}
done




###### add hosts

echo -e "\nadd router..."
sudo ip netns add router
echo "router"




###### add bridges

for i in 0 1
do
   bridges[i]="s$(($i+1))"
   sudo ip link add ${bridges[i]} type bridge
   echo ${bridges[i]}
done




###### add links between bridges and router

# number of hosts in each subnet
num_hosts_sub=$((num_hosts / 2))

echo -e "\nadd links..."

for (( i=0; i<$num_hosts_sub; i++ ))
do
   # subnet 1
   name1=h$((i+1))-1
   name2=${bridges[0]}-$(($i+1))
   sudo ip link add $name1 type veth peer name $name2
   sudo ip link set $name1 netns ${hosts[i]}
   sudo ip link set $name2 master ${bridges[0]}
   echo "${hosts[i]}   $name1 <---> $name2   ${bridges[0]}"
   
   # subnet 2
   name1=h$(($i+$num_hosts_sub+1))-1
   name2=${bridges[1]}-$(($i+1))
   sudo ip link add $name1 type veth peer name $name2
   sudo ip link set $name1 netns ${hosts[$(($i+$num_hosts_sub))]}
   sudo ip link set $name2 master ${bridges[1]}
   echo "${hosts[$(($i+$num_hosts_sub))]}   $name1 <---> $name2   ${bridges[1]}"
done


# switches and router
for i in 0 1
do
   name1=r-$(($i+1))
   name2=${bridges[$i]}-$(($num_hosts_sub+1))
   sudo ip link add $name1 type veth peer name $name2
   sudo ip link set $name1 netns router
   sudo ip link set $name2 master ${bridges[i]}
   echo "r   $name1 <---> $name2   ${bridges[i]}"
done




###### assign IP

echo -e "\nassign ip..."

# router
sudo ip netns exec router ip addr add 172.0.0.1/24 dev r-1
sudo ip netns exec router ip link set r-1 up
sudo ip netns exec router iptables -t nat -A POSTROUTING -s 172.0.0.0/24 -o r-1 -j MASQUERADE
sudo ip netns exec router ip addr add 10.10.0.1/24 dev r-2
sudo ip netns exec router ip link set r-2 up
sudo ip netns exec router iptables -t nat -A POSTROUTING -s 10.10.0.0/24 -o r-2 -j MASQUERADE


# hosts and default router
for (( i=0; i<$num_hosts; i++ ))
do
   if [ $i -lt  $num_hosts_sub ]
   then
     def_router=172.0.0.1
     addr_h=172.0.0.$(($i+2))/24
   else
     def_router=10.10.0.1
     addr_h=10.10.0.$(($i+2-$num_hosts_sub))/24
   fi
   name=h$(($i+1))-1
   sudo ip netns exec ${hosts[i]} ip addr add $addr_h dev $name
   sudo ip netns exec ${hosts[i]} ip link set $name up
   sudo ip netns exec ${hosts[i]} ip route add default via $def_router
done


sudo ip netns exec router sysctl net.ipv4.ip_forward=1


echo done.




###### install switches

echo -e "\ninstall switches..."
num_iter=$(($num_hosts_sub+2))

for (( i=1; i<$num_iter; i++ ))
do
   sudo ip link set ${bridges[0]}-$i up
   sudo ip link set ${bridges[1]}-$i up
done

echo done.

sudo ip link set s1 up
sudo ip link set s2 up

echo done.






