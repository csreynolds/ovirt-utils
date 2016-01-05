#!/usr/bin/env python
#
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@redhat.com)
#
# Description: Script for setting the keyring password for RHEV scripts
#
# Requires: python keyring
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
RHEV-keyring is a script for mantaining the keyring used by rhev script for storing password

"""
#Parse args in ovirt_functions: parseoptions(basename, description, args)
options = parseoptions(sys.argv[0], description, sys.argv[1:])


if options.askpassword:
    options.password = getpass.getpass("Enter password: ")

# keyring.set_password('redhat', 'kerberos', '<password>')
# remotepasseval = keyring.get_password('redhat', 'kerberos')

if options.query:
    print "Username: %s" % keyring.get_password('rhevm-utils', 'username')
    print "Password: %s" % keyring.get_password('rhevm-utils', 'password')

if options.username:
    keyring.set_password('rhevm-utils', 'username', options.username)
if options.password:
    keyring.set_password('rhevm-utils', 'password', options.password)
