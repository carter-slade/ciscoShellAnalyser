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

MAXLIMIT=70000 # 70 Mbps limit
TIMELIMIT=1800 #Half an hour
queue={}
adminemail = ['deepak19396@gmail.com','sk.ali1@rp-sg.in']

style.use('fivethirtyeight')

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(1,1,1)
plt.subplots_adjust(bottom=0.20)
plt.title('Loading the plot. Please wait...')
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.pause(0.5)

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
        ax.text(rect.get_x()+rect.get_width()/2., 1.005*h, '%d'%int(h),ha='center', va='bottom',rotation=90,fontsize=8)	

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

		if inp>=MAXLIMIT or oup>=MAXLIMIT:
			dealwith(interfaces[i],interfaceDesc[i],time.time(),inp,oup)
		ipvals.append(inp)
		opvals.append(oup)

	# print ipvals
	
	rects1 = ax.bar(ind, ipvals, width, color='r')
	rects2 = ax.bar(ind+width, opvals, width, color='g')
	ax.legend( (rects1[0], rects2[0]), ('Input', 'Output'))	
	autolabel(rects1)
	autolabel(rects2)
	plt.title('Interfaces of '+hostname)
		
	

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
width = 0.27       # the width of the bars


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

try:
	ani = animation.FuncAnimation(fig, animate, interval=1000)
	plt.show()
except KeyboardInterrupt:
	print 'Interrupted'
	ssh.close()
