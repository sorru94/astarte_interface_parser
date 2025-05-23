#!/bin/bash

# (C) Copyright 2025, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

# --- Configuration ---
PYTHON_BIN="python3"
VENV_DIR=".venv"

# --- Helper Functions ---
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# --- Environment and Dependency Setup ---
echo "Setting up Python environment and dependencies..."

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

# --- Run pytest ---
echo "Running pytest..."
if ! pytest; then
    error_exit "pytest run failed."
fi
