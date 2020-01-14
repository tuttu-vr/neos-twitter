#!/bin/bash
set -x
sleep 10
curl http://127.0.0.1:4040/api/tunnels --silent | jq '.tunnels | .[] | .public_url'
