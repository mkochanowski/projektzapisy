# This cannot be run as root because node-sass is a piece of shit
# and will fail with EACCES
echo "Installing npm packages"

# package.json needs to be in the --prefixed dir
cp /vagrant/zapisy/package.json /webpack_modules/package.json

npm i --prefix /webpack_modules
