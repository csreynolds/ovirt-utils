#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for creating cloned machines based on a template
#
# Requires rhevm-sdk to work
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Goals:
# - Do not manage any host without tag elas_manage
# - Operate on one host per execution, exitting after each change
# - Have at least one host up without vm's to hold new VM's
# - Shutdown/suspend hosts without vm's until there's only one left
# - If a host has been put on maintenance and has no tag, it will not be activated by the script
# - Any active host must have no tags on it (that would mean user-enabled, and should have the tag removed)


# tags behaviour
# elas_manage: manage this host by using the elastic management script (EMS)
# elas_maint : this host has been put on maintenance by the EMS

from ovirt_functions import *

description = """
RHEV-clone is a script for creating clones based from a template

"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)

# MAIN PROGRAM
# Check if we have defined needed tags and create them if missing
if __name__ == "__main__":
    NEW_VM_NAME = options.name
    CLUSTER_NAME = options.cluster
    TEMPLATE_NAME = options.template

    try:
        api.vms.add(params.VM(name=NEW_VM_NAME, cluster=api.clusters.get(CLUSTER_NAME),
                              template=api.templates.get(TEMPLATE_NAME)))
        print('VM was created from Template successfully')

        print('Waiting for VM to reach Down status')
        while api.vms.get(NEW_VM_NAME).status.state != 'down':
            time.sleep(1)

    except Exception as e:
        print('Failed to create VM from Template:\n%s' % str(e))
