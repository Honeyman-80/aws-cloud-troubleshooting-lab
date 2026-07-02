#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh fault-001"
    exit 1
fi

cd "$1" || exit 1

echo "Building..."
sam build || exit 1

echo ""
echo "Deploying..."
sam deploy --stack-name document-processing-sam
