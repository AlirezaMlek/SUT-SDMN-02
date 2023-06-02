#!/usr/bin/env python3

from utils import *






def main():

    # Read values from args
    container, memory_limit = read_values()

    # Create a new network namespace for the container
    subprocess.call(['ip', 'netns', 'add', container])

    # Create a pair of virtual network interfaces (veth) and move one end to the container namespace
    subprocess.call(['ip', 'link', 'add', 'veth0', 'type', 'veth', 'peer', 'name', 'veth1'])
    subprocess.call(['ip', 'link', 'set', 'veth1', 'netns', container])

    # Configure the veth interfaces with IP addresses
    subprocess.call(['ip', 'addr', 'add', '10.0.0.1/24', 'dev', 'veth0'])
    subprocess.call(['ip', 'netns', 'exec', container, 'ip', 'addr','add', '10.0.0.2/24', 'dev', 'veth1'])

    # Bring up the veth interfaces
    subprocess.call(['ip', 'link', 'set', 'veth0', 'up'])
    subprocess.call(['ip', 'netns', 'exec', container, 'ip', 'link', 'set', 'veth1', 'up'])

    # Set the default route for the container
    subprocess.call(['ip', 'netns', 'exec', container, 'ip', 'route', 'add', 'default', 'via', '10.0.0.1'])

    # limit memory for the process
    pid = os.getpid()
    cgroup_config(memory_limit, pid)


    # File system setup
    # init_fs()

    """
    * create new namespaces: pid, net, uts, and mount (mnt)
    * create a distinct root for the container
    * starter.sh: sleep for a few seconds and mount proc in the container, then start a bash
    """
    cmd = initial_env_cmd(container)

    # Start the container
    subprocess.call(cmd)

    # Clean env after exit
    clean_network_ns(container)






if __name__ == '__main__':
    main()
