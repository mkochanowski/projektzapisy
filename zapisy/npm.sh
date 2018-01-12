#!/usr/bin/env bash
set -e

# Ensure the directory exists and has proper perms
sudo mkdir -p /webpack_modules
sudo chown `whoami`: /webpack_modules

# We'll want package-lock if it exists
if [ -e "package-lock.json" ]
then
	cp package-lock.json /webpack_modules
fi
cp package.json /webpack_modules

npm --prefix /webpack_modules $@

cp /webpack_modules/package.json .
cp /webpack_modules/package-lock.json .
