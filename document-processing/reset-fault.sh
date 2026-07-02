#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./reset-fault.sh fault-001"
    exit 1
fi

rm -rf "$1"
mkdir "$1"
cp -r baseline/* "$1"/

echo "$1 has been reset to the baseline."
