'''
Created on Feb 23, 2015

@author: rgroten
'''

import ConfigParser
from datetime import datetime

from flask.globals import g

# Import NetApp API libraries
from NaElement import NaElement
from NaServer import NaServer


# from flask.globals import g
def connect():
    naHost = getConfigOption("NAHost")
    user = getConfigOption("User")
    password = getConfigOption("Password")
    s = NaServer(naHost, 1 , 21)
    s.set_server_type("FILER")
    s.set_transport_type("HTTPS")
    s.set_port(443)
    s.set_style("LOGIN")
    s.set_admin_user(user, password)
    return s


def getConfigOption(option, section=None):
           
    config = ConfigParser.ConfigParser()
    config.read("/home/rgroten/git/NetApp-Snapshot-Manager/snapmgr/config.ini")

    # If section is not provided, first check if g.env is set and use that.
    # Otherwise, set section to GENERAL
    if not section:
        try:
            if g.env:
                section = g.env
        except:
            section = "GENERAL"

    return config.get(section, option)


def executeCmd(cmd):
    isDebug = getConfigOption("Debug")

    s= connect()
    if (isDebug == 'True'):
        print("Request Object: " + cmd.sprintf())
    ret = s.invoke_elem(cmd)
    
    if (ret.results_status() == "failed"):
        print("Error: ")
        print(ret.sprintf())

#     Print object for debugging
    if (isDebug == 'True'):
        print( "Response Object: " + ret.sprintf())
    return ret


def listVolumes():
    isDebug = getConfigOption("Debug")
#     Build command to list volumes
    cmd = NaElement("volume-get-iter")
    xi = NaElement("desired-attributes")
    xi1 = NaElement("volume-attributes")

 
    xi1.child_add(NaElement("volume-id-attributes"))
    xi1.child_add(NaElement("volume-snapshot-attributes"))
    xi1.child_add(NaElement("volume-space-attributes"))   
    
    xi2 = NaElement("volume-clone-attributes")
    xi2.child_add(NaElement("volume-clone-parent-attributes"))
    xi1.child_add(xi2)
    
    xi.child_add(xi1)

    cmd.child_add(xi)   
    cmd.child_add_string("max-records", "500")
    
    ret = executeCmd(cmd)

    # Remove volumes from list that contain filterStrings
    filterString = getConfigOption("VolFilters")
    filterList = filterString.replace(" ","").split(",")
    filteredVolumes = NaElement("attributes-list")

    for vol in ret.child_get("attributes-list").children_get():
        volattrs = vol.child_get('volume-id-attributes')

        if any(x in volattrs.child_get_string('name') for x in filterList):
            if (isDebug == 'True'):
                print "Skipping filtered vol : %s" % volattrs.child_get_string('name')
            continue
        if (isDebug == 'True'):
            print 'Volume Name : %s' % volattrs.child_get_string('name')
            
        filteredVolumes.child_add(vol)

    filteredRet = NaElement("results")
    filteredRet.attr_set("status", "passed")
    filteredRet.child_add(filteredVolumes)

    if (isDebug == 'True'):
        print "Number of volumes (after filtering): " + str(ret.child_get("attributes-list").children_get().__len__())
    return filteredRet


def listSnapshots(volume):
    cmd = NaElement('snapshot-list-info')
    cmd.child_add_string('volume', volume)

    ret = executeCmd(cmd)

    return ret


def createSnapshot(volume, customname=None):
    if customname:
        snapshotName = customname
    else:
#         Create snapshot format name
        snapshotName = "snap_" + volume + "_" +  datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")

    cmd = NaElement('snapshot-create')
    cmd.child_add_string("volume", volume)
    cmd.child_add_string("snapshot", snapshotName)

    return executeCmd(cmd)


def deleteSnapshot(volume, snapshot):
    cmd = NaElement('snapshot-delete')
    cmd.child_add_string("snapshot", snapshot)
    cmd.child_add_string("volume", volume)

    return executeCmd(cmd)


def restoreSnapshot(volume, snapshot):
    cmd = NaElement('snapshot-restore-volume')
    cmd.child_add_string("snapshot", snapshot)
    cmd.child_add_string("volume", volume)

    return executeCmd(cmd)


def renameSnapshot(volume, snapshot, newName):
    cmd = NaElement('snapshot-rename')
    cmd.child_add_string("current-name", snapshot)
    cmd.child_add_string("volume", volume)
    cmd.child_add_string("new-name", newName)

    return executeCmd(cmd)


def createClone(parentVolume, volume):
    cmd = NaElement('volume-clone-create')
    cmd.child_add_string("parent-volume", parentVolume)
    cmd.child_add_string("volume", volume)
    
    # Feature disabled for now
    debugret = NaElement("results")
    debugret.attr_set("status", "failed")
    debugret.attr_set("reason", "Creating clones not supported...yet!")
    return debugret


def getEnvs():
    envs = getConfigOption("Environments", "GENERAL").split(",")
    envObjs = []
    for env in envs:
        try:
            envObj = EnvObj(env)

            envObjs.append(envObj)
        except Exception as e:
            print str(e)
            print "Error: couldn't load options for environment: " + env
    return envObjs

class EnvObj:
    name = ""
    rfcRequired = False

    def __init__(self, envName):
        self.get_env_properties(envName)


    def get_env_properties(self, envName):
        self.name = envName
        self.rfcRequired = getConfigOption("RFCRequired", envName)
        return self


    def get_name(self):
        return self.__name


    def get_rfc_required(self):
        return self.rfcRequired


    def set_name(self, value):
        self.__name = value


    def set_rfc_required(self, value):
        self.__rfcRequired = value


    def del_name(self):
        del self.__name


    def del_rfc_required(self):
        del self.__rfcRequired

    name = property(get_name, set_name, del_name, "name's docstring")
    rfcRequired = property(get_rfc_required, set_rfc_required, del_rfc_required, "rfcRequired's docstring")

                    