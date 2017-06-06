import os

i = 0
for root, subdir, files in os.walk("."):
    if "urls.py" in files:
        

print("%d files removed" % i)
