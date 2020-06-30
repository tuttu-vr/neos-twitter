#!/bin/bash

set -x

mkdir -p server/common
mkdir -p collector/common
cp -r common/* server/common/
cp -r common/* collector/common/

docker-compose build
