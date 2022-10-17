# Filename without space
# Path: Makefile
# .bib and .tex files with same name enables variable to work without extension
# else use $(FILE).bib and $(FILE).tex

FILE := main
OUTPUR_DIR := outputs
SCRIPTDIR := scripts
SECTIONSDIR := sections

# DIRs for conditional builds
NO_APPENDIX_CONFIG := headers/config/noappendix.config
NO_ACKNOWLEDGEMENTS_CONFIG := headers/config/noacknowledgements.config

LOG := $(OUTPUR_DIR)/$(FILE).log

########
# PDFS #
########

# Default with bibtex
# Make normal pdf
pdf:
	@echo "Compiling $(FILE).tex to $(OUTPUR_DIR)/$(FILE).pdf"
	pdflatex $(FILE)
	bibtex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)
	mv $(FILE).pdf $(OUTPUR_DIR)/$(FILE).pdf
	cp $(FILE).log $(OUTPUR_DIR)/$(FILE).log

# Make pdf in greyscale
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
	cp $(FILE).log $(OUTPUR_DIR)/$(FILE)_grey.log
	rm $(FILE).pdf

# Make pdf with no appendix
no-appendix:
	@echo "Compiling $(FILE).tex to $(OUTPUR_DIR)/$(FILE)_no-appendix.pdf"
	touch $(NO_APPENDIX_CONFIG)
	pdflatex $(FILE)
	bibtex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)
	mv $(FILE).pdf $(OUTPUR_DIR)/$(FILE)_no-appendix.pdf
	cp $(FILE).log $(OUTPUR_DIR)/$(FILE)_no-appendix.log
	make clean-configs

# Make pdf with no acknowledgements
no-acknowledgements:
	@echo "Compiling $(FILE).tex to $(OUTPUR_DIR)/$(FILE)_no-acknowledgements.pdf"
	touch $(NO_ACKNOWLEDGEMENTS_CONFIG)
	pdflatex $(FILE)
	bibtex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)
	mv $(FILE).pdf $(OUTPUR_DIR)/$(FILE)_no-acknowledgements.pdf
	cp $(FILE).log $(OUTPUR_DIR)/$(FILE)_no-acknowledgements.log
	make clean-configs

# Make everything
all:
	make pdf
	make greyscale
	make no-appendix
	make no-acknowledgements

############
# ABSTRACT #
############

# Parse abstract into a separate file
.PHONY: abstract
abstract:
	python3 $(SCRIPTDIR)/python/abstract.py 
	rm -rf $(SCRIPTDIR)/python/__pycache__

#########
# CLEAN #
#########

# Remove all temporary files
.PHONY: clean
clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc
	rm -f $(OUTPUR_DIR)/*.log

# Remove all configs
.PHONY: clean-configs
clean-configs:
	rm -rf headers/config/*.config

# Remove everything
.PHONY: clean-all
clean-all: clean clean-configs
	rm -f $(OUTPUR_DIR)/*.pdf
	
##########
# DOCKER #
##########

# For running locally only (not integrated with CI obviously)

# Docker command (sudo if needed)
DOCKER-CMD := ./scripts/docker.sh

# Current directory
PAPERDIR := $$(pwd)
# Docker image with TeX environment
IMAGE := ethsrilab/latex-plus:version-4.0
# Docker container name
CONTAINER := latex-plus-container

# Build docker image from Dockerfile
BUILD := $(DOCKER-CMD) build \
 		-t $(CONTAINER) .

# Run docker container
RUN := $(DOCKER-CMD) run \
		-it \
		--name $(CONTAINER) \
		$(CONTAINER)

# Launch a docker container using the image, which will provide a shell in the container
.PHONY: docker-run
docker-run: clean-container
	$(BUILD)
	$(RUN)

# Check for updates and remove the created docker container
.PHONY: clean-container
clean-container:
	$(DOCKER-CMD) pull $(IMAGE)
	$(DOCKER-CMD) rm /$(CONTAINER) 2>/dev/null || true

# Run everything in the container

# All above commands, run in the docker container

# Make all pdfs
.PHONY: docker-all
docker-all: clean-container
	$(RUN) make all
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/*.pdf outputs/
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/*.log outputs/

# Make normal pdf
.PHONY: docker-pdf
docker-pdf: clean-container
	$(RUN) make pdf
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main.pdf outputs
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main.log outputs

# Make pdf in greyscale
.PHONY: docker-greyscale
docker-greyscale: clean-container
	$(RUN) make greyscale
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main_grey.pdf outputs
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main_grey.log outputs

# Make pdf with no appendix
.PHONY: docker-no-appendix
docker-no-appendix: clean-container
	$(RUN) make no-appendix
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main_no-appendix.pdf outputs
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main_no-appendix.log outputs

# Make pdf with no acknowledgements
.PHONY: docker-no-acknowledgements
docker-no-acknowledgements: clean-container
	$(RUN) make no-acknowledgements
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main_no-acknowledgements.pdf outputs
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/main_no-acknowledgements.log outputs

# Make abstract
.PHONY: docker-abstract
docker-abstract: clean-container
	$(RUN) make abstract
	$(DOCKER-CMD) cp $(CONTAINER):/paper/outputs/abstract.txt outputs



	
