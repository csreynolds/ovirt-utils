#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for starting VM's using rhevm-sdk
# api based on single VM dependency
#
# Requires rhevm-sdk to work
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.

# Goals:
# - Do not manage any VM without tag elas_manage
# - reverse missing -> start VM specified
# - reverse 1             -> start all VM's if VM specified is up and running

# tags behaviour
# elas_manage: this machine is being managed by this script

from ovirt_functions import *

description = """
RHEV-vm-start is a script for managing via API the VMs under RHEV command in both RHEV-H and RHEL hosts.

It's goal is to keep some VM's started if another VM is running and host status has not changed

"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)


# FUNCTIONS
def process_cluster(cluster):
    """Processes cluster
    @param cluster: Cluster to process
    """
    # Emtpy vars for further processing
    hosts_in_cluster = []
    vms_in_cluster = []

    # Get host list from this cluster
    query = "cluster = %s" % api.clusters.get(id=cluster.id).name
    for host in paginate(api.hosts, query):
        if host.cluster.id == cluster.id:
            hosts_in_cluster.append(host.id)

    if options.verbosity > 2:
        print("\nProcessing cluster %s..." % cluster.name)
        print("##############################################")

    # Populate the list of tags and VM's
    query = "cluster = %s" % api.clusters.get(id=cluster.id).name
    for vm in paginate(api.vms, query):
        if vm.cluster.id == cluster.id:
            vms_in_cluster.append(vm.id)

    query = "cluster = %s and tag = elas_manage" % api.clusters.get(id=cluster.id).name
    for vm in paginate(api.vms, query):
        if vm.cluster.id == cluster.id:
            if vm.tags.get("elas_manage"):
                # Add the VM Id to the list of VMS to manage in this cluster
                vms_in_cluster.append(vm.id)

    if options.verbosity > 3:
        print("Hosts in cluster:")
        print(hosts_in_cluster)

        print("Vm's in cluster")
        print(vms_in_cluster)

    destino = None
    for vm in vms_in_cluster:
        # Iterate until we get our target machine to monitor
        maquina = api.vms.get(id=vm)
        if maquina.name.startswith(options.machine):
            if maquina.tags.get("elas_manage"):
                destino = maquina
            else:
                if options.verbosity > 4:
                    print("Specified target machine has no elas_manage tag attached")
                sys.exit(1)

    # Iterate for all the machines in our cluster and check behaviour based on reverse value
    one_is_up = False
    for host in hosts_in_cluster:
        if api.hosts.get(id=host).status.state == "up":
            one_is_up = True

    if destino:
        if options.reverse == 0:
            if destino.status.state == "down":
                if options.verbosity > 3:
                    print("Our VM is down... try to start it if possible")
                if one_is_up:
                    try:
                        destino.start()
                    except:
                        if options.verbosity > 3:
                            print("Error starting up machine %s" % destino.name)
        else:
            # Reverse is != 0... then just boot if target machine is already up
            if destino.status.state == "up":
                # Our target VM is not down, it's safe to start our machines up!
                for vm in vms_in_cluster:
                    maquina = api.vms.get(id=vm)
                    if maquina.tags.get("elas_manage"):
                        if maquina.status.state != "up":
                            if maquina.id != destino.id:
                                try:
                                    maquina.start()
                                except:
                                    if options.verbosity > 3:
                                        print("Error starting %s" % maquina.name)
                    else:
                        if options.verbosity > 4:
                            print("VM %s has no elas_manage tag associated" % maquina.name)
            else:
                if options.verbosity > 3:
                    print("Target machine is not up, not starting vm")

# MAIN PROGRAM
if __name__ == "__main__":
    # Check if we have defined needed tags and create them if missing
    check_tags(api, options)

    # TAGALL?
    # Add elas_maint TAG to every single vm to automate the management
    if options.tagall == 1:
        if options.verbosity >= 1:
            print("Tagging all VM's with elas_manage")
        for vm in paginate(api.vms):
            try:
                vm.tags.add(params.Tag(name="elas_manage"))
            except:
                print("Error adding elas_manage tag to vm %s" % vm.name)
    if options.machine == "":
        print("Error machine name must be defined")
        sys.exit(1)

    if not options.cluster:
        # Processing each cluster of our RHEVM
        for cluster in api.clusters.list():
            process_cluster(cluster)
    else:
        process_cluster(api.clusters.get(name=options.cluster))
