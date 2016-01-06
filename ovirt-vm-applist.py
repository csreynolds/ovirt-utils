#!/usr/bin/env python
#
# Author:    Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
# Description: Script for accessing RHEV-M DB for gathering app list for a given VM
#
# Requires rhevm-sdk to work and psycopg2 (for PG access)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.

import psycopg2
from ovirt_functions import *

description = """
rhev-vm-applist is a script for gathering statistics about VM usage that can be used to tax usage
"""

#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)
con = psycopg2.connect(database='engine', user=options.dbuser, password=options.dbpass)

try:
    value = api.vms.list()
except:
    print("Error accessing RHEV-M api, please check data and connection and retry")
    sys.exit(1)


# FUNCTIONS
def gathervmdata(vmname):
    """Obtans VM data from Postgres database and RHEV api
    @param vmname: VM name to get information for
    """
    # Get VM ID for the query
    vmid = api.vms.get(name=vmname).id

    # sql Query for gathering date from range
    sql = "select app_list as vm_apps from vm_dynamic where vm_guid='%s' ;" % vmid

    cur.execute(sql)
    rows = cur.fetchall()

    return rows[0]


def vmdata(vm):
    """Returns a list of VM data
    @param vm: object identifying VM and return information from it
    """
    # VMNAME, VMRAM, VMRAMAVG, VMCPU, VMCPUAVG, VMSTORAGE, VMSIZE
    vmdata = [vm.name, gathervmdata(vm.name)]
    return vmdata


def htmlrow(lista):
    """Returns an HTML row for a table
    @param lista: Elements to put as diferent columns to construct a row
    """
    table = "<tr>"
    for elem in lista:
        table += "<td>%s</td>" % elem
    table += "</tr>"
    return table


def htmltable(listoflists):
    """Returns an HTML table based on Rows
    @param listoflists: Contains a list of all table rows to generate a table
    """
    table = "<table>"
    for elem in listoflists:
        table += htmlrow(elem)
    table += "</table>"
    return table

# MAIN PROGRAM
if __name__ == "__main__":

    # Open connection
    cur = con.cursor()

    print("<html>")
    print("<head><title>VM Table</title></head><body>")

    if not options.name:
        data = [["Name", "App list"]]
        for vm in paginate(api.vms):
            try:
                data.append(vmdata(vm))
            except:
                skip = 1
    else:
        data = [["VMNAME", "APP list"], vmdata(api.vms.get(name=options.name))]

    print(htmltable(data))

    if con:
        con.close()

    print("</body></html>")
