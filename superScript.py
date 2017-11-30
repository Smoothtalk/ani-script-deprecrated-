import sys
import os
import vars

#Duckwad Stinx

os.chdir(vars.script_loc)

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]

#sys.argv = ['synckkk.py', arg1, arg3]
#execfile('synckkk.py')

sys.argv = ['sync.py', arg1, arg2, arg3]
execfile('sync.py')
