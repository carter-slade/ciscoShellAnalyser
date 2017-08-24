import paramiko
import numpy as np
import matplotlib.pyplot as plt
import re
import os
from time import sleep
from matplotlib.widgets import Slider, Button, RadioButtons
from textwrap import wrap
import sys
import smtplib
from datetime import datetime
import time
MAXLIMIT=1000
queue={}
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
        ax.text(rect.get_x()+rect.get_width()/2, 1.005*h, '%d'%int(h),ha='center', va='bottom',rotation=90,fontsize=8)	

def sendmail(intf,usein,useout,timestamp):

	try:
		smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
		smtpObj.ehlo()
		smtpObj.starttls()
		smtpObj.login('cesctraffic@gmail.com', '$ic@Sty#07&')
		smtpObj.sendmail('cesctraffic@gmail.com', 'deepak19396@gmail.com', 'Subject: Bandwidth Overuse\n \nInterface: %s\nInput: %s\nOutput: %s\nTimestamp: %s\n' %(intf,usein,useout,timestamp))
		smtpObj.quit()
	except Exception as e:
		print "SMTP ERROR"+ e

def dealwith(intf, timestamp):
	# print queue
	if intf not in queue.keys():
		queue[intf]	= timestamp
		print "MAIL SENT for", intf
	for x in queue:
		if (time.time()-queue[x])>60:
			# print "removed "+str(queue[x])
			del queue[x]
			return
def run_in_loop():
	try:
		for x in xrange(0,len(interfaces)):
			command = 'sh int '+interfaces[x]+' | include BW'
			bw = run_cmd(command)
			# print bw
			# bandwidth.append(int(bw[4]))
		
		
		# sendmail(interfaces[i],inp,oup,str(datetime.now()))
			
			# print queue
		while True:	
			ipvals=[]
			opvals=[]
			ax.clear()
			ax.set_ylabel('Bitrate in Kbits/sec')
			ax.set_xticks(ind+width/2)
			ax.set_xticklabels(interfaceDesc,rotation=90,fontsize=6)
			# ax.set_ylim(0,max(bandwidth))


			for i in xrange(0,len(interfaces)):
				command = 'sh int '+interfaces[i]+' | include bits'
				stats = run_cmd(command)

				# print stats
				inp = float(stats[4])/1000
				oup = float(stats[12])/1000

				# if inp>=MAXLIMIT or oup>=MAXLIMIT:
					# dealwith(interfaces[i],time.time())
				ipvals.append(inp)
				opvals.append(oup)

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
	except Exception as e:
		print e	

command = 'sh ip int brief | include up'
# command = 'sh ip int brief'

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111)
plt.subplots_adjust(bottom=0.20)

plt.title('Please wait while the graph loads')
plt.draw()
plt.pause(0.5)

output = run_cmd(command)
# print output
# exit()

print output

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


# fig.autofmt_xdate()

# resolve_button_ax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
# resolve_button = Button(resolve_button_ax, 'Resolve', color='orange', hovercolor='0.975')
# def resolve_button_on_clicked(mouse_event):
# 	os.system('python python ipstatus.py '+hostname)
# resolve_button.on_clicked(resolve_button_on_clicked)

interfaceshort=[]
interfaceDesc=[]
for x in interfaces:
	f=x

	command = 'sh int '+x+' | include Description'
	op = run_cmd(command)
	print op
	desc = ' '.join(op)
	desc = desc.replace('Description','')
	desc = desc.replace('Connected','')
	desc = desc.replace('connected','')
	# if len(desc)>=25:
	# 	desc=desc[-25:]
	
	if x[0] is 'F':
		f=x.replace("FastEthernet","fa")
	if x[0] is 'G':
		f=x.replace("GigabitEthernet","gi")
	if x[0] is 'T':
		f=x.replace("TenGigabitEthernet","ten")
	interfaceshort.append(f)
	interfaceDesc.append(f+'->'+desc)
	interfaceDesc = [ '\n'.join(wrap(l, 20)) for l in interfaceDesc ]
print interfaceshort
run_in_loop()
ssh.close()