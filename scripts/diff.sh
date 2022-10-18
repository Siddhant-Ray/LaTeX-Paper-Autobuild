#!/bin/bash
# Diff between current version and an older one (specified by commit hash)
#
# USAGE: ./diff.sh COMMIT_HASH

# collect argument
VERSION="$1"

# find directory containing this script
SCRIPTDIR="$(dirname "$(readlink -f "$0")")"
echo "Script directory: $SCRIPTDIR"

# run latexdiff
# https://ctan.org/pkg/latexdiff?lang=en
# - flatten: Replace\inputand\includecommands within body by the content ofthe
#   files in their argument
# - pdf: Generate pdf for diff
# - r: Compare to this revision
cd "$SCRIPTDIR/../"
latexdiff-git \
	--flatten \
	--pdf \
	-r "$VERSION" \
	main.tex

# move to output directory (overwrite)
cp main-diff*.tex main-diff*.pdf ./outputs/
rm main-diff*.tex main-diff*.pdf
