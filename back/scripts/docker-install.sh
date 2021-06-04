#!/bin/bash
ROOT=/opt/dp

pip3 install virtualenv

cd $ROOT/back

virtualenv -p /usr/bin/python3 venv
source venv/bin/activate

cd $ROOT
pip3 install -e .

cd $ROOT/back
pip3 install -r scripts/requirements.txt
pip3 install -r ../scripts/requirements.txt
