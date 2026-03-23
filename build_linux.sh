#!/bin/bash
# Captura el hash corto del commit actual
REV=$(git rev-parse --short HEAD)
# O si prefieres el tag: REV=$(git describe --tags)

echo "Compilando versión: $REV"

pyinstaller --noconfirm --onefile --windowed \
    --name "Convertidor_RA3_Linux_$REV" \
    --add-data "io_sead.py:." \
    --collect-all ttkbootstrap \
    --hidden-import pandas \
    --hidden-import PIL._tkinter_finder \
    --collect-submodules PIL \
    "convertidor_RA3.py"
