import paramiko
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
from time import sleep

hostname = sys.argv[1]
# hostname = '10.16.11.12'
# hostname = '10.16.14.86'
# hostname = '10.16.14.187'
# hostname = '10.16.14.83'
# hostname = '10.16.14.143'
# hostname = '10.50.1.60'
# hostname = '10.50.1.44'
# hostname = 'localhost'

# plt.gcf().subplots_adjust(bottom=0.15)

ssh = paramiko.Transport(hostname,22)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username='admin', password='$ic@Sty#07&')
chan = ssh.invoke_shell()

resp = chan.recv(9999)#welcome to cescnet
resp = chan.recv(9999)#First prompt

def run_cmd(cmd):
    count = 0
    chan.send(cmd + '\n          ')
    # chan.send(' ')
    buff = ''
    op=[]
    while True:
        if(buff.endswith('#')):
            break
        
        resp = chan.recv(9999)
        # x = resp.split()
        # print x
        buff += resp
    
    buff = re.sub('\s+',' ',buff).strip()   
    buff = buff.replace('\r','')
    buff = buff.replace('\b','')
    buff = buff.replace('\t','')
    
    # print (buff)
    op=buff.split()

    op = [e for e in op if e not in ('--More--')]
    op = op[:-1]
    
    
    l=len(cmd.split())
    # print l
    op = op[l:] 

    # print op
    # exit()

    return op
        

command = 'conf t'
output = run_cmd(command)

command = 'no monitor session 1'
output = run_cmd(command)

command = 'monitor session 1 source interface gi0/1'
output = run_cmd(command)

command = 'monitor session 1 destination interface Fa 0/6 ingress Vlan 1'
output = run_cmd(command)

command = 'end'
output = run_cmd(command)

command = 'sh monitor'
output = run_cmd(command)
print output

ssh.close()