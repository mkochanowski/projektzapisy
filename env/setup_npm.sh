# This cannot be run as root because node-sass is a piece of shit
# and will fail with EACCES
echo "Installing npm packages"

cd /vagrant/zapisy
./npm.sh i
