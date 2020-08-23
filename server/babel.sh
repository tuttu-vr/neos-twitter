#!/bin/bash

cd $(dirname $0)

pybabel extract -F babel.cfg -k lazy_gettext -o translates.pot .
pybabel update -i translates.pot -d translations
pybabel compile -d translations
