#!/bin/bash

# create venv, install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# run the application
cd ui
python health_bar.py