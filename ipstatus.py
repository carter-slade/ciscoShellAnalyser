import Tkinter
import tkMessageBox
import paramiko
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import re
import sys
from time import sleep
import os
hostname = sys.argv[1]
# hostname = '10.16.11.12'
# hostname = '10.16.11.139 telnet'
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

top = Tkinter.Tk()

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
    buff = buff.replace('administratively down', 'administratively_down')
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
    
def helloCallBack():
   tkMessageBox.showinfo( "Hello Python", "Hello World")
def open_this(myStr):
	# os.system('python iptrafficsingle.py '+hostname+" "+ myStr)
	subprocess.Popen('python iptrafficsingle.py '+hostname+" "+ myStr)

def generate(interfaces, str):
	global x
	buttons=[]
	count=0
	x+=1
	if(str is 'up'):
		for i in xrange(0,len(interfaces)):
			
			buttons.append(Tkinter.Button(top, text=interfaces[i],command=lambda i=i:open_this(interfaces[i]),bg='green',activebackground='white'))
			
			if count is 10:
				count=0
				x+=1
			buttons[i].grid(column=count, row=x,sticky='nsew')	
			count+=1
			
			
	elif(str is 'down'):
		for i in xrange(0,len(interfaces)):
			
			buttons.append(Tkinter.Button(top, text=interfaces[i],command=lambda i=i:open_this(interfaces[i]),bg='red',activebackground='white'))
			if count is 10:
				count=0
				x+=1
			buttons[i].grid(column=count, row=x,sticky='nsew')		
			count+=1
	else:
		for i in xrange(0,len(interfaces)):
			
			buttons.append(Tkinter.Button(top, text=interfaces[i],command=lambda i=i:open_this(interfaces[i]),bg='yellow',activebackground='white'))
			if count is 10:
				count=0
				x+=1
			buttons[i].grid(column=count, row=x,sticky='nsew')
			count+=1	

x=0
command = 'sh ip int brief | include down'
output = run_cmd(command)
print output
interfaces=[]
for x in xrange(0,len(output)):
	if x%6==0:
		if interfaces is not '--More--':
			interfaces.append(output[x])

generate(interfaces,'down')
print interfaces
# generate(interfaces,'administratively_down')

command = 'sh ip int brief | include up'
output = run_cmd(command)
interfaces=[]
for x in xrange(0,len(output)):
	if x%6==0:
		if interfaces is not '--More--':
			interfaces.append(output[x])

generate(interfaces,'up')
print interfaces

top.mainloop()