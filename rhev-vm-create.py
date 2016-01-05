#!/usr/bin/env python
#
# Description: Script for creating VM's via API
#
# This software is based on GPL code so:
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# Requires rhevm-sdk to work or RHEVM api equivalent
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Contributors:
# Vincent Van der Kussen  (vincent@vanderkussen.org)
#

from rhev_functions import *

description = """
vmcreate is a script for creating vm's based on specified values

vmcpu    defines the number of CPUs
sdtype can be: SD to use
sdsize can be: Storage to assing
vmgest can be: rhevm, or your defined networks
vmserv can be: rhevm, or your defined networks
osver can be: rhel_6x64, etc
"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

from rhev_functions import *

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)

try:
    value = api.hosts.list()
except:
    print("Error accessing RHEV-M api, please check data and connection and retry")
    sys.exit(1)

# Define VM based on parameters
if __name__ == "__main__":
    vmparams = params.VM(os=params.OperatingSystem(type_=options.osver),
                         cpu=params.CPU(topology=params.CpuTopology(cores=int(options.vmcpu))), name=options.name,
                         memory=1024 * 1024 * 1024 * int(options.vmmem), cluster=api.clusters.get(name=options.cluster),
                         template=api.templates.get(name="Blank"), type_="server")
    vmdisk = params.Disk(size=1024 * 1024 * 1024 * int(options.sdsize), wipe_after_delete=True, sparse=True,
                         interface="virtio", type_="System", format="cow", storage_domains=params.StorageDomains(
                             storage_domain=[api.storagedomains.get(name="data_domain")]))
    vmnet = params.NIC()

    network_gest = params.Network(name=options.vmgest)
    network_serv = params.Network(name=options.vmserv)

    nic_gest = params.NIC(name='eth0', network=network_gest, interface='virtio')
    nic_serv = params.NIC(name='eth1', network=network_serv, interface='virtio')

    try:
        api.vms.add(vmparams)
    except:
        print('Error creating VM with specified parameters, recheck')
        sys.exit(1)

    if options.verbosity > 1:
        print("VM created successfuly")

    if options.verbosity > 1:
        print("Attaching networks and boot order...")
    vm = api.vms.get(name=options.name)
    vm.nics.add(nic_gest)
    vm.nics.add(nic_serv)

    # Setting VM to boot always from network, then from HD
    boot1 = params.Boot(dev="network")
    boot2 = params.Boot(dev="hd")
    vm.os.boot = [boot1, boot2]

    try:
        vm.update()
    except:
        print('Error attaching networks, please recheck and remove configurations left behind')
        sys.exit(1)

    if options.verbosity > 1:
        print("Adding HDD")
    try:
        vm.disks.add(vmdisk)
    except:
        print('Error attaching disk, please recheck and remove any leftover configuration')

    if options.verbosity > 1:
        print("VM creation successful")

    vm = api.vms.get(name=options.name)
    vm.memory_policy.guaranteed = 1 * 1024 * 1024
    vm.high_availability.enabled = True
    vm.update()
    print('MAC:%s' % vm.nics.get(name="eth0").mac.get_address())
