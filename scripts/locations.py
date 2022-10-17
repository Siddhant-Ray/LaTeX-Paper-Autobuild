import os 
import sys

# Path: scripts/locations.py

# Get the path to the directory containing this script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Abstract
abstract_file = os.path.join(script_dir, '../sections/abstract.tex')
target_abstract_file = os.path.join(script_dir, '../outputs/abstract.txt')