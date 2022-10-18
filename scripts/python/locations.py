import os
import sys

# Path: scripts/locations.py


def get_short_filename(filename):
    return os.path.relpath(filename, root)


# Get the path to the directory containing this script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Abstract
abstract_file = os.path.join(script_dir, "../../sections/abstract.tex")
target_abstract_file = os.path.join(script_dir, "../../outputs/abstract.txt")

# Get root directory
root = os.path.join(script_dir, "../../")

# Output dir
output_dir = os.path.join(script_dir, "../../outputs/")

# Script log dir
script_log_dir = os.path.join(script_dir, "../../outputs/script-logs/")

# Script log file
calling_file = sys.modules["__main__"].__file__
calling_file_name = os.path.basename(calling_file)
script_log_file = os.path.join(script_log_dir, "logs-{}.log".format(calling_file_name))
