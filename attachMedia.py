from ovirt_functions import *

description = "Attaches an iso to a VM"
options = parseoptions(sys.argv[0], description, sys.argv[1:])


print "options.username: %s" % options.username


try:
    options.username, options.password = getuserpass(options)
    baseurl = "https://%s:%s" % (options.server, options.port)
    api = apilogin(url=baseurl, username=options.username, password=options.password)

    print "Connected to %s successfully!" % api.get_product_info().name

except Exception as ex:
    print "Unexpected error: %s" % ex

vm = api.vms.get(options.vmname)

try:
    sd = api.storagedomains.get(name=options.isodomain)
    isofilelist = sd.files.list(name=options.isoname)
    
    for iso in isofilelist:
        isofilename = iso.get_name()

except Exception as ex:
    print "Unexpected error: %s" % ex

try:
    cdrom = vm.cdroms.get(id="00000000-0000-0000-0000-000000000000")
    isofile = params.File(id=isofilename)
    print "Attaching %s to %s" % (isofilename,options.vmname)
    cdrom.set_file(isofile)
    cdrom.update(current=True)

except Exception as e:
    print 'Failed to Attach ISO to VM:\n%s' % str(e)

try:

    if vm.status.state != 'up':
        print 'Starting VM'
        vm.start()
    else:
        print 'VM already up'

except Exception as e:
       print 'Failed to Start VM:\n%s' % str(e)

api.disconnect()
