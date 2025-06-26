#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies with specific versions
pip install --upgrade pip
pip install -r requirements.txt