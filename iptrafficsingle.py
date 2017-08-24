import paramiko
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
from time import sleep

hostname = sys.argv[1]
interface = sys.argv[2]
REF_RATE=10
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

    		
def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.005*h, '%d'%int(h),ha='center', va='bottom',fontsize=8)	
	
def run_in_loop():
	try:
		
		
		command = 'sh int '+interface+' | include BW'
		bw = run_cmd(command)
		# print bw
		# bandwidth.append(int(bw[3]))
		# print max(bandwidth)	
		

		while True:
			ipvals=[]
			opvals=[]
			ax.clear()
			ax.set_ylabel('Bitrate in Kbits/sec')
			ax.set_xticks(ind+width/2)
			# ax.set_xticklabels(interface,rotation=90,fontsize=8)
			ax.set_xlabel(interface)
			# ax.set_ylim(0,max(bandwidth))


			
			command = 'sh int '+interface+' | include bits'
			stats = run_cmd(command)

			ipvals.append(float(stats[4])/1000)
			opvals.append(float(stats[12])/1000)

			# print ipvals
			
			rects1 = ax.bar(ind, ipvals, width, color='r')
			rects2 = ax.bar(ind+width, opvals, width, color='g')
			ax.legend( (rects1[0], rects2[0]), ('Input', 'Output'))	
			autolabel(rects1)
			autolabel(rects2)
			plt.title('Traffic of '+interface+'('+desc+')'+' Bandwidth = '+bw[4])
			plt.draw()
			plt.pause(REF_RATE)
								
			# sleep(1)	
	except KeyboardInterrupt:
		print 'Interrupted'
		ssh.close()


ind = np.arange(1)  # the x locations for the groups
width = 0.27       # the width of the bars

ip=''
mac=''
x = interface
if x[0] is 'F':
	f=x.replace("FastEthernet","fa")
elif x[0] is 'G':
	f=x.replace("GigabitEthernet","gi")
elif x[0] is 'T':
	f=x.replace("TenGigabitEthernet","ten")
else:
	f=''

command = 'show cdp neighbors '+f+' detail | include IP'
# print command
op = run_cmd(command)
# print op

x = interface
if x[0] is 'F':
	f=x.replace("FastEthernet","Fa")
if x[0] is 'G':
	f=x.replace("GigabitEthernet","Gi")
if x[0] is 'T':
	f=x.replace("TenGigabitEthernet","Ten")

if len(op) is not 0:
	ip = op[-1]
	# print ip
if ip is '':
	command = 'show mac address-table | include '+f	
	op = run_cmd(command)
	try:
		index = op.index(f)
		macop = op[index-3:index+1]
		print macop
		if len(macop) is not 0:
			mac=macop[1]
	except Exception as e:
		print 'NO MAC/IP Specified'		
command = 'sh int '+interface+' | include Description'
op = run_cmd(command)

# print op

desc = ' '.join(op[6:])
desc = desc+"\n,IP:"+ip+"\n,MAC:"+mac
# print "descscsc", desc
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111)
plt.subplots_adjust(bottom=0.20)

plt.title('Please wait while the graph loads')
plt.draw()
plt.pause(0.5)

run_in_loop()
ssh.close()
print "Exited!"