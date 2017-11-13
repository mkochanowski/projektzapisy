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

p1 = subprocess.Popen(["python", "manage.py", "runserver", "0.0.0.0:8000"])
p2 = subprocess.Popen(["npm", "run", "dev"])

p1.wait()
p2.wait()
