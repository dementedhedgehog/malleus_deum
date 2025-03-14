"""

  Xelatex utilities.

  High level methods to run xelatex, makeindex etc.
  The actual .tex files are created in latex_formatter.py

"""
import os
import sys
import functools
from copy import deepcopy
from os.path import exists, splitext, basename, join  # abspath, dirname, exists, 
import platform
import codecs
import shutil
from subprocess import call, check_output, CalledProcessError, STDOUT
import hashlib

from utils import (
    #root_dir,
    build_dir,
    pdfs_dir,
    # docs_dir,
    styles_dir,
    # encounters_dir,
    # modules_dir,
    # release_dir,
    # third_party_dir
)
from latex_formatter import LatexFormatter

@functools.cache
def find_xelatex(verbosity=0):
    """
    Return a path to the xelatex executable on this platform.

    """
    if platform.system() == "Linux":
        xelatex_executable = "/usr/bin/xelatex"
    else:
        # ??
        xelatex_executable = "C:/Program Files (x86)/MiKTeX 2.9/miktex/bin/xelatex.exe"

    # sanity check
    assert exists(xelatex_executable), f"Can't find xelatex at {xelatex_executable}"
    if verbosity > 0:
        print("Using xelatex at %s" % xelatex_executable)

    return xelatex_executable


def xelatex(tex_fname, verbosity=0):
    """
    Run xelatex on the given tex file to produce a pdf.

    """
    xelatex_executable = find_xelatex(verbosity)
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
                                      stderr=STDOUT,
                                      universal_newlines=True)            
        assert isinstance(xelatex_output, str)
        succeeded = True
    except CalledProcessError as e:
        xelatex_output = e.output

    if succeeded:
        if verbosity > 1:  
            print(xelatex_output)        
        elif verbosity == 1:
            # print xelatex output (filter out some of the spammy messages)
            filter_xelatex_output(xelatex_output)
    else:
        print(xelatex_output)
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


@functools.cache
def find_makeindex(verbosity=0):
    """
    Return a path the makeindex executable (a latex tool).

    """
    if platform.system() == "Linux":
        makeindex = "/usr/bin/makeindex"
    else:
        # This is a guess.
        makeindex = "C:/Program Files (x86)/MiKTeX 2.9/miktex/bin/makeindex.exe"

    # sanity check makeindex exists.
    assert exists(makeindex), f"Can't find makeindex at {makeindex}"
    if verbosity > 1:
        print("Using makeindex at %s" % makeindex)
        
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
            line.startswith(r"Underfull \vbox ") or 
            line.startswith(r"Overfull \vbox ") or 
            line.startswith("This is XeTeX")):
            del lines[line_index]

    for line in lines:
        if not isinstance(line, str):        
            line = line.encode("ascii", "replace")            
            print(line)
    return


def _get_md5_hash(fname):
    return hashlib.md5(open(fname,'rb').read()).hexdigest()


def build_pdf(
        xml_fname,
        verbosity,
        doc,
        db,
        archetype=None,
        patron=None,
        fast_mode=False):
    
    # base name .. no extension
    doc_base_fname, _ = splitext(basename(xml_fname))
    pdf_fname = join(build_dir, f"{doc_base_fname}.pdf")
    tex_fname = join(build_dir, f"{doc_base_fname}.tex")
    idx_fname = join(build_dir, f"{doc_base_fname}.idx")

    print(f"\tBuilding {pdf_fname}")

    # check we have a book_node to format
    if not doc.has_book_node():
        if verbosity >= 1:
            print("No book node to format in document: %s IGNORING!" % doc_fname)
        return    
    
    # makeindex won't write to files outside of the cwd (a safety mechanism),
    # so we don't want a path here, ust a filename.
    short_idx_fname = "%s.idx" % doc_base_fname

    # clear the index
    if not exists(idx_fname):
        f = open(idx_fname, 'w')
        f.write('')

    # build the latex document by translating the doc xml
    if not fast_mode:
        with codecs.open(tex_fname, "w", "utf-8") as f:           
            latex_formatter = LatexFormatter(f, db, xml_fname)
            errors = doc.format(latex_formatter)
            if len(errors) > 0:
                print("Errors:")
                for error in errors:
                    print("\t%s\n\n\n" % error)                
                    exit()

    # then convert the latex document to pdf (and generate the index idx file)
    idx_hash = _get_md5_hash(idx_fname)
    new_idx_hash = None
    for i in range(3):
        if not xelatex(tex_fname, verbosity=verbosity):
            print((f"\fFailed to build {pdf_fname}"))
            return False

        # check if the index is still changing.
        new_idx_hash = _get_md5_hash(idx_fname)
        if new_idx_hash == idx_hash:
            break
        else:
            idx_hash = new_idx_hash
        

    # if the idx file is still changing we have a problem
    if new_idx_hash != idx_hash:
        print(f"\tWarning: Index file {idx_fname} keeps changing!")
                
    # run makeindex to, ah, make the index
    # (makeindex won't let you build an index outside of the cwd!)
    makeindex = find_makeindex(verbosity=verbosity)
    style_fname = join(styles_dir, "latex_index_style.ist")
    cmd_line = [makeindex, short_idx_fname, "-s", style_fname]
    print(f"\n\nIn {build_dir} run:\n\t{' '.join(cmd_line)}")
    return_code = call(cmd_line, cwd=build_dir)
    if return_code != 0:
        sys.exit("Failed to run makeindex on %s" % idx_fname)


    # rerun latex to build the pdf with the up to date index
    if not xelatex(tex_fname, verbosity=verbosity):
        print((f"\fFailed to build {pdf_fname}"))
        return False
    



    # Copy the pdf from the build dir to the pdfs dir
    shutil.copy(pdf_fname, pdfs_dir)
    
    print((f"\tFinished building {pdf_fname}"))
    return True


# latex preamble for the meta index.
INDEX_TEMPLATE = r"""
\\documentclass{article}
\\usepackage{makeidx}
\\usepackage{hyperref}

% Override the default index \see behaviour and include
% the pageref.
\\renewcommand{\see}[2]{see #1 #2}

\\begin{document}
\\printindex
\\end{document}

"""

def create_shared_index(verbosity=0, fail_fast=True):
    print()
    print("===============================================")
    print("     Create the Index.pdf file")
    print("===============================================")
    
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
#         f.write(INDEX_TEMPLATE)

#     # run makeindex to, ah, make the index
#     # (makeindex won't let you build an index outside of the cwd!)
#     cmd_line = [makeindex, basename(index_idx)]
#     if verbosity > 0:
#         print(("\n\n\n" + " ".join(cmd_line)))
#     #call(cmd_line, cwd = build_dir)

#     succeeded = False
#     try:
#         makeindex_output = check_output(cmd_line, env=env,
#                                         stderr=STDOUT,
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
    return


