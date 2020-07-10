#!/bin/sh

status=`curl -so /dev/null -k -w %{http_code} http://localhost/health`
if [ $? -eq 0 -a "$status" = "200" ]; then
    exit 0
else
    exit 1
fi
