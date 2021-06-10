#!/bin/bash
echo "Getting started"

# Generate OpenAPI yaml file
python manage.py generateschema_mocked --file downtime.yaml

# Bundle docs into zero-dependency HTML file
npx redoc-cli bundle downtime.yaml && \
mv redoc-static.html downtime.html && \
echo "Changed name from redoc-static.html to index.html" && \
echo -e "\nDone!"