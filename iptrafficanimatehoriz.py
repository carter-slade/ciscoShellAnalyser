import paramiko
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import re
import os
import matplotlib.animation as animation
from time import sleep
from matplotlib.widgets import Slider, Button, RadioButtons
from textwrap import wrap
import sys
import smtplib
from datetime import datetime
import time, matplotlib
matplotlib.use('TkAgg')
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from matplotlib.font_manager import FontProperties

fontP = FontProperties()
fontP.set_size('small')

MAXLIMIT=50000 # 50 Mbps limit
TIMELIMIT=1800 #Half an hour
REF_RATE=60 #in seconds

queue={}
adminemail = ['deepak19396@gmail.com','sk.ali1@rp-sg.in','rishabhgupta23@gmail.com']

style.use('fivethirtyeight')

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(1,1,1)
plt.subplots_adjust(left=0.20)

# plt.title('Loading the plot. Please wait...')
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')

plt.draw()

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
        h = rect.get_width()
        ax.text(1.005*h, rect.get_y()+rect.get_height()/2.,'%d'%int(h),ha='left', va='center',fontsize=6)	

def sendmail(intf,intfd,usein,useout,timestamp):

	try:
		smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
		smtpObj.ehlo()
		smtpObj.starttls()
		smtpObj.login('cesctraffic@gmail.com', '$ic@Sty#07&')
		fromaddr = "cesctraffic@gmail.com"
		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['Subject'] = "Bandwidth Overuse"
		body = 'Interface: %s\nDescription: %s\nInput(Kbps): %s\nOutput(Kbps): %s\nTimestamp: %s\n' %(intf,intfd,usein,useout,timestamp)
		msg.attach(MIMEText(body, 'plain'))
		text = msg.as_string()

		for email in adminemail:
			toaddr = email
			msg['To'] = toaddr
			smtpObj.sendmail(fromaddr, toaddr, text)
		
		smtpObj.quit()
	except Exception as e:
		print e

def dealwith(intf,intfd,timestamp,inp,oup):
	# print queue

	if intf not in queue.keys():
		queue[intf]	= timestamp
		print "MAIL SENT for", intf , time.ctime(int(timestamp))
		sendmail(intf,intfd,inp,oup,time.ctime(int(timestamp)))
	for x in queue:
		if (time.time()-queue[x])>TIMELIMIT:
			# print "removed "+str(queue[x])
			del queue[x]
			return
def animate(i):
	
	ipvals=[]
	opvals=[]
	interfaces=[]
	ax.clear()
	
	op = run_cmd("show interfaces | include line_protocol | input_rate | output_rate")    
	# print op
	# print len(op)
	for x in xrange(0,len(op)):
	    if op[x]=='protocol':
	        if 'up' in op[x-2]:
				interfaces.append(op[x-4])
				if 'Vlan' in op[x-4]:
					inp = float(op[x+7])/1000
					oup = float(op[x+15])/1000
					
					
				else:
					inp = float(op[x+8])/1000
					oup = float(op[x+16])/1000
				
				if inp>=MAXLIMIT or oup>=MAXLIMIT:
					if op[x-4] in interfaceDesc.keys():
						dealwith(op[x-4],interfaceDesc[op[x-4]],time.time(),inp,oup)
					else:
						dealwith(op[x-4],"Unknown",time.time(),inp,oup)

				ipvals.append(inp)
				opvals.append(oup)

	N = len(interfaces)
	ind = np.arange(N)  # the x locations for the groups
	width = 0.3				

	interfacedesc=[]
	for x in interfaces:
		if x in interfaceDesc.keys():
			interfacedesc.append(interfaceDesc[x])
		else:
			command = 'sh int '+x+' | include Description'
			op = run_cmd(command)
			print op
			desc = ' '.join(op)
			desc = desc.replace('Description','')
			desc = desc.replace('Connected','')
			desc = desc.replace('connected','')
			interfacedesc.append(x+'->'+desc)
			interfaceDesc[x]=desc	
		# interfaceshort.append(f)
	# print ipvals
	ax.set_xlabel('Bitrate in Kbits/sec')
	ax.set_yticks(ind+width/2)
	ax.set_yticklabels(interfacedesc,fontsize=6)
	rects1 = ax.barh(ind, ipvals, width, color='r')
	rects2 = ax.barh(ind+width, opvals, width, color='g')
	ax.legend( (rects1[0], rects2[0]), ('Input', 'Output'),prop = fontP)	
	autolabel(rects1)
	autolabel(rects2)
	plt.title('Interfaces of '+hostname)

	
	# ax.set_ylim(0,max(bandwidth))


	# for i in xrange(0,len(interfaces)):
	# 	command = 'sh int '+interfaces[i]+' | include bits'
	# 	stats = run_cmd(command)
		
	# 	inp = float(stats[4])/1000
	# 	oup = float(stats[12])/1000

	# 	if inp>=MAXLIMIT or oup>=MAXLIMIT:
	# 		dealwith(interfaces[i],interfaceDesc[i],time.time(),inp,oup)
	# 	ipvals.append(inp)
	# 	opvals.append(oup)
		
	

command = 'sh ip int brief | include up'
# command = 'sh ip int brief'
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
width = 0.3       # the width of the bars


interfaceshort=[]
interfaceDesc={}
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
	# interfaceshort.append(f)
	interfaceDesc[x]=f+'->'+desc
	# interfaceDesc = [ '\n'.join(wrap(l, 20)) for l in interfaceDesc ]
print interfaceshort

try:
	# plt.draw()
	ani = animation.FuncAnimation(fig, animate, interval=(REF_RATE*1000))#miliseconds
	plt.show()
except KeyboardInterrupt:
	print 'Interrupted'
	ssh.close()
