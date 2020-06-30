#!/bin/bash

mkdir -p server/common
mkdir -p collector/common
cp -r common/* server/common/
cp -r common/* collector/common/
