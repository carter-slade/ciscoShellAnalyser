import paramiko
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
from time import sleep
import time
from datetime import datetime
import calendar
hostname = sys.argv[1]

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

resp=''
while resp.endswith('#') is not True:
    resp = chan.recv(9999)#Till first prompt


def run_cmd(cmd):
    count = 0
    chan.send(cmd + '\n')
    # chan.send(' ')
    buff = ''
    op=[]
    while True:
        if(buff.endswith('#')):
            break
        if('--More--' in buff):
            buff = buff.replace('--More--','')
            chan.send(' ')

        resp = chan.recv(9999)
        # x = resp.split()
        # print buff

        buff += resp
        # buff = buff.strip()
        # print buff+"-=-=-=-=-==--"
    buff = re.sub('\s+',' ',buff).strip()   
    buff = buff.replace('\r','')
    buff = buff.replace('\b','')
    buff = buff.replace('\t','')
    buff = buff.replace('--More--','')
    # print (buff)
    op=buff.split()

    op = [e for e in op if e not in ('--More--')]
    
    # print op
    # exit()

    op = op[:-1]
    l=len(cmd.split())
    # print l
    op = op[l:] 

    # print op
    # exit()

    return op

def run_in_loop():
    try:
        while True:
            interf=[]
            command = 'show int trunk | include trunking'
            # print command
            op = run_cmd(command)
            for i in xrange(0,len(op)):
                if op[i]=='on':
                    interf.append(op[i-1])

            for inter in interf:            
                inter = inter.replace('Gi','GigabitEthernet')
                inter = inter.replace('Fa','FastEthernet')
                inter = inter.replace('Te','TenGigabitEthernet')
                print inter

            command = 'show log | include %LINEPROTO-5-UPDOWN: '
            op = run_cmd(command)
            # print op
            # exit()
            # inter = 'FastEthernet0/15'

            log=[]
            for x in xrange(0,len(op)):
                for inter in interf:
                    if inter in op[x]:
                        myDate =  op[x-7]+"-"+op[x-8].replace('*','')+" "+op[x-6]
                        # print myDate
                        time_tuple = datetime.strptime(myDate, "%d-%b %H:%M:%S:")
                        timestamp = calendar.timegm(time_tuple.utctimetuple())
                        # print(time_tuple)
                        # print timestamp

                        log.append(str(timestamp)+"->"+op[x]+"->"+op[x+4])

            print log
            res = check_flap(log)
            if len(res) is not 0:
                for re in res:
                    print "Flapping occured for :" +re

            time.sleep(60)
    except KeyboardInterrupt:
        print 'Interrupted'
        ssh.close()            

def check_flap(log):
    result=[]
    for i in xrange(0,len(log)-1):
        a = log[i].split('->')
        b = log[i+1].split('->')

        if((int(b[0])-int(a[0]))<=60):
            if a[2]!=b[2]:
                result.append(a[1])

    return result



run_in_loop()    