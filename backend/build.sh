#!/usr/bin/env bash
# Render build script for KisanMitra Backend
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
