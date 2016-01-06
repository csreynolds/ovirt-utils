#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for exporting a VM by snapshoting, creating a new VM
# based on that snapshot and then exporting the snapshot and deleting the VM
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

# Contributors:
# Ian Lochrin LOCHRINI at stgeorge.com.au

from ovirt_functions import *

description = """
RHEV-vm-clone-to-export is a script for creating clones based from a vm snapshot

"""
#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])

options.username, options.password = getuserpass(options)

baseurl = "https://%s:%s" % (options.server, options.port)

api = apilogin(url=baseurl, username=options.username, password=options.password)


def snapclone_to_export(api, vm):
    """Generates a snapshot of a VM, clones it, then exports, and removes the temporary VM
    @param api: pass API call to this function
    @param vm: VM to process
    """
    description = "Preexport-%s" % time.mktime(time.gmtime())

    # GET VM
    cluster = api.clusters.get(id=vm.cluster.id)

    if not vm:
        print("VM %s not found" % vm.name)
        sys.exit(1)

    # Create new snapshot
    if options.verbosity > 0:
        print("Creating snapshot...")

    vm.snapshots.add(params.Snapshot(description=description, vm=vm))

    # Wait for snapshot to finish
    i = 0
    while api.vms.get(name=vm.name).status.state == "image_locked":
        if options.verbosity > 0:
            print("waiting for snapshot to finish %s..." % i)
        time.sleep(10)
        i += 1

    # Get snapshot object
    snap = api.vms.get(name=vm.name).snapshots.list(description=description)[0]

    # Build snapshots collection
    snapshots = params.Snapshots(snapshot=[params.Snapshot(id=snap.id)])

    i = 0
    while api.vms.get(name=vm.name).snapshots.get(id=snap.id).snapshot_status != "ok":
        if options.verbosity > 0:
            print("waiting for snapshot to finish %s..." % i)
        time.sleep(10)
        i += 1

    # Create new VM from SNAPSHOT (NOT WORKING AT THE MOMENT)
    newname = "%s-deleteme" % vm.name

    if options.verbosity > 0:
        print("Creating new VM based on snapshot...")
    api.vms.add(params.VM(name=newname, snapshots=snapshots, cluster=cluster, template=api.templates.get(name="Blank")))

    # Wait for create to finish
    i = 0
    while api.vms.get(name=newname).status.state == "image_locked":
        if options.verbosity > 0:
            print("Waiting for creation to finish...")
        i += 1
        time.sleep(10)

    # DC
    dc = api.datacenters.get(id=cluster.data_center.id)

    # Get Export domain from our DC
    export = None

    for sd in dc.storagedomains.list():
        if sd.type_ == "export":
            export = sd

    if not export:
        print("Export domain required, and none found, exitting...")
        sys.exit(1)

    if options.verbosity > 0:
        print("Exporting cloned VM to export domain...")

    # Export cloned VM to export domain for backup
    api.vms.get(name=newname).export(params.Action(storage_domain=export))

    # Wait for create to finish
    i = 0
    while api.vms.get(name=newname).status.state == "image_locked":
        i += 1
        if options.verbosity > 0:
            print("waiting for export to finish...")
        time.sleep(10)

    if options.verbosity > 0:
        print("Deleting temporary VM...")
    api.vms.get(name=newname).delete()

    if options.verbosity > 0:
        print("Deleting temporary snapshot...")
        print("NOT YET SUPPORTED BY RHEV API")

    return


# MAIN PROGRAM
#
# Uncomment for debug the exception creation
#
# snapclone_to_export(api, vm=api.vms.get(name=options.name))
# sys.exit(0)

if __name__ == "__main__":
    NEW_VM_NAME = options.name
    if not options.name:
        print("VM name is required")
        sys.exit(1)

    if not check_version(api, major=3, minor=2):
        print("This functionality requires api >= 3.2")
        sys.exit(1)

    try:
        snapclone_to_export(api, vm=api.vms.get(name=options.name))
        print('VM was exported succesfully')

    except Exception as e:
        print('Failed to export VM')
