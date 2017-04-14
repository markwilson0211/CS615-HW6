import os

class Host:
    def __init__(self, in_arr):
        cache = {}
        for item in in_arr:
            cache[item[0]] = item[1]
        self.host = cache["Host"]
        self.Ip = cache["HostName"]
        self.user = cache["User"]
        self.mkp = cache["IdentityFile"]

    def __str__(self):
        return "\n".join([
            "Host: " + self.host, 
            "HostName: " + self.Ip,
            "User: " + self.user, 
            "IdentityFile: " + self.mkp,
            ])


SSH_CONFIG_DIR = os.path.expanduser('~') + "~/.ssh/config"

def host_parser():
    config = open(SSH_CONFIG_DIR, 'r')

    lines = config.readlines()
    hosts = []
    for i in range(len(lines)):
        if lines[i].strip(" ").split(" ")[0] == "Host":
            j = i + 1
            while (j < len(lines) and lines[j].strip(" ").split(" ")[0] != "Host"):
                j += 1
            res = [lines[k] for k in range(i, j)]
            hosts.append(Host([item.strip().split(" ") for item in res]))
    return hosts

    config.close()


for host in host_parser():
    print host
