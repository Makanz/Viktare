#!/bin/bash

echo "======================================="
echo "   Viktspårare - Weight Tracker"
echo "======================================="
echo ""

# Kontrollera om Python är installerat
if ! command -v python3 &> /dev/null
then
    echo "FEL: Python3 är inte installerat!"
    echo ""
    echo "Installera Python3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi

echo "Python hittat! Startar Viktspåraren..."
echo ""

python3 weight_tracker_V1.py

if [ $? -ne 0 ]; then
    echo ""
    echo "======================================="
    echo "Ett fel uppstod!"
    echo "======================================="
    echo ""
    echo "Om du får felmeddelande om saknade moduler, kör:"
    echo "  pip3 install -r requirements.txt"
    echo ""
    echo "På vissa system kan du behöva:"
    echo "  pip3 install -r requirements.txt --break-system-packages"
    echo ""
fi
