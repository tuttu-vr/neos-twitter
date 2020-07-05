#!/bin/bash

for req in $(find ../ -name requirements.txt)
do
    pip install -r $req
done

mkdir -p common
cp -r ../common/* common
