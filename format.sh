#!/bin/bash

# (C) Copyright 2025, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

# --- Configuration ---
CHECK_ONLY=false
VENV_DIR=".venv"
PYTHON_BIN="python3"
FORMAT_FILES=("./astarte_interface_parser/*.py" "./tests/*.py")

# --- Helper Functions ---
display_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Builds the python package.

Options:
  --check-only Run formaters in check mode without making changes.
  -h, --help   Display this help message.
EOF
}
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# --- Argument Parsing ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --check-only) CHECK_ONLY=true; shift ;;
        -h|--help) display_help; exit 0 ;;
        *) display_help; error_exit "Unknown option: $1" ;;
    esac
done

# --- Script start ---
echo "Starting project formatting process..."

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' not found. Creating it..."
    if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
        error_exit "Error: Failed to create virtual environment. Ensure $PYTHON_BIN is installed."
    fi
    echo "Virtual environment created."
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
# shellcheck source=/dev/null
if ! source "$VENV_DIR/bin/activate"; then
    error_exit "Error: Failed to activate virtual environment. Check path: $VENV_DIR/bin/activate"
fi
echo "Virtual environment activated."

# Install Astarte parser package (always reinstall)
echo "Installing Astarte parser package into the virtual environment..."
if ! pip install -q -e ".[static,linting,unit]"; then
    deactivate
    error_exit "Error: Failed to install Astarte parser."
fi
echo "Astarte parser installed."

# Run python formatter
CMD_ARGS="--line-length 100"
if [ "$CHECK_ONLY" = true ]; then
    CMD_ARGS="$CMD_ARGS --diff --check"
fi
for FILE_PATTERN in "${FORMAT_FILES[@]}"; do
    if ! black $CMD_ARGS $FILE_PATTERN; then
        deactivate
        error_exit "Error: Failed formatting files with black."
    fi
done

# Run isort formatter
CMD_ARGS="--profile black"
if [ "$CHECK_ONLY" = true ]; then
    CMD_ARGS="$CMD_ARGS --check-only"
fi
for FILE_PATTERN in "${FORMAT_FILES[@]}"; do
    if ! isort $CMD_ARGS $FILE_PATTERN; then
        deactivate
        error_exit "Error: Failed formatting files with isort."
    fi
done
