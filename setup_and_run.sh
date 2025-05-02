#!/bin/bash

# Script to set up a virtual environment and run the SVG optimizer

# Configuration
VENV_DIR="venv"
PYTHON="python3"
CONSOLE_SCRIPT="svg_optimizer_console.py"
PYQT5_SCRIPT="svg_optimizer_pyqt5.py"
REQUIREMENTS=("lxml" "PyQt5" "Pillow")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v $PYTHON &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3 from https://www.python.org/downloads/ and try again.${NC}"
    exit 1
fi

# Create and activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    $PYTHON -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment.${NC}"
        exit 1
    fi
else
    echo "Virtual environment already exists in $VENV_DIR."
fi

# Activate virtual environment
source $VENV_DIR/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment.${NC}"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
for pkg in "${REQUIREMENTS[@]}"; do
    pip install $pkg
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to install $pkg. Check your internet connection or pip version.${NC}"
        deactivate
        exit 1
    fi
done
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Check if scripts exist
if [ ! -f "$CONSOLE_SCRIPT" ] && [ ! -f "$PYQT5_SCRIPT" ]; then
    echo -e "${RED}Error: Neither $CONSOLE_SCRIPT nor $PYQT5_SCRIPT found in the src directory.${NC}"
    deactivate
    exit 1
fi

# Prompt user to choose which script to run
echo "Which SVG optimizer would you like to run?"
if [ -f "$CONSOLE_SCRIPT" ]; then
    echo "1) Console-based optimizer ($CONSOLE_SCRIPT)"
fi
if [ -f "$PYQT5_SCRIPT" ]; then
    echo "2) PyQt5-based GUI optimizer ($PYQT5_SCRIPT)"
fi
echo "Enter 1 or 2 (or press Enter to exit):"

read choice

case $choice in
    1)
        if [ -f "$CONSOLE_SCRIPT" ]; then
            echo "Running $CONSOLE_SCRIPT..."
            $PYTHON $CONSOLE_SCRIPT "$@"
        else
            echo -e "${RED}Error: $CONSOLE_SCRIPT not found.${NC}"
        fi
        ;;
    2)
        if [ -f "$PYQT5_SCRIPT" ]; then
            echo "Running $PYQT5_SCRIPT..."
            $PYTHON $PYQT5_SCRIPT
        else
            echo -e "${RED}Error: $PYQT5_SCRIPT not found.${NC}"
        fi
        ;;
    *)
        echo "Exiting without running any script."
        ;;
esac

# Deactivate virtual environment
deactivate