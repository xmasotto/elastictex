#!/bin/bash

python -m mongo_connector.connector \
    -m localhost:27017 \
    -t localhost:5000 \
    -d elastictex_doc_manager \
    -n crawler.data $*
