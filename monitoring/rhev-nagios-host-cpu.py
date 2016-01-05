#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for monitoring host CPU status and VM's rhevm-sdk
# api and produce NAGIOS valid output
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

from ovirt_functions import *

description = """
RHEV-nagios-host-cpu output  is a script for querying RHEVM via API to get host status

It's goal is to output a table of host/vm status for simple monitoring via external utilities

"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)

# MAIN PROGRAM
# if not options.host:

try:
    host = api.hosts.get(name=options.host)
except:
    print("Host %s not found" % options.host)

if not host:
    print("Host %s not found" % options.host)
    sys.exit(3)

# NAGIOS PRIOS:
# 0 -> ok
# 1 -> warning
# 2 -> critical
# 3 -> unknown

# By default, return unknown
usage = (100 - host.statistics.get(name="cpu.current.idle").values.value[0].datum)

retorno = 3
if usage >= 90:
    retorno = 1
    if usage >= 95:
        retorno = 2
else:
    retorno = 0

print(usage)
sys.exit(retorno)
