#!/bin/bash

for req in $(find ../ -name requirements.txt)
do
    pip install -r $req
done
pip install flake8

mkdir -p common
cp -r ../common/* common
