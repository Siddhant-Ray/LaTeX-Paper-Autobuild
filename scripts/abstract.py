import re
import sys
import os

from locations import abstract_file, target_abstract_file

# Path: scripts/abstract.py

class ParseAbstract:

    def __sanitize(self, text):
        # replace abstract environment if existing
        text = text.replace("\\begin{abstract}", "")
        text = text.replace("\\end{abstract}", "")

        # replace text between \ and \ with text
        text = re.sub(r"\\(.*?)\\", r"\1", text)

        # remove tilde (non-breaking whitespace)
        text = text.replace("~", " ")

        # remove backslash for inter-word spacing after period
        text = text.replace(".\\ ", ". ")

        # replace %, ~, ...
        text = text.replace("\\%", "<<PERCENT>>")  # to disambiguate with comments
        text = text.replace("\\textasciitilde ", "~")  # with space
        text = text.replace("\\textasciitilde", "~")  # without space
        text = text.replace("\\ldots", "...")
        text = text.replace("\\dots", "...")
        
        # Replace line breaks
        text = text.replace("\\\\", " ")

        # Replace longer than single space
        text = re.sub(r"\s+", " ", text)

        # remove comments
        text = re.sub(r"\n%[^\n]*", r"", text, re.M)
        text = re.sub(r'%(.*)', '', text)
        text = text.replace("<<PERCENT>>", "%")  # re-introduce percent characters

        # remove hard wraps
        text = re.sub(r"\n[\n]+", "<<PARAGRAPH>>", text)
        text = text.replace("\n", " ")

        # add markdown for emphasis
        text = re.sub(r'\\emph{([0-9a-zA-Z-\' \.,/]+)}', r"_\1_", text)

        # replace text variants by standard text
        text = re.sub(r'\\text{([0-9a-zA-Z-\' \.,/]+)}', r"\1", text)
        text = re.sub(r'\\textsc{([0-9a-zA-Z-\' \.,/]+)}', r"\1", text)
        text = re.sub(r'\\textrm{([0-9a-zA-Z-\' \.,/]+)}', r"\1", text)
        text = re.sub(r'\\textsf{([0-9a-zA-Z-\' \.,/]+)}', r"\1", text)

        # remove xspace
        text = text.replace("\\xspace ", " ")
        text = text.replace("\\xspace.", ".")
        text = text.replace("\\xspace,", ",")
        text = text.replace("\\xspace:", ":")
        text = text.replace("\\xspace'", "'")
        # (xspace results in warning in other cases)

        # remove hyphenation indicators
        text = text.replace("\-", "")

        # re-introduce paragraphs
        text = text.replace("<<PARAGRAPH>>", "\n\n")

        # strip whitespace
        text = text.strip()

        return text

    @staticmethod
    def __is_sanitized(text):
        # remove math, because math may contain backslashes
        no_math_text = re.sub(r'\$.*\$', "", text)

        if no_math_text.find("\\") != -1:
            return False
        else:
            return True

    def get_abstract(self, abstract_text, allow_failure=True):
        abstract = self.__sanitize(abstract_text)
        
        res = "Abstract: {}".format(abstract)
        if not (self.__is_sanitized(abstract)):
            if allow_failure:
                res = "\n** WARNING: NOT ALL COMMANDS COULD BE REPLACED, INSPECT MANUALLY **\n\n" + res
            else:
                sys.exit(1)
        
        return abstract
    
    

if __name__ == "__main__":
    
    # Read abstract file
    with open(abstract_file, 'r', encoding='iso-8859-1') as f:
        raw_abstract = f.read()

    parser = ParseAbstract()
    replaced_abstract = parser.get_abstract(raw_abstract)

    with open(target_abstract_file, 'w', encoding='iso-8859-1') as f:
        f.write(replaced_abstract)



