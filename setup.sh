#!/usr/bin/env bash
# Pyswip is problematic: need to install from GitHub
echo "Installing Pyswip"
mkdir tmp && cd tmp
wget https://github.com/yuce/pyswip/archive/master.zip
unzip master.zip && cd pyswip-master
echo "Running setup"
python setup.py install
cd ..
rm master.zip
rm -rf pyswip-master
cd ..
rmdir tmp
echo "Installed Pyswip"

echo "Installing python requirments"
pip install -r requirements.txt



