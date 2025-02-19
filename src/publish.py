#!/usr/bin/env python3
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
import subprocess
from subprocess import call, check_output, CalledProcessError
from copy import deepcopy
from shutil import copy
import io 
import re
import platform
import zipfile


src_dir = abspath(join(dirname(__file__)))
sys.path.append(src_dir)


# local
from doc import Doc
from db import DB
from latex_formatter import LatexFormatter
#from epub_formatter import EPubFormatter
from html_formatter import HtmlFormatter
from spreadsheet_writer import write_game_balance_spreadsheet, write_ability_summary_spreadsheet

# Graph creation stuff.. for analysis in the rationale doc.
import graphs
#import dice_pool_graph
import morale_graph
import d6_graph
import aspect_lifetime_graph

# FIXME: didn't want to deal with pdftk at the moment.
from character_sheet_writer import (
    create_character_sheet_for_archetype,
    create_blank_character_sheet)

from generate_level_progression_tables import generate_level_progression_tables
from generate_skill_tree import build_skill_trees
import config
import utils
from utils import (
    root_dir,
    build_dir,
    pdfs_dir,
    docs_dir,
    styles_dir,
    encounters_dir,
    modules_dir,
    release_dir,
    third_party_dir
)

sys.path.append(third_party_dir)
#from jinja2 import Template, Environment
from jinja2 import Environment, FileSystemLoader
#from jinja2.lexer import Token
#from  jinja2 import lexer


# Jinja2 doesn't like absolute paths.  We must supply a relative path
ARCHETYPE_TEMPLATE_FNAME = join("docs", "archetype_template.xml")
PATRON_TEMPLATE_FNAME = join("docs", "patron_template.xml")

def jinja_no_nones(x):
    """Custom jinja filter for formatting nones"""
    return "-" if (x is None or (type(x) == str and x.strip() == "")) else x

def jinja_log_to_console(text):
    """Custom jinja filter for printing log messages to console."""
    print(text, flush=True)
    return ''

def jinja_exit(text):
    """Custom jinja filter to exit the program (for debugging only)."""
    print(text, flush=True)
    sys.exit(1)



# latex preamble for the index.
index_str = r"""
\\documentclass{article}
\\usepackage{makeidx}
\\usepackage{hyperref}

% Override the default index \see behaviour and include the pageref.
\\renewcommand{\see}[2]{see #1 #2}

\\begin{document}
\\printindex
\\end{document}

"""

def die():
    raise Exception("Fatal Error")


def jinja_recursive_render(template, jinja_env, **values):
    """
    Recurse into expanded template variables .. so our templates can
    include templates which can include templates... etc and all the
    templates will be evaluated.

    """
    MAX_DEPTH=5
    depth = 0
    prev = template.render(**values)
    while True:

        new_template = jinja_env.from_string(prev)
        curr = new_template.render(**values)
        if curr != prev:
            prev = curr
        else:
            return curr

        depth += 1
        if depth >= MAX_DEPTH:
            break
        

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
           "\t-v\tVerbose.\n"
           "\t-r\tBuild a release zip with contents defined in config and version from docs/version.xml.\n"
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
        # ??
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
        #env["TEXMFHOME"] = "/home/blaize/proj/malleus_deum/fonts"

        print(("\n\nRun with:\n%s\n%s" % 
               ("export TEXINPUTS=%s" % tex_inputs, " ".join(cmd_line))))        
    else:
        args.insert(1, "-include-directory=%s" % styles_dir)
        print("\n\nRun with:\n%s" % " ".join(cmd_line))

    succeeded = False
    try:
        xelatex_output = check_output(cmd_line, env=env,
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True)            
        assert isinstance(xelatex_output, str)
        succeeded = True
    except CalledProcessError as e:
        xelatex_output = e.output
    
    # print xelatex output (filter out some of the spammy messages)
    if verbosity > 1:
        print(xelatex_output)
    else:  
        filter_xelatex_output(xelatex_output)

    if not succeeded:
        sys.exit(f"Failed to run xelatex on doc: {tex_fname} with error:\n{xelatex_output}")
        
    # Rerun once to try and get cross-references right
    # (Throw away the trace this time)
    try:
        check_output(cmd_line)
    except:
        succeded = False
        xelatex_output = e.output.decode()
        print(xelatex_output)
    return succeeded


def find_makeindex():
    """
    Return a path the makeindex executable (a latex tool).

    """
    if platform.system() == "Linux":
        makeindex = "/usr/bin/makeindex"
    else:
        # This is a guess.
        makeindex = "C:/Program Files (x86)/MiKTeX 2.9/miktex/bin/makeindex.exe"
    return makeindex


def filter_xelatex_output(xelatex_output):
    """Filter out some noisy common latex errors that are not important."""

    # join up all the lines of the output so there's
    # one error per line 
    lines = []
    current_line = None
    for line in xelatex_output.split("\n"):        
        if line.strip() == "":        
            if current_line is not None:
                lines.append(current_line)
                current_line = None
        else:
            if current_line is not None:
                current_line += " " + line
            else:
                current_line = line

    if current_line is not None:
        lines.append(current_line)

    # filter lines
    for line_index in range(len(lines) -1, -1, -1):
        line = lines[line_index]
        
        if (line.startswith("(/usr/share/texlive/texmf-dist/tex/latex/") or 
            line.startswith(r"Underfull \hbox ") or 
            line.startswith(r"Overfull \hbox ") or 
            line.startswith(r"Overfull \vbox ") or 
            line.startswith(r"Overfull \vbox ") or 
            line.startswith("This is XeTeX")):
            del lines[line_index]

    for line in lines:
        if not isinstance(line, str):        
            line = line.encode("ascii", "replace")            
            print(line)
    return


# def create_shared_index(verbosity=0, fail_fast=True):
#     print()
#     print("===============================================")
#     print("     Create the Index.pdf file")
#     print("===============================================")
    
#     # combine indexes
#     index_entries = []
#     index_regex = re.compile(
#         "\\\\indexentry\{"
#         "(?P<index_name>.*?)"
#         "\}\{"
#         "(?P<index_page>\d+)"
#         "\}$")
#     for fname, build_index, index_name in config.doc_files_to_build:
#         base_fname, _ = splitext(basename(fname))
#         idx_fname = join(build_dir, base_fname + ".idx")

#         with open(idx_fname) as f:
#             for line in f.readlines():
#                 match_obj = index_regex.match(line)
#                 if match_obj is not None:
#                     new_index_line = "\\indexentry{%s}{%s-%s}\n" % (
#                         match_obj.group("index_name"), 
#                         index_name,
#                         match_obj.group("index_page"))
#                     index_entries.append(new_index_line)
#                 else:
#                     print("no match " + line[:-1])

#     # write the combined .idx file
#     index_idx = join(build_dir, "index.idx")
#     with open(index_idx, "w") as f:
#         f.write("".join(index_entries))

#     # create an index.tex
#     index_tex = join(build_dir, "index.tex")
#     with open(index_tex, "w") as f:
#         f.write(index_str)

#     # run makeindex to, ah, make the index
#     # (makeindex won't let you build an index outside of the cwd!)
#     cmd_line = [makeindex, basename(index_idx)]
#     if verbosity > 0:
#         print(("\n\n\n" + " ".join(cmd_line)))
#     #call(cmd_line, cwd = build_dir)

#     succeeded = False
#     try:
#         makeindex_output = check_output(cmd_line, env=env,
#                                         stderr=subprocess.STDOUT,
#                                         cwd=build_dir,
#                                         universal_newlines=True)            
#         assert isinstance(makeindex_output, str)
#         succeeded = True
#     except CalledProcessError as e:
#         makeindex_output = e.output

#         if fail_fast:
#             raise Exception(f"Failed to makeindex {e.output}")

#     print("------------------------------------v")
#     print(makeindex_output)
#     print("------------------------------------^")
            
#     if not xelatex(index_tex):
#         if fail_fast:
#             raise Exception("Failed to run latex on index_tex!")
#         print("Failed to run latex on index_tex!")
#         return
    
#     # move the pdf from the build dir to the pdfs dir
#     pdf_fname = join(build_dir, "index.pdf")
#     if exists(pdf_fname):
#         copy(pdf_fname, pdfs_dir)
#     else:
#         print("Missing index pdf: %s" % pdf_fname)
#     return



def apply_template_to_xml(jinja_env,
                          db,
                          xml_fname_in,
                          verbosity,
                          template_fname=None,
                          archetype=None,
                          patron=None):
    """
    Run the xml through a templating system.

    """
    xml_base_fname, _ = splitext(basename(xml_fname_in))
    xml_fname_out = join(build_dir, "%s.xml" % xml_base_fname)

    # the very first thing we do is run the xml through a template engine 
    # (Doing it like this allows us to include files relative to the doc 
    # dir using Jinjas include directive). 
    if template_fname is None:
        template_fname = xml_fname_in
    template = jinja_env.get_template(template_fname)
    if template is None:
        print(f"Problem reading template file {template_fname}.")
        exit(0)
        
    xml = jinja_recursive_render(
        template=template,
        jinja_env=jinja_env,
        db=db,
        monster_groups=db.monster_groups,                          
        ability_groups=db.ability_groups,
        npc_gangs=db.npc_gangs,
        archetype=archetype,
        patron=patron,
        config=config,
        encounters=db.encounters,
        add_index_to_core=config.add_index_to_core,
        doc_name=xml_fname_in)

    # process Λ abilities
    try:
        xml = db.filter_abilities(xml, verbose=verbosity>0)
    except Exception as err:
        print(f"Problem filtering abilities in {xml_fname_in}")
        raise err

    # write the post-processed xml to the build dir 
    # (has all the included files in it).
    with codecs.open(xml_fname_out, "w", "utf-8") as f:
        f.write(xml)

    # parse an xml document
    doc = Doc(xml_fname_out)
    if not doc.parse():
        print(f"Problem parsing the xml.")
        exit(0)

    if not doc.validate():
        print("Fatal: xml errors are fatal!")
        print("Run with the -s cmd line option to ignore xml errors.")
        exit(0)        
        
    return doc


# def build_epub(xml_fname,
#                verbosity,
#                doc,
#                db,                  
#                archetype=None,
#                patron=None):
#     # base name .. no extension
#     doc_base_fname, _ = splitext(basename(xml_fname))
#     epub_fname = join(build_dir, "%s.epub" % doc_base_fname)

#     print((f"\tBuilding {epub_fname}"))

#     # check we have a book_node to format
#     if not doc.has_book_node():
#         if verbosity >= 1:
#             print("No book node to format in document: %s IGNORING!" % doc_fname)
#         return

#     # build the epub document 
#     #with codecs.open(tex_fname, "w", "utf-8") as f:
#     epub_formatter = EPubFormatter(epub_fname=epub_fname, db=db)

#     errors = doc.format(epub_formatter)
#     if len(errors) > 0:
#         print("Errors:")
#         for error in errors:
#             print("\t%s\n\n\n" % error)                
#             exit()

#     # Copy the pdf from the build dir to the pdfs dir
#     copy(epub_fname, pdfs_dir)
    
#     print((f"\tFinished building {epub_fname}"))
#     return True


def build_pdf(
        xml_fname,
        verbosity,
        doc,
        db,
        archetype=None,
        patron=None):
    # base name .. no extension
    doc_base_fname, _ = splitext(basename(xml_fname))
    pdf_fname = join(build_dir, "%s.pdf" % doc_base_fname)
    tex_fname = join(build_dir, "%s.tex" % doc_base_fname) 

    print(f"\tBuilding {pdf_fname}")

    # check we have a book_node to format
    if not doc.has_book_node():
        if verbosity >= 1:
            print("No book node to format in document: %s IGNORING!" % doc_fname)
        return    
    
    # makeindex won't write to files outside of the cwd,
    # so we don't want a path here.  Just a filename
    idx_fname = "%s.idx" % doc_base_fname

    # create an empty index if one does not exist.
    full_idx_fname = join(build_dir, idx_fname)
    if not exists(full_idx_fname):
        f = open(full_idx_fname, 'w')
        f.write('')

    # run makeindex to, ah, make the index
    # (makeindex won't let you build an index outside of the cwd!)
    cmd_line = [makeindex, idx_fname]
    if verbosity > 0:
        print((f"\n\n\nIn {build_dir} run:\n") + " ".join(cmd_line))
        return_code = call(cmd_line, cwd=build_dir)
        if return_code != 0:
            sys.exit("Failed to run makeindex on %s" % idx_fname)    

    # build the latex document by converting the xml into tex
    with codecs.open(tex_fname, "w", "utf-8") as f:           
        latex_formatter = LatexFormatter(f, db)
        errors = doc.format(latex_formatter)
        if len(errors) > 0:
            print("Errors:")
            for error in errors:
                print("\t%s\n\n\n" % error)                
                exit()

    # converts the latex to pdf
    if not xelatex(tex_fname, verbosity=verbosity):
        print((f"\fFailed to build {pdf_fname}"))
        return False

    # Copy the pdf from the build dir to the pdfs dir
    copy(pdf_fname, pdfs_dir)
    
    print((f"\tFinished building {pdf_fname}"))
    return True



def build_html_doc(template_fname, verbosity, archetype = None):
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
    html_fname = join(build_dir, "%s.html" % doc_base_fname)

    # parse an xml document
    print(f"--------------> PARSING {xml_fname}")
    doc = Doc(xml_fname)        
    if not doc.parse():
        print("Problem parsing the xml.")
        exit(0)

    print(f"--------------> VALIDATING {xml_fname}")
    if not doc.validate():
        print("Fatal: xml errors are fatal!")
        print("Run with the -s cmd line option to ignore xml errors.")
        exit(0)
        
    # build the html document by converting the xml into tex
    with codecs.open(html_fname, "w", "utf-8") as f:
        html_formatter = HtmlFormatter(f)
        errors = doc.format(html_formatter)
        if len(errors) > 0:
            print("Errors:")
            for error in errors:
                print("\t%s\n\n\n" % error)
                exit()
    return


def clean():
    """
    Delete all the build artifacts (tex, etc) and the pdfs.

    """
    for fname in os.listdir(build_dir):
        _, ext = splitext(fname)
        if ext in (".tex", ".log", ".toc", ".aux", ".idx", ".ind", 
                   ".xlsx", ".pdf", ".xml", ".ilg", ".out", ".loa"):
            fname = join(build_dir, fname)
            os.remove(fname)

    for fname in os.listdir(pdfs_dir):
        if fname.endswith(".pdf"):
            fname = join(pdfs_dir, fname)
            os.remove(fname)
    return


def build_book(dir_name, xml_fname, verbosity=0):
    """
    Build a single book/document.

    """
    full_doc_xml_fname = join(dir_name, xml_fname)
    print(" ==================================== ")
    print(f" Processing {xml_fname}")
    print(f"\tReading {full_doc_xml_fname}")
    doc = apply_template_to_xml(
        jinja_env,
        xml_fname_in = full_doc_xml_fname,
        db=db,
        verbosity=verbosity) or die()

    print(f"\tBuilding {full_doc_xml_fname}")
    print(f"\t\tBuilding pdf")
    build_pdf(
        xml_fname=full_doc_xml_fname,
        doc=doc,
        db=db,
        verbosity=verbosity) or die()

    # build_epub(
    #     xml_fname=archetype.get_id(),
    #     verbosity=verbosity,
    #     doc=doc,
    #     db=db,
    #     archetype=archetype) or die()
    return



def create_release(config, db, verbosity=0):
    release_fname = join(release_dir, f"malleus_deum_{db.version}.zip")
    if verbosity > 0:
        print("----------------------------------")
        print(f"Creating release {release_fname}")
        
    with zipfile.ZipFile(release_fname, mode="w") as archive:
        for fname in config.release_files:
            fname = join(build_dir, fname)

            if verbosity > 1:
                print(f"\tadding {fname})")
            archive.write(fname)
    return


if __name__ == "__main__":
    try:
        opts, args = getopt(
            sys.argv[1:],
            "vhcCr",
            ["verbose", "help", "clean", "clobber", "release"])

    except GetoptError as err:
        usage(msg = str(err), return_code = 2)        

    verbosity = 0
    debug = True
    release = False
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
        elif o in ("-r", "--release"):
            release = True
        else:
            raise Exception(f"unhandled option {o}")

    # check xelatex exists.
    xelatex_executable = find_xelatex()
    assert exists(xelatex_executable)
    if verbosity > 1:
        print("Using xelatex at %s" % xelatex_executable)

    # check makeindex exists.
    makeindex = find_makeindex()
    assert exists(makeindex), "Can't find makeindex at %s" % makeindex
    if verbosity > 1:
        print("Using makeindex at %s" % makeindex)

    # make any dirs we need
    if not exists(build_dir):
        mkdir(build_dir)

    if not exists(pdfs_dir):
        mkdir(pdfs_dir)

    # Conditionally build some graphs (we won't need unless we're building the rationale doc)
    if "rationale.xml" in [t[0] for t in config.doc_files_to_build]:
        print("Building dice pool graphs.")
        graphs.draw_graphs()
        #dice_pool_graph.build_dice_pool_graphs()
        morale_graph.build_morale_graph()
        d6_graph.draw_d6_graph()
        aspect_lifetime_graph.draw_aspect_lifetime_graph()

    # load the game database (archetypes, abilties etc).
    db = DB()
    db.load(root_dir=root_dir, fail_fast=True)
    
    # generate the skill tree images
    # skill_tree_builder = SkillTreeBuilder(page=Page.ONE)
    # skill_tree_builder.build(db.ability_groups,
    #                          fname=join(build_dir, "ability_tree1.eps"))
    # skill_tree_builder.build(db.ability_groups,
    #                          fname=join(build_dir, "ability_tree1.pdf"))
    
    # skill_tree_builder = SkillTreeBuilder(page=Page.TWO)
    # skill_tree_builder.build(db.ability_groups,
    #                          fname=join(build_dir, "ability_tree2.eps"))
    # skill_tree_builder.build(db.ability_groups,
    #                          fname=join(build_dir, "ability_tree2.pdf"))
    
    # get a jinja environment
    jinja_env = Environment(
        loader = FileSystemLoader([root_dir, ]),
        keep_trailing_newline = True,
        trim_blocks = False,
        lstrip_blocks = False,
    )

    # Use these in jinja templates like this:  {{ "foobar" | log }}
    jinja_env.filters['convert_to_roman_numerals'] = utils.convert_to_roman_numerals
    jinja_env.filters['ab'] = db.filter_abilities
    jinja_env.filters['abilities'] = db.filter_abilities
    jinja_env.filters['no_nones'] = jinja_no_nones
    jinja_env.filters['log']=jinja_log_to_console
    jinja_env.filters['exit']=jinja_exit


    print("********************** 0")

    
    # Add the local styles dir
    # The trailing // means that TeX programs will search recursively in that 
    # folder; the trailing colon means "append the standard value of TEXINPUTS" 
    # (which you don't need to provide).
    tex_inputs = styles_dir + "//:"

    # Get a copy of the environment with TEXINPUTS set.
    env = deepcopy(os.environ)
    env["TEXINPUTS"] = tex_inputs

    print("********************** 0.1")

    generate_level_progression_tables(jinja_env, db)
    #sys.exit() # FIXME:!!    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    print("********************** 0.2")

    
    # Build the ability trees (these are the eps diagrams that should skill prereqs)
    build_skill_trees(db.ability_groups)


    print("********************** 1")
    
    #
    # Build Pdf Files.
    #
    
    # Build doc books (in the docs dir)
    for doc_xml_fname, _, _ in config.doc_files_to_build:
        build_book("docs", doc_xml_fname, verbosity)

    # Build background books (in the background dir)
    for doc_xml_fname, _, _ in config.background_files_to_build:
        print("--------------------- " + doc_xml_fname)
        build_book("background", doc_xml_fname, verbosity)
        
    # Build archetypes
    for archetype_id, _, _ in config.archetypes_to_build:
        archetype = db.archetypes[archetype_id]
        assert archetype is not None
        
        full_doc_xml_fname = join("archetypes", archetype.get_id() + ".xml")
        doc = apply_template_to_xml(
            jinja_env,
            xml_fname_in=full_doc_xml_fname,
            template_fname=ARCHETYPE_TEMPLATE_FNAME,           
            archetype=archetype,
            db=db,
            verbosity=verbosity) or die()
        
        build_pdf(
            xml_fname=archetype.get_id(),
            verbosity=verbosity,
            doc=doc,
            db=db,
            archetype=archetype) or die()

        # build_epub(
        #     xml_fname=archetype.get_id(),
        #     verbosity=verbosity,
        #     doc=doc,
        #     db=db,
        #     archetype=archetype) or die()


    # Build latex/pdf module files.
    for module_id, _, _ in config.modules_to_build:
        build_book(join("modules", module_id), f"{module_id}.xml", verbosity)

        
    # Build latex/pdf patron files.
    for patron_id, _, _ in config.patrons_to_build:
        patron = db.patrons[patron_id]
        full_doc_xml_fname = join("docs", patron.get_id() + ".xml")
        doc = apply_template_to_xml(
            jinja_env,
            xml_fname_in=full_doc_xml_fname,
            template_fname=PATRON_TEMPLATE_FNAME,           
            #archetype=archetype,
            patron=patron,
            db=db,
            verbosity=verbosity) or die()
        
        build_pdf(
            xml_fname=patron.get_id(),
            verbosity=verbosity,
            doc=doc,
            db=db,
            patron=patron) or die()
        
        # build_pdf(template_fname=PATRON_TEMPLATE_FNAME,
        #           doc_fname=patron.get_id(), 
        #           verbosity=verbosity,
        #           db=db,
        #           patron=patron) or die()


        
        
    # # Build latex/pdf encounter files.
    # for encounter_id, _, _ in config.encounters_to_build:
    #     encounter_fname = join(#encounters_dir,
    #         "encounters",
    #         encounter_id,
    #         "%s.xml" % encounter_id)
    #     build_pdf_doc(encounter_fname,
    #                   db=db,
    #                   doc_fname=encounter_fname, 
    #                   verbosity=verbosity) or die()



    #
    # Build HTML Files (mostly a placeholder at this stage)
    #

    # Build html docs.
    #for doc_xml_fname, _, _ in config.files_to_build:
    #    build_html_doc(doc_xml_fname, verbosity=verbosity)
        
    
    #
    # Create the index.pdf file
    #
    print(" Creating index.pdf")
    #create_shared_index(verbosity=verbosity)
    
    #
    # Create Summary.xslx
    # (a table of ability costs by archetype for working on balance)
    #
    # save summary details to a spreadsheet (for analysis)
    #spreadsheet_fname = join(build_dir, "summary.xlsx")
    #write_summary_to_spreadsheet(spreadsheet_fname,
    #                             ability_groups=db.ability_groups,
    #                             archetypes=db.archetypes)

    spreadsheet_fname = join(build_dir, "game_balance.xlsx")
    write_game_balance_spreadsheet(spreadsheet_fname,
                                   ability_groups=db.ability_groups,
                                   archetypes=db.archetypes)


    ability_summary_fname = join(build_dir, "ability_summary.xlsx")
    write_ability_summary_spreadsheet(ability_summary_fname,
                                      ability_groups=db.ability_groups)    
    
    #
    # Create the character sheets
    # 
    create_blank_character_sheet()
    for archetype in db.archetypes:
        print(f"CREATING {archetype}")
        create_character_sheet_for_archetype(db, archetype)
        
    #sys.exit(0)
    #create_empty_abilities_sheet()        
    
    #
    # Generate the license report
    #
    db.licenses.generate_license_report(root_dir)
    

    #
    # If we're releasing then zip a bunch of pdfs from the
    # zip dir and put them in the release dir.
    #
    if release:
        create_release(config, db, verbosity)
