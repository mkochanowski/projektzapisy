#!/usr/bin/env bash
set -e

# We'll want package-lock if it exists
if [ -e "package-lock.json" ]
then
	cp package-lock.json /webpack_modules
fi
cp package.json /webpack_modules

npm --prefix /webpack_modules $@

cp /webpack_modules/package.json .
cp /webpack_modules/package-lock.json .
