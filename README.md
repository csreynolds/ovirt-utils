#oVirt-Elastic-Management Scripts

REQUIRES: ovirt-engine-sdk-python or  rhevm-sdk 
Required: python-keyring
Required: python-argparse if < python2.7 installed

NOTE: If you are willing to use the keyring feature, please, first setup a username/password using `ovirt-keyring.py` before using `-k` argument with the remaining scripts.
 
Author: Pablo Iranzo Gómez (Pablo.Iranzo@redhat.com)
Modified by: Chris Reynolds (c.reynolds82@gmail.com)

Contributors: 

- Ian Lochrin 
- Sean P Kane (github.com/spkane)

Please, check individual README files for specific behaviour and description under doc/:

- ovirt_functions.py:         Common set of functions for usage by other scripts

- ovirt-keyring.py:           Script to set/query keyring values for username/password

- ovirt-elastic.py:           Manage hosts and power them off if unused

- ovirt-vm-cluster.py:        Use tags to migrate VM's away from each other (sort of anti-affinity)

- ovirt-vlan.py:              Create VLAN with name and vlan_id on DC and associate to specified cluster and its hosts

- ovirt-cleanpinning.py:      Clean VM pinning to host

- ovirt-policy.py:            Change clusters policy to the one provided

- ovirt-vm-os.py:             Group VM's by O.S. on hosts

- ovirt-clone.py:             Create a clone VM based on a Template on a specified Cluster

- ovirt-poweron.py:           Power on (remove maintenance) from all rhev_elastic hosts in maintenance in order to prepare for peak hours

- ovirt-vm-start.py:          Start VM specified or remaining VM's if specified is up

- ovirt-vm-create.py:         Create a new VM with specified parameters

- ovirt-vm-tax.py:            Create a table with information about last month usage and configured values for CPU/RAM/HDD

- ovirt-vm-applist.py:        Create a table with information about VM's and apps reported by ovirt-agent

PD: Please, if you're using this scripts, send me an email just to know if
there's anyone outside there. If you find any error, please report it to me
and I'll try to get it fixed, opening a issue request on github helps to track them!

Those scripts are updated when I have the opportunity to deal with the environment, so they maybe outdated until I have the chance to update them to newer versions, and may have errors not detected when performing updates on others, please, test with care and report any issue.

Philosophy is: Release Early, Release Often, so some scripts can be ugly (no error control, etc), but provide the basic functionality, in later updates, they will be improved.
