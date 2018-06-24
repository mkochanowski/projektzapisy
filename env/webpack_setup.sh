set -e

echo "Creating node_modules"

# We do this because while symlinks can be made to work on windows,
# the 255 path character limit might cause problems with npm's long
# recursively generated paths; the solution is to create node_modules
# outside the shared filesystem and link to it
# see https://blog.rudylee.com/2014/10/27/symbolic-links-with-vagrant-windows/
cd
mkdir node_modules
cd /vagrant/zapisy
ln -sf "$HOME/node_modules" node_modules

echo "Installing npm packages"
yarn
