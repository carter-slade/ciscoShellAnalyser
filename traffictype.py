import subprocess
import sys
import numpy as np
from matplotlib import pyplot as plt

fig = plt.figure()
ax = plt.axes()

plt.title('Please wait while the graph loads')
plt.draw()
plt.pause(0.5)

tcp = [0] * 100
udp = [0] * 100
icmp = [0] * 100

timescale = [x for x in range(1,101)]


# sys.os('path=%path's)
pktcnt = 20
if len(sys.argv) is 1:
	command = "tshark.exe -qz io,phs -i eth -c "+str(pktcnt)
# 10.50.81.233
else:
	host = sys.argv[1]
	command = "tshark.exe -qz io,phs -i eth -c "+str(pktcnt)+" host "+host

# -Y "ip.src == 192.168.0.10 and (http or http2)"
# command = "tshark.exe -qz io,phs -i eth -c "+str(pktcnt)
count = 0
# command = ["tshark.exe", "-qz","io,phs ","-i ","eth0","-c","1000"]
try:
	while True:
		try:
		    output = subprocess.check_output(command, shell=True)
		except subprocess.CalledProcessError as e:
		    print "An error has occured", e
		    raise

		result = {}
		lines = output.split('\n')
		lines = lines[3:]
		ax.clear()
		# print lines
		for row in lines:
			c = row.split()
			if len(c) is 3:
				result[c[0]]={}
				a = c[1].split(':')
				b = c[2].split(':')
				
				# print a
				# print b

				result[c[0]][a[0]]= a[1]
				result[c[0]][b[0]]= b[1]

		# print result
		# exit()		
		# print "tcp",result['tcp']['frames']
		# for x in result:
		# 	print x,result[x]
		tcpcnt = 0
		udpcnt = 0
		icmpcnt = 0
		if 'tcp' not in result:
			tcpcnt = 0
		else:
			tcpcnt = 100*int(result['tcp']['frames'])/pktcnt	
		if 'udp' not in result:
			udpcnt = 0
		else:
			udpcnt = 100*int(result['udp']['frames'])/pktcnt	
		if 'icmp' not in result:
			icmpcnt = 0
		else:
			icmpcnt = 100*int(result['icmp']['frames'])/pktcnt	

		if count<100:
			tcp[count]= tcpcnt
			udp[count]= udpcnt
			icmp[count]= icmpcnt
		else:
			tcp = tcp[1:]
			icmp = icmp[1:]
			udp = udp[1:]
			tcp.append(tcpcnt)
			icmp.append(icmpcnt)
			udp.append(udpcnt)

		# print tcp	
		ax.plot(timescale, tcp, color='r', label='tcp',linewidth=0.75)
		ax.plot(timescale, udp, color='g', label='udp',linewidth=0.75)
		ax.plot(timescale, icmp, color='b', label='icmp',linewidth=0.75)
		count+=1		
		plt.legend()
		plt.title('Traffic incoming')
		plt.pause(0.5)

except KeyboardInterrupt:
	print 'Interrupted'
					

