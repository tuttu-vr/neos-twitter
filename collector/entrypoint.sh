#!/bin/ash

set -x

FILE="data/db.sqlite3"
CLIENT_NAME=${COLLECTOR_CLIENT_NAME:twitter}

if [ ! -e $FILE ]; then
  python src/common/lib/db.py
fi

PYTHONPATH=src python src/${CLIENT_NAME}_client/collector.py
