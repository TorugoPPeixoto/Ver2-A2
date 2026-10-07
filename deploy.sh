#!/usr/bin/env bash
set -e

pip install -r requirements.txt
python backend/db/init_db.py
python main.py