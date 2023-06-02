import sys
import os
import subprocess
import psutil

def clean_network_ns(container):
    # Clean up after the container exits
    subprocess.call(['ip', 'netns', 'delete', container])
    subprocess.call(['ip', 'link', 'delete', 'veth0'])

def initial_env_cmd(container):
    cmd_env = 'unshare --pid --net --uts --mount -f --mount-proc ip netns exec {}'.format(container).split(' ')
    cmd = 'chroot /home/oldman/ubuntu20.04/ /bin/bash /bin/starter.sh'.split()
    return cmd_env+cmd


def init_fs():
    # Start the container's init process
    if not os.path.exists("./ubuntu20.04"):
        os.system('debootstrap --variant=minbase focal ./ubuntu20.04 http://archive.ubuntu.com/ubuntu/')

    os.system('cp ./namespace-stat.sh ./ubuntu20.04/home')


def read_values():
    if len(sys.argv) != 3:
        print("Usage: {} <container>".format(sys.argv[0]))
        sys.exit(1)

    container = sys.argv[1]
    memory_limit = int(sys.argv[2])

    return container, memory_limit


def cgroup_config(mem_lim, pid):
    # Set the path to the cgroup directory
    cgroup_path = '/sys/fs/cgroup/sdmn'
    if not os.path.exists(cgroup_path):
        os.mkdir(cgroup_path)

    # Write the memory limit to the memory.limit_in_bytes file

    os.system('echo "{}" | sudo tee {}/memory.high'.format(mem_lim, cgroup_path))

    os.system('echo "{}" | sudo tee {}/cgroup.procs'.format(pid, cgroup_path))