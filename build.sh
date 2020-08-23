#!/bin/bash

set -x

mkdir -p server/common
mkdir -p collector/common
cp -r common/* server/common/
cp -r common/* collector/common/

if [ "x$1" = "xfull" ]; then
    cd server
    pybabel compile -d translations
    cd ..
    docker-compose build
fi
