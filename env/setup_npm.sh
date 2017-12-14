# This cannot be run as root because node-sass is a piece of shit
# and will fail with EACCES
echo "Installing npm packages"

# Fake typings for tsc
cp -R node/typings /node/

# Needed for module resolving
export NODE_PATH=/node/node_modules

# package.json needs to be in the --prefixed dir
cp /vagrant/zapisy/package.json /node/package.json

npm i --prefix /node
