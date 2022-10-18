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

pdflatex -output-directory=$OUTPUT_DIR $ROOTFILE
bibtex $ROOTFILE
pdflatex -output-directory=$OUTPUT_DIR $ROOTFILE
pdflatex -output-directory=$OUTPUT_DIR $ROOTFILE

# Clean all aux files in the output directory
echo "Cleaning aux files in $OUTPUT_DIR"
rm $OUTPUT_DIR/*.aux $OUTPUT_DIR/*.bbl $OUTPUT_DIR/*.blg $OUTPUT_DIR/*.log $OUTPUT_DIR/*.out $OUTPUT_DIR/*.toc
rm $OUTPUT_DIR/*.fls $OUTPUT_DIR/*.fdb_latexmk




