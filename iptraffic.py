import paramiko
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
from time import sleep

# hostname = sys.argv[1]
hostname = '10.16.14.250'
# hostname = '10.16.11.12'
# hostname = '10.16.14.86'
# hostname = '10.16.14.187'
# hostname = '10.16.14.83'
# hostname = '10.16.14.143'
# hostname = '10.50.1.60'
# hostname = '10.50.1.44'
# hostname = 'localhost'
passwords = ['$ic@Sty#07&','poi(&%','(&%poi']
# plt.gcf().subplots_adjust(bottom=0.15)
stat = 1
for pwd in passwords:
	try:
		ssh = paramiko.Transport(hostname,22)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname, username='admin', password=pwd)
		stat = 0
		break
	except Exception as e:
		print e
if stat is 1:
	print 'Not able to SSH with any password'
	exit()		
	# print 'Wrong credentials'	
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
        if(buff.endswith('--More--')):
            chan.send(' ')

        resp = chan.recv(9999)
        # x = resp.split()
        # print x
        buff += resp
        buff = buff.strip()
        # print buff+"-=-=-=-=-==--"
    buff = re.sub('\s+',' ',buff).strip()   
    buff = buff.replace('\r','')
    buff = buff.replace('\b','')
    buff = buff.replace('\t','')
    buff = buff.replace('--More--','')
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


def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.005*h, '%d'%int(h),ha='center', va='bottom',rotation=90,fontsize=8)	
	
def run_in_loop():
	try:
		
		for x in xrange(0,len(interfaces)):
			command = 'sh int '+interfaces[x]+' | include BW'
			bw = run_cmd(command)
			# print bw
			bandwidth.append(int(bw[4]))
		# print max(bandwidth)	
		

		while True:
			ipvals=[]
			opvals=[]
			ax.clear()
			ax.set_ylabel('Bitrate in Kbits/sec')
			ax.set_xticks(ind+width/2)
			ax.set_xticklabels(interfaceshort,rotation=90,fontsize=8)
			# ax.set_ylim(0,max(bandwidth))


			for i in xrange(0,len(interfaces)):
				command = 'sh int '+interfaces[i]+' | include bits'
				stats = run_cmd(command)

				ipvals.append(float(stats[4])/1000)
				opvals.append(float(stats[12])/1000)

			# print ipvals
			
			rects1 = ax.bar(ind, ipvals, width, color='r')
			rects2 = ax.bar(ind+width, opvals, width, color='g')
			ax.legend( (rects1[0], rects2[0]), ('Input', 'Output'))	
			autolabel(rects1)
			autolabel(rects2)
			plt.title('Interfaces of '+hostname)
			plt.draw()
			plt.pause(0.5)
								
			# sleep(1)	
	except KeyboardInterrupt:
		print 'Interrupted'
		ssh.close()


command = 'sh ip int brief | include up'
# command = 'sh ip int brief'
plt.title('Please wait while the graph loads')
plt.draw()
plt.show()
output = run_cmd(command)
interfaces=[]
bandwidth=[]
for x in xrange(0,len(output)):
	if x%6==0:
		if interfaces is not '--More--':
			interfaces.append(output[x])

# print "Interfaces",interfaces
# exit()
N = len(interfaces)
ind = np.arange(N)  # the x locations for the groups
width = 0.27       # the width of the bars

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111)
plt.subplots_adjust(bottom=0.20)

interfaceshort=[]
for x in interfaces:
	f=x
	if x[0] is 'F':
		f=x.replace("FastEthernet","fa")
	if x[0] is 'G':
		f=x.replace("GigabitEthernet","gi")
	if x[0] is 'T':
		f=x.replace("TenGigabitEthernet","ten")
	interfaceshort.append(f)
print interfaceshort	
run_in_loop()
ssh.close()