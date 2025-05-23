#!/bin/bash

# (C) Copyright 2025, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

# --- Configuration ---
FRESH_MODE=false
VENV_DIR=".venv"
PYTHON_BIN="python3"
REQUIRED_TOOLS="build twine"
DIST_DIR="dist"
INSTALL_AFTER_BUILD=false

# --- Helper Functions ---
display_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Builds the python package.

Options:
  --fresh    Build from scratch (removes $VENV_DIR).
  --install  After having build the package install it.
  -h, --help Display this help message.
EOF
}
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# --- Argument Parsing ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --fresh) FRESH_MODE=true; shift ;;
        --install) INSTALL_AFTER_BUILD=true; shift ;;
        -h|--help) display_help; exit 0 ;;
        *) display_help; error_exit "Unknown option: $1" ;;
    esac
done

# --- Script start ---
echo "Starting project build process..."

# Clean build directory if --fresh is set
if [ "$FRESH_MODE" = true ]; then
    if [ -d "$VENV_DIR" ]; then
        echo "Fresh build requested. Removing $VENV_DIR..."
        if ! rm -rf "$VENV_DIR"; then
            error_exit "Failed to remove venv directory '$VENV_DIR'."
        fi
    else
        echo "Fresh build requested, but $VENV_DIR does not exist. Skipping removal."
    fi
fi

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' not found. Creating it..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        error_exit "Error: Failed to create virtual environment. Ensure $PYTHON_BIN is installed."
    fi
    echo "Virtual environment created."
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    error_exit "Error: Failed to activate virtual environment. Check path: $VENV_DIR/bin/activate"
fi
echo "Virtual environment activated."

# Install required build tools if not already present
echo "Installing required tools ($REQUIRED_TOOLS) into the virtual environment..."
pip install $REQUIRED_TOOLS
if [ $? -ne 0 ]; then
    deactivate
    error_exit "Error: Failed to install required tools."
fi
echo "Required tools installed."

# Build the project
echo "Building the project..."
python -m build
if [ $? -ne 0 ]; then
    deactivate
    error_exit "Error: Project build failed."
fi
echo "Project built successfully! Look for distributable files in the 'dist/' directory."

# Install the built package if requested
if [ "$INSTALL_AFTER_BUILD" = true ]; then
    echo "Installing the package in the venv"

    # Find the built wheel file
    WHEEL_FILE=$(find "$DIST_DIR" -name "*.whl" -print -quit)

    if [ -z "$WHEEL_FILE" ]; then
        echo "Warning: No wheel file found in '$DIST_DIR/'. Cannot perform local install."
    else
        echo "Attempting to install '$WHEEL_FILE' locally into the virtual environment..."
        pip install "$WHEEL_FILE" --force-reinstall
        if [ $? -ne 0 ]; then
            deactivate
            error_exit "Error: Local installation of the package failed."
        fi
        echo "Package installed successfully into the virtual environment."
        echo "You can now test your package (e.g., run 'generate-interfaces --help')."
    fi
fi

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate
echo "Build process completed."
