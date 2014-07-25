#!/bin/bash

python -m mongo_connector.connector \
    -m localhost:27017 \
    -t localhost:5000 \
    -d ~/coding/equations/equation_doc_manager.py \
    -n crawler.data
