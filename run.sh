#!/usr/bin/env sh

mysql -h db -uroot -p123456 < schema.sql
python /app/app.py

