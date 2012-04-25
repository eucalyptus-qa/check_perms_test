#!/usr/bin/python

import sys
import os
import subprocess

#These are the paths to check
KnownComponents = ['WS', 'SC']

PathsToCheck = {
    'SC' : '/disk1/storage/eucalyptus/instances/volumes',
    'WS' : '/disk1/storage/eucalyptus/instances/bukkits'}

class PermsChecker(object):

    def __init__(self):
        self.hosts = []
        self.ips = []
	self.ips = {'WS' : [],
                    'SC' : []}
        self.euca_home = "/opt/eucalyptus"

    def get_ips(self, filepath):
        data = open(filepath).readlines()
        for line in data:
            if "PKG_REPO" in line:
                self.euca_home = "/"
            for component in KnownComponents:
                if component in line:
                    self.ips[component].append(line[:line.find("\t")])

    def check_walrus_perms(self):
        for ip in self.ips['WS']:
            cmd = ["ssh"]
            cmd.append("root@" + ip)
            cmd.append("stat")
            cmd.append("-c")
            cmd.append("%a")
            cmd.append(PathsToCheck['WS'])
            pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = pipe.communicate()
            if len(output[0]) > 0:
                perm = output[0].strip()
                if perm == "700":
                    print "Perms for " + PathsToCheck['WS'] + " on " + ip + " are correct"
                else:
                    print "Invalid perms for " + PathsToCheck['WS'] + " on " + ip + " (" + perm + ")"
                    exit(1)

    def check_sc_perms(self):
        for ip in self.ips['SC']:
            skip = False
            cmd = ["ssh"]
            cmd.append("root@" + ip)
            cmd.append("grep")
            cmd.append("SANManager")
            cmd.append(self.euca_home + "/etc/eucalyptus/eucalyptus.conf")
            pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = pipe.communicate()
            if len(output[0]) > 0:
                print "SAN configuration detected on " + ip + " skipping..."
                skip = True

            if not skip:
                cmd = ["ssh"]
                cmd.append("root@" + ip)
                cmd.append("stat")
                cmd.append("-c")
                cmd.append("%a")
                cmd.append(PathsToCheck['SC'])
                pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = pipe.communicate()
                if len(output[0]) > 0:
                    perm = output[0].strip()
                    if perm == "700":
                        print "Perms for " + PathsToCheck['SC'] + " on " + ip + " are correct"
                    else:
                        print "Invalid perms for " + PathsToCheck['SC'] + " on " + ip + " (" + perm + ")"
                        exit(1)


permschecker = PermsChecker()
permschecker.get_ips("../input/2b_tested.lst")
permschecker.check_walrus_perms()
permschecker.check_sc_perms()
exit(0)
