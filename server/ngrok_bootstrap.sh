#!/bin/bash

# set -x

if [ "x$NGROK_AUTH_TOKEN" != "x" ]; then
  ngrok authtoken $NGROK_AUTH_TOKEN
  ngrok http 80
fi
