#!/usr/bin/env python

import subprocess
import sys
import json
import os 
import time
import signal

from collections import deque

#prints error message

def elog(line):
    sys.stderr.write(line + "\n")
    sys.exit(1)


# Security Groups
class SecurityGroup
  def_init_(self,sg):
    self.gname = sg["GroupName"]
    self.gid = sg["GroupID"]

  def_str_(self):
  return "\tGroupName: {0}\n\tGroupID: {1}".format(self.gname, self.gid)


class Instance:
  def_init_(self, instanceID):
    out,err = execute("aws ec2-describe-instances --instance-id {0} --output json".format(instanceID))

  if out:
    instance = json.loads(out)["Reservations"][0]["Instances"[0]
    self.inId = instanceID
    self.azone = instance["Placement"]["AvailabilityZone"]
    self.key = instance["KeyName"]
    self.Imgid = instance["ImageId"]
    self.InType = instance["InstanceType"]
    self.Ip = instance ["PublicIP"]
    self.dns = instance["PublicDNS"]
    self.uname = "root"
    self.mkp = "~/.ssh/my-key-pair.pem"
    self.secgroup = []

    for group in instance["SecurityGroup"]:
      self.secgroup.append(SecurityGroup(group))
    else:
      elog(err) 
  def_str_(self):
    res="\tinstanceID:{0} \n\tAvailabilityZone: {1}\n\tKeyName: {2}\n\tImageId: {3}\n\tInsatnceType: {4}\n\t
        PublicIP: {5}".format(self.inID, self.azone, self.key, self.Imgid, self.InType, self.Ip)
        for i, group in enumerate(self.secgroup):
          res += "\n\tSG #" + str(i)
          res += str(group)
    return res

#Checks to see if there is a successful login using ssh
#If yes, a footprint of instance will be returned

def Ready(self):
  log("Checking Instance: {0}".format(self.inID))
  out,err = execute("ssh-keyscan {0}".format(self.Ip)

  if out:
    out,err = execute("echo '{0}'>> ~/.ssh/known_hosts".format(out))
    if err:
      elog(err)
    log("Instance: {0} is ready, hosts have been added".format(self.Inid))
    return True
  elif err:
   elog(err)

  log("Instance: {0} is not ready".format(self.Inid))
  return False

def setLogin(self,username):
  self.uname = username

def setFile(self,idFile):
  self.idFile = idFile

#Hosts information is stored which is parsed from ~/.ssh/config

class Host:

def_init_(self, inf_arr):
  cache={}
  for item in inf_arr:
    cache[item[0] = item[1]
  self.host = cache["Host"]
  self.Ip = cache["HostName"]
  self.uname = cache["User"]
  self.idFile = cache["IdentityFile"]

def_str_(self):

  return "\n".join([
   "\tHost: " + self.host,
   "\tHostName: " + self.Ip,
   "\tUser: " + self.uname,
   "\tIdentityFile: " +self.idFile,
   ])


