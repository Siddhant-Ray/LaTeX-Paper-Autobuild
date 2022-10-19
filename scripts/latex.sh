#!/bin/bash

# Run LaTex build without the Makefile if needed (base pdf only, no advanced features)

# USAGE: ./scripts/latex.sh -output-directory=$OUTPUT_DIR $ROOT_LATEX_FILE

# Go back to the root directory
cd $(dirname $0)/..
echo "Running latex build from $(pwd)"

# Run latex build
# Set output directory to the current directory

OUTPUT_DIR=$(pwd)/outputs

echo "Output directory: $OUTPUT_DIR"

ROOTFILE=main

# Run latex build

# Clean if main.pdf exists
if [ -f "$OUTPUT_DIR/$ROOTFILE.pdf" ]; then
    echo "Cleaning $OUTPUT_DIR/$ROOTFILE.pdf"
    rm $OUTPUT_DIR/$ROOTFILE.pdf
fi

# Clean first 
rm sections/*.aux
rm *.aux

pdflatex $ROOTFILE
bibtex $ROOTFILE
pdflatex $ROOTFILE
pdflatex $ROOTFILE

# Copy to output directory
mv $ROOTFILE.pdf $OUTPUT_DIR/$ROOTFILE.pdf

# Clean current directory
echo "Cleaning aux files in $(pwd)"

rm *.aux *.bbl *.blg *.log *.out




