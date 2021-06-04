#!/bin/bash
ROOT=/opt/dp

pip3 install virtualenv

cd $ROOT/front

npm install postcss-cli autoprefixer sass postcss minify -g

virtualenv -p /usr/bin/python3 venv
source venv/bin/activate

pip3 install -r scripts/requirements.txt

cd $ROOT
pip3 install -e .

