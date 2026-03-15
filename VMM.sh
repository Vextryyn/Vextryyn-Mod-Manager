#!/bin/bash
# Navigate to the script's directory
cd "$(dirname "$0")"

# Optional: make sure Python 3 is used
PYTHON=$(which python3 || which python)

# Run the Python script
$PYTHON VMM.py

# Optional: keep terminal open after script finishes (for GUI-based double-click)
read -p "Press Enter to close..."
