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
#processing message
def log(line):
 if DEBUG:
    print "DEBUG: " + str(round(float(time.time() - START_TIME),3))+"s -" +str(line)

# Security Groups
class SecurityGroup:
  def __init__(self, sg):
    self.gname = sg["GroupName"]
    self.gid = sg["GroupID"]

  def __str__(self):
    return "\tGroupName: {0}\n\tGroupID: {1}".format(self.gname, self.gid)


class Instance:
  def __init__(self, instanceID):
    out,err = execute("aws ec2-describe-instances --instance-id {0} --output json".format(instanceID))

  if out:
      instance = json.loads(out)["Reservations"][0]["Instances"[0]]
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
  def __str__(self):
    res="\tinstanceID:{0} \n\tAvailabilityZone: {1}\n\tKeyName: {2}\n\tImageId: {3}\n\tInsatnceType: {4}\n\tPublicIP: {5}".format(self.inID, self.azone, self.key, self.Imgid, self.InType, self.Ip)
    for i, group in enumerate(self.secgroup):
        res += "\n\tSG #" + str(i)
        res += str(group)
    return res

#Checks to see if there is a successful login using ssh
#If yes, a footprint of instance will be returned

def Ready(self):
  log("Checking Instance: {0}".format(self.inID))
  out,err = execute("ssh-keyscan {0}".format(self.Ip))

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

#host parser which parses ~/.ssh.config to the host

def parser(dir):
 
    config = open(dir,'r')
#except IOError, err:
    elog("afewmore ERROR: can not open file: {0}".format(dir))

lines = config.readlines()
hosts = []
for i in range(len(lines)):
    if lines[i].strip(" ").split(" ")[0] == "Host":
        j = i + 1
        while(j < len(lines) and lines[j].strip(" ").split(" ")[0]!="Host"):
                       j += 1
        res = [lines[k] for k in range(i,j)]
        hosts.append(Host([item.strip().split(" ") for item in res]))
config.close()
  
#executing the function
#successful return is (stdout, None), if not successful, return is (None,stderr)

#def execute(cmd, timeout=None):

 # try:
 #  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

  #output, error = proc.communicate()

 # if timeout is not None:
 #    time.sleep(timeout)
 #     log("kill command: \n\t{0}".format(cmd)
 #     os.killprog(proc.pid, signal.SIGTERM)
 #     return (output, error)

 # if output:
 #     return (output, None)
 # if error:
 #     log("There was an error executing the command: \n\t{0}".format(cmd))
 #     return (None, error)
 # return ("", None)

 # except OSError, oserror:
 #     return (None, oserror)

#Analyzing the original instance

def analyze_instance(instanceID, copy_dir):
    log("Analyzing the original Instance: {0}".format(instanceID))

    origin = Instance(instanceID)
    while not origin.Ready():
      origin.Ready()

    log('cheking username...')
    out, err = execute("ssh {0}@{1} 'echo cs615'".format(origin.uname, origin.dns))

    if err:
      log(err)
      elog("afewmore ERROR: can not access instance: {0}".format(origin.inId))

    else:
      msg = out.split(' ')
      if msg[0].strip() !="cs615":
        log("user is not [0]".format(origin.uname))
      login = msg[5].strip('"')
      log("changing user to {0}".format(login))
    origin.setLogin(login)

    #else:
    # log("user is {0}".format(origin.uname))

      #sets superuser command
    SUPER_USER_COMMAND = 'sudo'
    log('changing dir ownership...')
    execute("ssh {0}@{1} '{2} chown -R {0} {3}'".format(origin.uname, origin.dns, SUPER_USER_COMMAND, copy_dir))
    log('changing dir mode...')
    execute("ssh {0}@{1} '{2} chown -R 700 {3}'".format(origin.uname, origin.dns, SUPER_USER_COMMAND, copy_dir))
    log("Checking source directory..")
    out, err = execute("ssh {0}@{1} 'ls -l {2}'".format(origin.uname, origin.dns, copy_dir))
    if err:
                elog("afewmore ERROR: cannot access directory or no such file")
                print err

    return origin

#Analyzes Created Instance

def analyze_created(created, target_dir):
    log('cheking username...')
    out, err = execute("ssh {0}@{1} 'echo cs615'".format(created.uname, created.dns))

    if err:
      log(err)
      elog("afewmore ERROR: can not access instance: {0}".format(created.inId))

    else:
      msg = out.split(' ')
      if msg[0].strip() !="cs615":
        log("user is not [0]".format(created.uname))
        login = msg[5].strip('"')
        log("changing user to {0}".format(login))
        created.setLogin(login)

    #else:
      log("user is {0}".format(created.uname))

      #sets superuser command
      SUPER_USER_COMMAND = 'sudo'
      log('Creating Target Dir..')
      execute("ssh {0}@{1} '{2} mkdir -p {3}'".format(created.uname, created.dns, SUPER_USER_COMMAND, target_dir))
      log('changing dir ownership...')
      execute("ssh {0}@{1} '{2} chown -R {0} {3}'".format(created.uname, created.dns, SUPER_USER_COMMAND, target_dir))
      log('changing dir mode...')
      execute("ssh {0}@{1} '{2} chown -R 700 {3}'".format(created.uname, created.dns, SUPER_USER_COMMAND, target_dir))
      log("Checking source directory..")
      out, err = execute("ssh {0}@{1} 'ls -l {2}'".format(created.uname, created.dns, target_dir))
      if err:
          elog("afewmore ERROR: cannot access directory or no such file")
          print err

      return created

def duplicate(origin_inst, num):

    instances_queue = [] 
    origin = origin_inst
    out, err = execute("aws ec2 run-instances --placement AvailabilityZone={0} --image-id {1} --security-group-ids {2} --count {3} --instance-type {4} --key-name {5} --query 'Instances[*].InstanceId' --output json"
        .format(
        origin.azone,
        origin.Imgid,
        " ".join([group.gid for group in origin.secgroup]),
        num,
        origin.Intype,
        origin.key
    ))
    if out:
        for instanceID in json.loads(out):
            log("pushing instance: {0} to queue".format(instanceID))
            instances_queue.append(Instance(instanceID))
        return deque(instances_queue)
    else:
       elog(err)

#Copy files from source to new instance

def srcopy(origin, targets, dir="/data"):

     if dir[len(dir) - 1] != "/":
        dir += "/"

     while len(targets) is not 0:
        target = targets.popleft()
        target.uname = origin.uname

        start_time = time.time()

        if target.Ready():
            target = analyze_created(target, dir)
            log("Copying to Target: {0}".format(target.inId))
            out, err = execute("srcopy -3C -r {0}@{1}:{2} {3}@{4}:{5}"
                .format(origin.uname, origin.dns, dir + "*", target.uname, target.dns, dir))
            if err:
                elog(err)
            if out:
                log(out)
            else:
                log("successfully copied files")
                if not DEBUG:
                    print "\t" + target.inId
                log(target)
        else:
            targets.append(target)
        
        end_time = time.time()

        if end_time - start_time < 5:
            log("wating...")
time.sleep(5)

# Start of the program
def start(instanceID, copy_dir, num_ins):
    log("starting with {0} {1} {2}".format(instanceID, copy_dir, num_ins))
    log("verbose: " + str(DEBUG))

    origin_instance = analyze_instance(instanceID, copy_dir)
    log("Completed checking source instance: " + origin_inst.inId)

    log("duplicating instances...")
    targets_queue = duplicate(origin_inst, num_ins)
    log("Completed duplicating instnaces ")

    log("Copying " + copy_dir + "...")
    scp(origin_inst, targets_queue, copy_dir)

    log("Completed\n")

if __name__ == "__main__":

    DEBUG = False  
#Source Config File
    SSH_CONFIG_DIR = os.path.expanduser('~') + "/.ssh/config"
#Source instance provided by the user    
    INSTANCE_ID = "" 
#Default number of instances to start
    NUM_INS = 10 
#Deafult Directory to copy files from
    COPY_DIR = "/data" 
    START_TIME = time.time()

    options = sys.argv 
    FLAGS = {
        "-h":False,
        "-d":False,
        "-n":False,
        "-v":False,
    }
    i = 1

    while i < len(options):
        op = options[i]
        if op not in FLAGS or i is len(options) - 1:
            if (len(op) is not 19):
                elog("afewmore ERROR: Invalid argument {0}".format(op))
            if i is not len(options) - 1:
                elog("afewmore ERROR: Invalid argument after {0}".format(op))
            INSTANCE_ID = op
            start(INSTANCE_ID, COPY_DIR, NUM_INS)
            break;
        if FLAGS[op]:
            elog("afewmore ERROR: Multiple argument {0}".format(op))

        if op == "-n":
            FLAGS["-n"] = True
            i += 1
            try:
                NUM_INS = int(options[i])
            except (IndexError, ValueError) as err:
                elog("afewmore ERROR: Invalid argument after {0}".format(op))
        if op == "-d":
            FLAGS["-d"] = True
            i += 1
            try:
                COPY_DIR = options[i]
            except ValueError, err:
                elog("afewmore ERROR: Invalid argument after {0}".format(op))
        if op == "-v":
            FLAGS["-v"] = True
            DEBUG = True
        if op == "-h":


            print "AFEWMORE(1)       BSD General Commands Manual          AFEWMORE(1)\n\
    \n\
    NAME\n\
         afewmore -- duplicate EC2 instances with their data directory\
    \n\
    SYNOPSIS\n\
         afewmore [-hv] [-d dir] [-n num] instance\n\
    \n\
    DESCRIPTION\n\
         The afewmore tool can be used to duplicate a given EC2 instance.  When\n\
         doing so, it creates multiple new instances and populates their data\n\
         directory by copying the data from the original.\n\
    \n\
    OPTIONS\n\
         The source instance is specified via the mandatory argument to afewmore.\n\
         In addition, the following command-line options are supported:\n\
    \n\
         -d dir   Copy the contents of this data directory from the orignal source\n\
              instance to all the new instances.  If not specified, defaults\n\
              to /data.\n\
    \n\
         -h       Print a usage statement and exit.\n\
    \n\
         -n num   Create this many new instances.  If not specified, defaults to\n\
              10.\n\
    \n\
         -v       Be verbose.\n\
    \n\
    DETAILS\n\
         Frequently, it is necessary to duplicate a given server's configuration\n\
         or setup.  While configuration management and service orchestration sys-\n\
         tems may be able to perform this task, the afewmore tool allows for a\n\
         trivial initial bootstrapping that only concerns itself with data dupli-\n\
         cation, not host configuration.\n\
    \n\
         Upon invocation, afewmore will identify the type of EC2 instance in ques-\n\
         tion and launch the requested number of duplicates.  It will then copy\n\
         the contents of the given directory from the source instance to all of\n\
         the newly created instances.\n\
    \n\
    OUTPUT\n\
         By default, afewmore prints the instance IDs of the newly created EC2\n\
         instances as the only output.  Unless an error occurs, no other output is\n\
         generated.\n\
    \n\
         If the -v flag is given, afewmore may print meaningful diagnostic mes-\n\
         sages as it progresses to stdout.\n\
    \n\
         Any errors encountered cause a meaningful error message to be printed to\n\
         STDERR.\n\
    \n\
    ENVIRONMENT\n\
         The afewmore tool is suitable to be used by any user and does not have\n\
         any user-specific settings or credentials hard coded.\n\
    \n\
         afewmore assumes that the user has set up their environment for general\n\
         use with the EC2 tools.  That is, it will not set or modify any environ-\n\
         ment variables.\n\
    \n\
         afewmore also assumes that the user has set up their ~/.ssh/config file\n\
         to access instances in EC2 via ssh(1) without any additional settings.\n\
    \n\
    EXIT STATUS\n\
         The afewmore will exit with a return status of 0 under normal circum-\n\
         stances.  If an error occurred, afewmore will exit with a value >0.\n\
    \n\
    EXAMPLES\n\
         The following examples illustrate common usage of this tool.\n\
    \n\
         To create ten more instances of the EC2 instance i-0a1b2c3d4f and copy\n\
         the contents of the '/data' directory from that instance:\n\
    \n\
           $ afewmore i-0a1b2c3d4f\n\
           i-0a1b2c3d4f\n\
           i-1a1b2c3d4f\n\
           i-2a1b2c3d4f\n\
           i-3a1b2c3d4f\n\
           i-4a1b2c3d4f\n\
           i-5a1b2c3d4f\n\
           i-6a1b2c3d4f\n\
           i-7a1b2c3d4f\n\
           i-8a1b2c3d4f\n\
           i-9a1b2c3d4f\n\
           $ echo $?\n\
           0\n\
           $\n\
    \n\
         To create just one more instance and copy the contents of the directory\n\
         '/usr/local/share':\n\
    \n\
           $ afewmore -n 1 i-0a1b2c3d4f\n\
           i-1a1b2c3d4f\n\
           $\n\
    \n\
    SEE ALSO\n\
         aws help, ssh(1), tar(1), rsync(1)\n\
    \n\
    HISTORY\n\
         afewmore was originally assigned by Jan Schaumann\n\
         <jschauma@cs.stevens.edu> as a homework assignment for the class 'Aspects\n\
         of System Administration' at Stevens Institute of Technology in the\n\
         Spring of 2017.\n\
    \n\
    BSD             March 27, 2017                 BSD"
            break
        i += 1


