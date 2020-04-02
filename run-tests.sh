#!/bin/bash

sqlite3 data/test.db < data/init-db.sql

python3 -m nose sim
