#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for switching clusters policy to specified one, actually power_saving or evenly_distributed
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
RHEV-policy is a script for managing via API cluster policy

Actual policy is:
- power_saving
- evenly_distributed

"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)


# FUNCTIONS
def process_cluster(clusid):
    """Processes cluster
    @param clusid: Cluster ID to process
    """
    if options.verbosity > 1:
        print("\nProcessing cluster with id %s and name %s" % (clusid, api.clusters.get(id=clusid).name))
        print("#############################################################################")

    cluster = api.clusters.get(id=clusid)
    cluster.scheduling_policy.policy = options.policy
    try:
        cluster.update()
    except:
        if options.verbosity > 2:
            print("Problem updating policy")

            # evenly_distributed
            # power_saving


# MAIN PROGRAM
if __name__ == "__main__":

    if not options.cluster:
        # Processing each cluster of our RHEVM
        for cluster in api.clusters.list():
            process_cluster(cluster.id)
    else:
        process_cluster(api.clusters.get(name=options.cluster).id)
