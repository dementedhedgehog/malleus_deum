#!/usr/bin/env python
# coding=utf-8
"""

  Builds pdfs from the xml files.
 
  Xelatex installer for windows.
  http://www.texts.io/support/0002/
  (May need to set up the proxy for downloading packages)

   Erroneous fontspec error:
   This is quite likely caused by mismatched versions of fontspec and expl3.
   Update at least those packages using the MikTeX Update tool.

"""
import sys
import os
from getopt import getopt, GetoptError
from os.path import abspath, join, splitext, dirname, exists, basename
from os import mkdir, makedirs
import codecs
from subprocess import call, check_output, CalledProcessError
from copy import deepcopy
from shutil import copy
from io import BytesIO
import re
import platform

src_dir = abspath(join(dirname(__file__)))
third_party_dir = join(src_dir, "third_party")
sys.path.append(src_dir)
sys.path.append(third_party_dir)

from jinja2 import Template, Environment, FileSystemLoader

from doc import Doc
from abilities import AbilityGroups
from monsters import MonsterGroups
from archetypes import Archetypes
from latex_formatter import LatexFormatter
from spreadsheet_writer import write_summary_to_spreadsheet
import config
import utils


root_dir = abspath(join(src_dir, ".."))
build_dir = join(root_dir, "build")
docs_dir = join(root_dir, "docs")
pdfs_dir = join(root_dir, "pdfs")
styles_dir = join(root_dir, "styles").replace("\\", "/")
archetype_template_fname = "archetype_template.xml"

# latex preamble for the index.
index_str = """
\\documentclass{article}
\\usepackage{makeidx}
\\usepackage{hyperref}

% Override the default index \see behaviour and include the pageref.
\\renewcommand{\see}[2]{see #1 #2}

\\begin{document}
\\printindex
\\end{document}

"""


def usage(msg = "", return_code = 0):
    prog_name = basename(sys.argv[0])
    print(("Usage: %s -h | -s | -t | -x \n"
          "\n"
          "\t-h\tHelp! print this message.\n"
          "\t-c\tClean all the files before building, e.g. pdfs etc\n"
          "\t-C\tClean all the files and exit.\n"
          "\t-s\tFail slow!  Ignore xml errors and try and build the doc anyway.\n"
          "\t-t\tOnly do the template substitution don't parse the xml.\n"
          "\t-x\tDo the template substitution and parse the xml; don't build the doc.\n"
          "\t-l\tOnly build the latex doc; don't build the pdf.\n"
          "\n"
          "%s" % (prog_name, msg)))
    exit(return_code)


def find_xelatex():
    """
    Return a path to the xelatex executable on this platform.

    """
    if platform.system() == "Linux":
        xelatex_executable = "/usr/bin/xelatex"
    else:
        xelatex_executable = "C:/Program Files (x86)/MiKTeX 2.9/miktex/bin/xelatex.exe"
    return xelatex_executable


def xelatex(tex_fname, verbosity=0):
    """
    Run xelatex on the given tex file to produce a pdf.

    """
    global xelatex_executable
    if xelatex_executable is None:
        xelatex_executable = find_xelatex()

    cmd_line = [xelatex_executable,
                "-output-directory=%s" % build_dir, 
                "--halt-on-error",
                tex_fname]

    # get a copy of the environment with TEXINPUTS set.
    env = deepcopy(os.environ)
    
    if platform.system() == "Linux":
        # Add the local styles dir
        # The trailing // means that TeX programs will search recursively in that 
        # folder; the trailing colon means "append the standard value of TEXINPUTS" 
        # (which you don't need to provide).
        tex_inputs = styles_dir + "//:"

        env["TEXINPUTS"] = tex_inputs

        if verbosity > 0:
            print(("\n\nRun with:\n%s\n%s" % 
                   ("export TEXINPUTS=%s" % tex_inputs,
                    " ".join(cmd_line))))
        
    else:
        args.insert(1, "-include-directory=%s" % styles_dir)

        if verbosity > 0:
            print("\n\nRun with:\n%s" % " ".join(cmd_line))


    xelatex_output = ""
    xelatex_error = False
    try:
        xelatex_output = check_output(cmd_line, env=env)
    except CalledProcessError as e:
        xelatex_output = e.output
        xelatex_error = True

    # print xelatex output (filter out some of the spammy messages)
    if verbosity > 1:
        assert False
        print(xelatex_output)
    else:        
        filter_xelatex_output(xelatex_output)

    if xelatex_error:
        sys.exit("Failed to run xelatex on doc: %s" % tex_fname)

    # Rerun once to try and get cross-references right
    # (Throw away the trace this time)
    check_output(cmd_line)            
    return


def find_makeindex():
    """
    Return a path the makeindex executable (a latex tool).

    """
    if platform.system() == "Linux":
        makeindex = "/usr/bin/makeindex"
    else:
        makeindex = "C:/Program Files (x86)/MiKTeX 2.9/miktex/bin/makeindex.exe"
    return makeindex


def filter_xelatex_output(xelatex_output):
    """Filter out some noisy common latex errors that are not important."""

    # join up all the lines of the output so there's
    # one error per line 
    lines = []
    current_line = None
    for line in xelatex_output.split("\n"):

        # end 
        if line.strip() == "":        
            if current_line is not None:
                lines.append(current_line)
                current_line = None
        else:
            if current_line is not None:
                current_line += line
            else:
                 current_line = line

    if current_line is not None:
        lines.append(current_line)

    # filter lines
    for line_index in range(len(lines) -1, -1, -1):
        line = lines[line_index]
        
        if (line.startswith("(/usr/share/texlive/texmf-dist/tex/latex/") or 
            line.startswith("Underfull \hbox ") or 
            line.startswith("Overfull \hbox ") or 
            line.startswith("Overfull \hbox ") or 
            line.startswith("Overfull \vbox ") or 
            line.startswith("This is XeTeX")):
            del lines[line_index]

    for line in lines:
        print line
    return



def create_index(verbosity=0):
    print()
    print("===============================================")
    print("===============================================")
    print("     Create Index")
    print("===============================================")
    print("===============================================")
    
    # combine indexes
    index_entries = []
    index_regex = re.compile(
        "\\\\indexentry\{"
        "(?P<index_name>.*?)"
        "\}\{"
        "(?P<index_page>\d+)"
        "\}$")
    for fname, build_index, index_name in config.files_to_build:
        base_fname, _ = splitext(basename(fname))
        idx_fname = join(build_dir, base_fname + ".idx")

        with file(idx_fname) as f:
            for line in f.readlines():
                match_obj = index_regex.match(line)
                if match_obj is not None:
                    new_index_line = "\\indexentry{%s}{%s-%s}\n" % (
                        match_obj.group("index_name"), 
                        index_name,
                        match_obj.group("index_page"))
                    index_entries.append(new_index_line)
                else:
                    print "no match " + line[:-1]

    # write the combined .idx file
    index_idx = join(build_dir, "index.idx")
    with file(index_idx, "w") as f:
        f.write("".join(index_entries))

    # create an index.tex
    index_tex = join(build_dir, "index.tex")
    with file(index_tex, "w") as f:
        f.write(index_str)

    # run makeindex to ah make the index
    # (makeindex won't let you build an index outside of the cwd!)
    cmd_line = [makeindex, 
                #"-q",
                basename(index_idx)]
                #index_idx]
    print " ".join(cmd_line)
    
    if verbosity > 0:
        print(("\n\n\n" + " ".join(cmd_line)))
    call(cmd_line, cwd = build_dir)


    print "-------------------------"
    # build the index.pdf
    #print index_
    xelatex(index_tex)
    # cmd_line = [xelatex, "-output-directory=%s" % build_dir, index_tex]
    # if verbosity > 0:
    #     print(("\n\n\n" + " ".join(cmd_line)))
    #call(cmd_line, env = env)

    #print cmd_line
    #call(cmd_line)

    # move the pdf from the build dir to the pdfs dir
    pdf_fname = join(build_dir, "index.pdf")
    if exists(pdf_fname):
        copy(pdf_fname, pdfs_dir)
    else:
        print("Missing index pdf: %s" % pdf_fname)
    return



def build_doc(template_fname, verbosity, archetype = None):
    """
    Archetype required only when building archetype docs.

    """
    # archetypes all use the same template.. but we don't want to 
    # put them in the same doc file.
    if archetype is not None:
        doc_fname = archetype.get_id()
    else:
        doc_fname = template_fname

    # base name .. no extension
    doc_base_fname, _ = splitext(basename(doc_fname))
    xml_fname = join(build_dir, "%s.xml" % doc_base_fname)
    pdf_fname = join(build_dir, "%s.pdf" % doc_base_fname)
    tex_fname = join(build_dir, "%s.tex" % doc_base_fname)
    # makeindex won't write to files outside of the cwd.
    # We don't want a path here.  Just a filename
    idx_fname = "%s.idx" % doc_base_fname

    print("===============================================")
    print("Building %s " % doc_fname)
    print("===============================================")

    # get the path to the xml filename, e.g. docs/core.xml
    full_template_fname = join(docs_dir, template_fname)

    # the very first thing we do is run the xml through a template engine 
    # (Doing it like this allows us to include files relative to the doc 
    # dir using Jinjas include directive).
    template = jinja_env.get_template(template_fname)
    xml = template.render(ability_groups = ability_groups,
                          monster_groups = monster_groups,
                          archetypes = archetypes,
                          archetype = archetype,
                          config = config,
                          add_index_to_core = config.add_index_to_core,
                          doc_name = doc_base_fname)

    # drop out early?
    if template_only:
        print("Template only! ...")
        print(xml.encode('ascii', 'xmlcharrefreplace'))
        return

    # write the post-processed xml to the build dir 
    # (has all the included files in it).
    with codecs.open(xml_fname, "w", "utf-8") as f:
       f.write(xml)
            
    # parse an xml documento
    doc = Doc(xml_fname)        
    if not doc.parse():
        print("Problem parsing the xml.")
        exit(0)

    if not doc.validate() and fail_fast:
        print("Fatal: xml errors are fatal!")
        print("Run with the -s cmd line option to ignore xml errors.")
        exit(0)

    # drop out early?
    if parse_only:
        print("Parse only!")
        return            

    # check we have a book_node to format
    if not doc.has_book_node():
        if verbosity >= 1:
            print("No book node to format in document: %s IGNORING!" % doc_fname)
        return

    # build the latex document by converting the xml into tex
    with codecs.open(tex_fname, "w", "utf-8") as f:           
        latex_formatter = LatexFormatter(f)
        errors = doc.format(latex_formatter)
        if len(errors) > 0:
            print("Errors:")
            for error in errors:
                print("\t%s\n\n\n" % error)
                
            if fail_fast:
                sys.exit()

    # exit early if we don't build pdfs
    if latex_only:
        return

    # converts the latex to pdf
    xelatex(tex_fname, verbosity=verbosity)

    # run makeindex to, ah, make the index
    # (makeindex won't let you build an index outside of the cwd!)
    return_code = call([makeindex, 
                        # "-q", 
                        idx_fname], cwd = build_dir)
    if return_code != 0:
        sys.exit("Failed to run makeindex on %s" % idx_fname)

    # Copy the pdf from the build dir to the pdfs dir
    copy(pdf_fname, pdfs_dir)

    print("===============================================")
    print(("   Finished building %s " % doc_fname))
    print("===============================================\n")
    return


def clean():
    """
    Delete all the build artifacts (tex, etc) and the pdfs.

    """
    for fname in os.listdir(build_dir):
        _, ext = splitext(fname)
        if ext in (".tex", ".log", ".toc", ".aux", ".idx", ".ind", 
                   ".xlsx", ".pdf", ".xml", ".ilg", ".out"):
            fname = join(build_dir, fname)
            os.remove(fname)

    for fname in os.listdir(pdfs_dir):
        print fname
        if fname.endswith(".pdf"):
            fname = join(pdfs_dir, fname)
            os.remove(fname)
    return


if __name__ == "__main__":
    try:
        opts, args = getopt(
            sys.argv[1:],
            "chxvtslC",
            ["help", "clean", "template_only", "parse_xml", "verbose", "fail_slow",
             "no_index", "clobber", "build_latex"])

    except GetoptError as err:
        usage(msg = str(err), return_code = 2)        

    verbosity = 0
    template_only = False
    parse_only = False
    fail_fast = True
    no_index = False
    latex_only = False
    debug = True
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbosity += 1
            
        elif o in ("-h", "--help"):
            usage()

        elif o in ("-c", "--clean"):
            clean()            

        elif o in ("-C", "--clobber"):
            clean()
            sys.exit()

        elif o in ("-s", "--fail_slow"):
            fail_fast = False
            
        elif o in ("-t", "--template_only"):
            # create the template  only (don't build the doc
            template_only = True

        elif o in ("-p", "-x", "--parse_only"):
            # parse only (don't build the doc)
            parse_only = True

        elif o in ("-l", "--build_latex"):
            # parse only (don't build the doc)
            latex_only = True

        elif o in ("--no_index", ):
            # don't create the index
            no_index = True
            
        else:
            raise Exception("unhandled option")

    # check xelatex exists.
    xelatex_executable = find_xelatex()
    assert exists(xelatex_executable)
    if verbosity > 1:
        print "Using xelatex at %s" % xelatex_executable

    # check makeindex exists.
    makeindex = find_makeindex()
    assert exists(makeindex), "Can't find makeindex at %s" % makeindex
    if verbosity > 1:
        print "Using makeindex at %s" % makeindex

    # make any dirs we need
    if not exists(build_dir):
        mkdir(build_dir)

    if not exists(pdfs_dir):
        mkdir(pdfs_dir)

    # load the abilities
    abilities_dir = join(root_dir, "abilities")
    ability_groups = AbilityGroups()
    if not ability_groups.load(abilities_dir, fail_fast = fail_fast) and fail_fast:
        print("Failing fast")
        sys.exit()
    
    # load the archetypes
    archetype_dir = join(root_dir, "archetypes")
    archetypes = Archetypes()
    archetypes.load(ability_groups, archetype_dir, fail_fast = fail_fast)

    # load the monsters
    monsters_dir = join(root_dir, "monsters")
    monster_groups = MonsterGroups()
    monster_groups.load(monsters_dir, fail_fast = fail_fast)

    # get a jinja environment
    docs_dir  = join(root_dir, "docs")
    jinja_env = Environment(
        loader = FileSystemLoader(docs_dir),
        keep_trailing_newline = True,
        trim_blocks = False,
        lstrip_blocks = False)
    jinja_env.filters['convert_to_roman_numerals'] = utils.convert_to_roman_numerals

    # Add the local styles dir
    # The trailing // means that TeX programs will search recursively in that 
    # folder; the trailing colon means "append the standard value of TEXINPUTS" 
    # (which you don't need to provide).
    #tex_inputs = styles_dir + "//:"

    # get a copy of the environment with TEXINPUTS set.
    #env = deepcopy(os.environ)
    #env["TEXINPUTS"] = tex_inputs

    for doc_xml_fname, _, _ in config.files_to_build:        
        build_doc(doc_xml_fname, verbosity=verbosity)

    for archetype_id, _, _ in config.archetypes_to_build:
        archetype = archetypes[archetype_id]
        build_doc(archetype_template_fname, archetype = archetype, verbosity=verbosity)

    if parse_only or template_only or latex_only:
        sys.exit()
    
    #
    # Create the index.pdf
    #
    if not no_index:
        create_index(verbosity=verbosity)

    # save summary details to a spreadsheet (for analysis)
    spreadsheet_fname = join(build_dir, "summary.xlsx")
    write_summary_to_spreadsheet(spreadsheet_fname, ability_groups, archetypes)

