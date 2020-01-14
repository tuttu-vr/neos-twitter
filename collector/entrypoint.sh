#!/bin/ash

set -x

FILE="data/db.sqlite3"

if [ ! -e $FILE ]; then
  python src/db_write.py
fi

python src/twitter_collector.py
