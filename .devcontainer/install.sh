#!/bin/bash
set -e

sudo rm -f /etc/apt/sources.list.d/yarn.list

sudo apt-get update
sudo apt-get install -y graphviz socat


pip install --upgrade pip
pip install poetry

# We use venv to deal with weird conflicts.
# we force that to the vscode folder, because that's faster.
VENV_PATH="/home/vscode/.venv"
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
poetry config virtualenvs.create false

poetry lock
poetry install --no-interaction
