#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./new-incident.sh INC-002"
    exit 1
fi

mkdir -p incidents/$1
cp -r baseline/* incidents/$1/

echo ""
echo "$1 created from baseline."
echo ""
echo "Next:"
echo "cd incidents/$1"
