# requires pip install texsoup
import os

import locations
from mylogging import logger
from TexSoup import (RArg, TexArgs, TexCmd, TexEnv, TexNode, TexSoup,
                     TokenWithPosition)


class TextBlock:
    def __init__(self, raw_text, origin="?"):
        self.text = self.normalize(raw_text)
        self.file_origin = origin

    def __eq__(self, other):
        return self.text == other.text and self.file_origin == other.file_origin

    def normalize(self, text):
        text = text.replace("\n", " ")
        text = text.replace("~", " ")
        return text

    @staticmethod
    def check_skip(text):
        return len(text.strip()) < 3

    def __str__(self):
        return "TextBlock('" + self.text + "', origin = '" + self.file_origin + "')"


class TexDataProvider:

    extract_body_config = {
        # list of commands whose arguments should be included as body text
        "include_command_args": [
            "section",
            "subsection",
            "subsubsection",
            "paragraph",
            "caption",
            "item",
            "emph",
        ],
        # list of environments whose body should be skipped
        "skip_envs": ["$", "displaymath", "equation", "align", "comment"],
    }

    float_envs = ["table", "figure", "algorithm"]

    # list of relevant .tex files in the document tree
    imported_tex_files = []

    # cache holding parsed TexSoup objects for .tex files
    __parsed_tex_cache = {}

    # list of (file, error_message) of files with parsing errors
    parse_errors = []

    # returns the content of the given file as a string, excluding blocks between:
    #   %% >>> BEGIN NO PARSE
    #   ...
    #   %% >>> END NO PARSE
    def _get_parseable_tex_content(self, fname):
        src = ""
        skipping = False
        with open(fname, "r") as f:
            for line in f:
                if line.startswith("%% >>> BEGIN NO PARSE"):
                    skipping = True
                elif line.startswith("%% >>> END NO PARSE"):
                    skipping = False
                elif not skipping:
                    src += line
        return src

    # parses the given .tex file, caches its results
    def _parse_tex_file(self, fname):
        if not (fname in self.__parsed_tex_cache):
            logger.info("parsing file '%s'..." % (locations.get_short_filename(fname)))
            try:
                src = self._get_parseable_tex_content(fname)
                self.__parsed_tex_cache[fname] = TexSoup(src)
            except Exception as e:
                logger.warn(
                    "error while parsing file '{}':".format(
                        locations.get_short_filename(fname)
                    )
                )
                logger.warn("  {}".format(e))
                self.__parsed_tex_cache[fname] = TexSoup("")
                self.parse_errors.append(
                    (locations.get_short_filename(fname), "{}".format(e))
                )

        return self.__parsed_tex_cache[fname]

    # creates a TexDataProvider and parses the TeX import tree starting at 'root_tex_file'
    def __init__(self, root_tex_file):
        self.imported_tex_files = self.__get_recursive_imports(
            root_tex_file, os.path.dirname(root_tex_file)
        )

    # returns a generator providing all body text blocks of the document
    def get_body_text_blocks(self, skip_comments=True):
        for f in self.imported_tex_files:
            for t in self.get_body_text_blocks_in_file(f):
                yield t

    # returns a generator providing all body text blocks of the provided file
    def get_body_text_blocks_in_file(self, fname, skip_comments=True):
        soup = self._parse_tex_file(fname)
        for t in self.__process_tree(soup.expr.all, skip_comments):
            t.file_origin = fname
            yield t

    # returns a list of all package names used in the document
    def get_packages(self):
        packages = []
        for f in self.imported_tex_files:
            for p in self.get_packages_in_file(f):
                packages.append(p)
        return packages

    # returns a list of all package names used in a file
    def get_packages_in_file(self, file):
        packages = []
        soup = self._parse_tex_file(file)
        for package in soup.find_all("usepackage"):
            package_name = self.__get_required_arg(package.args, 0)
            names = package_name.split(",")  # to support \usepackage{a,b,c}
            for n in names:
                packages.append(n)
        return packages

    # returns all \newcommand declarations in the document
    def get_commands(self):
        commands = []
        for f in self.imported_tex_files:
            for p in self.get_commands_in_file(f):
                commands.append(p)
        return commands

    # returns all \newcommand declarations in a file
    def get_commands_in_file(self, file):
        commands = []
        soup = self._parse_tex_file(file)
        for command in soup.find_all("newcommand"):
            if len(command.args) > 0:
                commands.append(command.args[0].value)
        return commands

    # returns the (raw) contents of the \title{} command in the document (none if not found or ambiguous)
    def get_title(self):
        titles = []
        for f in self.imported_tex_files:
            soup = self._parse_tex_file(f)
            for command in soup.find_all("title"):
                titles.append(command.args[0].value)
        if len(titles) != 1:
            return None
        return titles[0]

    # \newcommand declarations without any arguments in the document
    # returns a dictionary \commandname -> args
    def get_simple_replacement_commands(self):
        commands = {}
        for f in self.imported_tex_files:
            a = self.get_simple_replacement_commands_in_file(f)
            for p in a:
                commands[p] = a[p]
        return commands

    # \newcommand declarations without any arguments in 'file'
    # returns a dictionary \commandname -> args
    def get_simple_replacement_commands_in_file(self, file):
        commands = {}
        soup = self._parse_tex_file(file)
        for command in soup.find_all("newcommand"):
            if len(command.args) == 2:
                commands[command.args[0].value] = command.args[1].value.strip()
            elif len(command.args) == 3 and command.args[1].value == "0":
                commands[command.args[0].value] = command.args[2].value.strip()
        return commands

    # returns tuples (file, type, labels) for any found \\ref or \\eqref
    def get_ref_eqref(self):
        labels = []
        for f in self.imported_tex_files:
            soup = self._parse_tex_file(f)
            for command in soup.find_all("ref"):
                labels.append((f, "ref", command.args[0].value))
            for command in soup.find_all("eqref"):
                labels.append((f, "eqref", command.args[0].value))
        return labels

    # returns all labels that are assigned to any float in the document
    def get_float_labels(self):
        labels = []
        for f in self.imported_tex_files:
            soup = self._parse_tex_file(f)
            for label in soup.find_all("label"):
                if isinstance(label.parent.expr, TexEnv) and (
                    label.parent.expr.name in self.float_envs
                ):
                    labels.append(label.string)
            for lst in soup.find_all("lstinputlisting"):
                # special treatment of 'lstinputlisting' command which directly assigns a label
                if len(lst.args) == 2:
                    raw_args = lst.args[0].value
                    parts = raw_args.split(",")
                    for p in parts:
                        lr = p.split("=")
                        if lr[0] == "label":
                            labels.append(lr[1])
        return labels

    # returns (caption, label, file, type) of all mis/-unlabeled floats in the
    # document
    # 'caption' is empty for floats that do not contain a caption
    # 'type':
    #    0 iff no label
    #    1 iff label but no caption
    #    2 iff label and caption, but in the wrong order
    def get_unlabeled_floats(self):
        floats = []
        for f in self.imported_tex_files:
            soup = self._parse_tex_file(f)
            for fig in soup.find_all("figure"):
                has_label = False
                has_caption = False
                label_before_caption = False
                caption = ""
                label = ""
                for c in fig.children:
                    if isinstance(c.expr, TexCmd):
                        if c.expr.name == "caption":
                            caption = c.expr.args[0].value
                            has_caption = True
                        elif c.expr.name == "label":
                            label = c.expr.args[0].value
                            has_label = True
                            if not has_caption:
                                label_before_caption = True
                if not has_label:
                    floats.append((caption, label, f, 0))
                elif has_label and not has_caption:
                    floats.append((caption, label, f, 1))
                elif has_label and has_caption and label_before_caption:
                    floats.append((caption, label, f, 2))
        return floats

    # returns all labels referenced within any \cref command
    def get_crefs(self):
        labels = []
        for f in self.imported_tex_files:
            soup = self._parse_tex_file(f)
            for command in soup.find_all("cref"):
                labels.append(command.args[0].value)
            for command in soup.find_all("ref"):
                labels.append(command.args[0].value)
        return labels

    # check if file with name 'fname' should be exempted from LaTeX parsing
    def __check_skip_file(self, fname):
        if fname == locations.appendix_labels_file and not os.path.isfile(fname):
            return True
        with open(fname, "r") as f:
            first_line = f.readline()
            if first_line.startswith("% GNUPLOT:"):
                return True

    # returns the list of files (non-recursively) imported in the .tex file 'f'
    def __get_imports(self, f, root_dir):
        soup = self._parse_tex_file(f)
        l = []

        # resolve subimports
        for subimport in soup.find_all("subimport"):
            path = subimport.args[0].value + subimport.args[1].value
            l.append(path)

        # resolve imports
        for _import in soup.find_all("import"):
            path = _import.args[0].value
            l.append(path)

        # resolve includes
        for include in soup.find_all("include"):
            path = include.args[0].value
            l.append(path)

        # resolve inputs
        for _input in soup.find_all("input"):
            path = _input.args[0].value
            l.append(path)

        def add_extension_and_root(f):
            ret = os.path.join(root_dir, f)
            if not os.path.isfile(ret):
                if not f.endswith(".tex"):
                    ret += ".tex"
            return ret

        l = [add_extension_and_root(f) for f in l]
        l = [f for f in l if (not self.__check_skip_file(f))]
        return l

    # returns the list of files imported in the .tex file 'f' (recursively)
    def __get_recursive_imports(self, f, root_dir):
        queue = [f]
        l = []
        while len(queue) > 0:
            f = queue.pop()
            if f not in l:
                l.append(f)
                queue += self.__get_imports(f, root_dir)
        return l

    def __get_required_args(self, args: TexArgs):
        ret = []
        for a in args:
            if a.type == "required":
                ret.append(a)
        return ret

    def __get_required_arg(self, args: TexArgs, i: int):
        req = self.__get_required_args(args)
        return req[i].value

    def __process_command(self, cmd, skip_comments):
        if cmd.name in self.extract_body_config["include_command_args"]:
            for arg in cmd.args:
                for t in self.__process_node(arg, skip_comments):
                    yield t

    def __process_node(self, node, skip_comments):
        if isinstance(node, TexEnv):
            if not (node.name in self.extract_body_config["skip_envs"]):
                for t in self.__process_tree(node.all, skip_comments):
                    yield t
        elif isinstance(node, TexCmd):
            for t in self.__process_command(node, skip_comments):
                yield t
        elif isinstance(node, TokenWithPosition):
            t = str(node.text).strip()
            if not (
                TextBlock.check_skip(t)
                or (len(t) > 0 and t[0] == "%" and skip_comments)
            ):
                yield TextBlock(t)
        elif isinstance(node, RArg):
            t = node.value
            if not TextBlock.check_skip(t):
                yield TextBlock(t)
        elif isinstance(node, str):
            t = node
            if not TextBlock.check_skip(t):
                yield TextBlock(t)
        else:
            pass  # TODO what to do here?

    def __process_tree(self, tex_tree, skip_comments):
        for n in tex_tree:
            for t in self.__process_node(n, skip_comments):
                yield t
