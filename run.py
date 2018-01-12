import subprocess
import signal
import sys
import os
import time

def signal_handler(sig, frame):
	os.kill(p1.pid, signal.SIGTERM)
	os.kill(p2.pid, signal.SIGTERM)
	p1.wait()
	p2.wait()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

os.chdir("/vagrant/zapisy")

print(os.system("./npm.sh i"))
p1 = subprocess.Popen(["python", "manage.py", "runserver", "0.0.0.0:8000"])
p2 = subprocess.Popen(["npm", "run", "devw"])

p1.wait()
p2.wait()
