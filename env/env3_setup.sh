# set up virtualenv
cd $HOME
python3.6 -m venv env3
source env3/bin/activate

# get requirements
pip install -r /vagrant/zapisy/requirements.development.txt

echo "Python 3.6 environment has been set up."
