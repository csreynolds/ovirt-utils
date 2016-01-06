#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for cleaning VM's pinning to hosts using rhevm-sdk
# api based on RHCS cluster_ tags on RHEV-M and elas_manage
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

from ovirt_functions import *

description = """
RHEV-cleanpinning is a script for managing via API the VMs under RHEV command
in both RHEV-H and RHEL hosts.

It's goal is to keep some VM's <-> host rules to avoid having two cluster
(RHCS) nodes at the same physical host.

"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)


def process_cluster(clusid):
    """Processes cluster with specified cluster ID
    @param clusid: Cluster ID to process
    """
    query = "cluster = %s" % api.clusters.get(id=clusid).name
    for vm in paginate(api.vms, query):
        if vm.cluster.id == clusid:
            if vm.tags.get("elas_manage"):
                for tag in vm.tags.list():
                    if tag.name[0:8] == "cluster_":
                        if vm.placement_policy.affinity != "migratable":
                            if options.verbosity > 1:
                                print("VM %s pinning removed" % vm.name)
                        vm.placement_policy.affinity = "migratable"
                        vm.placement_policy.host = params.Host()
                        vm.update()
    return


# MAIN PROGRAM
if __name__ == "__main__":
    if not options.cluster:
        # Processing each cluster of our RHEVM
        for cluster in api.clusters.list():
            process_cluster(cluster.id)
    else:
        process_cluster(api.clusters.get(name=options.cluster).id)
