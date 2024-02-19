#!/usr/bin/env bash

# This script assumes a user and a service called "reddit-bot"
# exist, and also that a virtual env is available at .venv/
# The bot user should own all files in this repository.

su reddit-bot -c "git pull"
su reddit-bot -c ". .venv/bin/activate && pip install -r requirements-frozen.txt"
systemctl restart reddit-bot
