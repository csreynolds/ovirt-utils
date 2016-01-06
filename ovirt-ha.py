#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for setting HA
#
# Requires ovirt-engine-sdk to work or RHEVM api equivalent
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

from ovirt_functions import *


description = """
ha is a script for enabling HA for each VM in the cluster
"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)

try:
    value = api.hosts.list()
except:
    print("Error accessing RHEV-M api, please check data and connection and retry")
    sys.exit(1)

query = ""

for vm in paginate(api.vms, query):
    if vm.high_availability.enabled is not True:
        vm.high_availability.enabled = True
        vm.memory_policy.guaranteed = 1 * 1024 * 1024
        try:
            vm.update()
            print("VM %s updated" % vm.name)
        except:
            print("Failure updating VM HA %s" % vm.name)
