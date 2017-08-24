import paramiko
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
from time import sleep
import sys
import telnetlib
import networkx as nx
import webbrowser
import tkMessageBox
import Tkinter as tk 

G = nx.Graph()


def run_cmd(cmd,chan):
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


def run_in_loop(hostname):
	global count
	global endstat
	global result

	stat = 1
	count = count+1
	if count is maxhop:
		print "Max Hop count reached"
		ssh.close()
		return
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
		print 'Not able to SSH with any password trying telnet'
		try:
			tn = telnetlib.Telnet(hostname, timeout=2)
			tn.open(hostname)
		except Exception as e:
			print e
			return
		user = 'admin'	
		password = '$ic@Sty#07&'		
		tn.read_until('Username:',timeout=1)
		tn.write(user+"\n")	

		tn.write(password + "\n")

		op = tn.read_until(">", timeout=1)


		if op[-1]=='>':
			tn.write("en\n")
			tn.write(password + "\n")
			tn.read_until("#")

		command = "sh spanning-tree | include Root\n" 
		tn.write(command)
		command = command.split()
		op = tn.read_until("#",timeout=2)
		l = len(command)
		op = op.split()
		# print op
		# exit()
		op = op[l:-1]
		root = op[4]

		print "ROOT",root

		command = 'sh cdp neighbors '+root+' detail | include IP\n'
		tn.write(command)
		command = command.split()
		op = tn.read_until("#",timeout=2)
		l = len(command)
		op = op.split()
		op = op[l:-1]
		rootip = op[-1]	
		print "ROOTIP",rootip


		command = 'sh cdp neighbors '+root+' detail | include Device\n'
		tn.write(command)
		command = command.split()
		op = tn.read_until("#",timeout=2)
		print op
		l = len(command)
		op = op.split()
		op = op[l:-1]
		details = op[-1]

		print root+"---->"+rootip+"---->"+details
		if rootip in servers:
			result.append(('server',rootip,root))
			print "SERVER FOUND"
			if rootip==dest:
				print "Destination reached"
				endstat=1
				ssh.close()
				return
			return
		else:
			if rootip[0].isdigit() is True:
				print rootip+' appended'
				if rootip==dest:
					result.append((root,rootip,details))
					print "Destination reached"
					endstat=1
					ssh.close()
					return	
				result.append((root,rootip,details))
		 # print 'Wrong credentials'
	if stat==0: 	
		chan = ssh.invoke_shell()
		resp=''
		while resp.endswith('#') is not True:
			resp = chan.recv(9999)#Till first prompt
		
		command = 'sh spanning-tree | include Root'
		# command = 'sh ip int brief'
		output = run_cmd(command,chan)
		# fig = plt.figure(figsize=(20,10))
		# ax = fig.add_subplot(111)
		# plt.subplots_adjust(bottom=0.20)
		root = output[4]
		command = 'sh cdp neighbors '+root+' detail | include IP'
		output = run_cmd(command,chan)
		rootip = output[-1]

		command = 'sh cdp neighbors '+root+' detail | include Device'
		output = run_cmd(command,chan)
		details = output[-1]

		print root+"---->"+rootip+"---->"+details
		if rootip in servers:
			result.append(('server',rootip,root))
			print "SERVER FOUND"
			if rootip==dest:
				print "Destination reached"
				endstat=1
				ssh.close()
				return
			return
		else:
			if rootip[0].isdigit() is True:
				if rootip==dest:
					result.append((root,rootip,details))
					print "Destination reached"
					endstat=1
					ssh.close()
					return	
				result.append((root,rootip,details))
	run_in_loop(rootip)

result=[]
maxhop = 50
count = 1
host = sys.argv[1]
dest = sys.argv[2]
servers = ['10.50.1.2','10.16.11.245']
passwords = ['$ic@Sty#07&']
endstat=0
result.append(('host',host,'Source'))

root = tk.Tk()
root.withdraw()
# tkMessageBox.showinfo("Loading Graph", "Fetching the paths take time, please wait while we plot the route")

run_in_loop(host)

print result
resultforward = result[:]

if endstat==0:
	resultbackward=[]
	print "BACKWARD TRACE NEEDED"
	result=[]
	if dest in servers:
		print "Server found"
		resultbackward.append(('server',dest,'Destination'))	
	else:
		
		run_in_loop(dest)
		print result
		# exit()
		resultbackward = result[::-1]
		resultbackward.append(('destination',dest,'Destination'))
		print resultbackward

		# exit()
		resultbackward.pop(0)

	resultforward.extend(resultbackward)


print resultforward 

f= open("routedata.js","w")
jsondata=''
jsondata = "data='["
for x in resultforward:
	jsondata = jsondata+'{"IP":"%s","name":"%s","int":"%s"},' %(x[1],x[2],x[0])
# data = '[{"IP" : "10.16.11.12", "name" : "Hello"},{"IP" : "10.16.11.10", "name" : "World"},{"IP" : "10.16.11.15", "name" : "Deepak"}]';
jsondata=jsondata[:-1]
jsondata = jsondata+"]'"
print jsondata

f.write(jsondata)
f.close()

webbrowser.open('route.html')

exit()

edges=[]
nodes=[]
labels=[]
interf=[]

nodes.append(host)
labels.append(host)

for x in resultforward:
	nodes.append(x[1])
	if x[2] is not None:
		labels.append(x[2])
	else:
		labels.append(x[1])	

for i in xrange(0,len(resultforward)-1):
	edges.append((resultforward[i][2],resultforward[i+1][2]))
edges.append((host,resultforward[0][2]))

print nodes
print edges
# exit()

# G.add_nodes_from(nodes)
G.add_nodes_from(labels)
G.add_edges_from(edges)
pos=nx.spring_layout(G)

# nx.draw_networkx_labels(G,pos=pos,nodelist=nodes,edgelist=edges,font_size=8)
plt.title(host+" to "+dest)

nx.draw(G,with_labels = True,label=labels,font_size=7)
plt.show()
