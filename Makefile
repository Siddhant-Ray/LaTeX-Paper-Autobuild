# Filename without space
# Path: Makefile
# .bib and .tex files with same name enables variable to work without extension
# else use $(FILE).bib and $(FILE).tex

FILE := main
OUTPUR_DIR := outputs
NO_APPENDIX_CONFIG := headers/config/noappendix.config
NO_ACKNOWLEDGEMENTS_CONFIG := headers/config/noacknowledgements.config

# Default with bibtex
pdf:
	@echo "Compiling $(FILE).tex to $(OUTPUR_DIR)/$(FILE).pdf"
	pdflatex $(FILE)
	bibtex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)
	mv $(FILE).pdf $(OUTPUR_DIR)/$(FILE).pdf

greyscale:
	@echo "Compiling $(FILE).tex to $(OUTPUR_DIR)/$(FILE)_grey.pdf"
	pdflatex '\PassOptionsToPackage{gray}{xcolor}\input $(FILE)'
	bibtex $(FILE)
	pdflatex '\PassOptionsToPackage{gray}{xcolor}\input $(FILE)'
	pdflatex '\PassOptionsToPackage{gray}{xcolor}\input $(FILE)'
	gs \
	-sDEVICE=pdfwrite \
	-dProcessColorModel=/DeviceGray \
	-dColorConversionStrategy=/Gray \
	-dPDFUseOldCMS=false \
	-dNEWPDF=false \
	-o $(FILE)_grey.pdf \
	-f $(FILE).pdf
	mv $(FILE)_grey.pdf $(OUTPUR_DIR)/$(FILE)_grey.pdf
	rm $(FILE).pdf

no-appendix:
	@echo "Compiling $(FILE).tex to $(OUTPUR_DIR)/$(FILE)_no-appendix.pdf"
	touch $(NO_APPENDIX_CONFIG)
	pdflatex $(FILE)
	bibtex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)
	mv $(FILE).pdf $(OUTPUR_DIR)/$(FILE)_no-appendix.pdf
	make clean-configs

no-acknowledgements:
	@echo "Compiling $(FILE).tex to $(OUTPUR_DIR)/$(FILE)_no-acknowledgements.pdf"
	touch $(NO_ACKNOWLEDGEMENTS_CONFIG)
	pdflatex $(FILE)
	bibtex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)
	mv $(FILE).pdf $(OUTPUR_DIR)/$(FILE)_no-acknowledgements.pdf
	make clean-configs

all:
	make pdf
	make greyscale
	make no-appendix
	make no-acknowledgements
	
.PHONY: clean
clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc

.PHONY: clean-configs
clean-configs:
	rm -rf headers/config/*.config

.PHONY: clean-all
clean-all: clean clean-configs
	rm -f $(OUTPUR_DIR)/*.pdf
	