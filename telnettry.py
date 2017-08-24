import sys
import telnetlib
# HOST = "10.16.11.139"
# HOST = "10.16.11.248"
HOST = '10.16.11.245'
# HOST = "10.50.1.2"
user = 'admin'
password = '$ic@Sty#07&'
# timeout = 10

print 'Connecting...'

try:
	tn = telnetlib.Telnet(HOST, timeout=2)
	tn.open(HOST)
except Exception as e:
	print e

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
print op
l = len(command)
op = op.split()
op = op[l:-1]
root = op[4]

command = 'sh cdp neighbors '+root+' detail | include IP\n'
tn.write(command)
command = command.split()
op = tn.read_until("#",timeout=2)
l = len(command)
op = op.split()
op = op[l:-1]
rootip = op[-1]	
print root+"---->"+rootip

tn.close()
  