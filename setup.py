import vars
import os
user = raw_input('Are you Avi or Kanchana: ')
user.lower()

if(user == "avi"):
	command = "ssh -p" + vars.userport1 + ' ' + vars.a_host + " mkdir -p .ssh"
	os.system(command)
	print "one more time (we're going to celebrate)"
	command = "cat ~/.ssh/id_rsa.pub | ssh -p" + vars.userport1 + ' ' + vars.a_host + " \'cat >> ~/.ssh/authorized_keys\'"
	os.system(command)
elif(user == "kanchana"):
        command = "ssh -p" + vars.userport2 + ' ' + vars.k_host + " mkdir -p .ssh"
        os.system(command)
	print "one more time (we're going to celebrate)"
        command = "cat ~/.ssh/id_rsa.pub | ssh -p" + vars.userport2 + ' ' + vars.k_host + " \'cat >> ~/.ssh/authorized_keys\'"
        os.system(command)
else:
	print "you are not valid, bitch"
