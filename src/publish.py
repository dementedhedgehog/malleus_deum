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
import subprocess
from copy import deepcopy
import io 
import re
import zipfile


src_dir = abspath(join(dirname(__file__)))
sys.path.append(src_dir)


# local
from doc import Doc
from db import DB
#from epub_formatter import EPubFormatter
from html_formatter import HtmlFormatter
from spreadsheet_writer import (
    write_game_balance_spreadsheet,
    write_ability_summary_spreadsheet
    )

# Graph creation stuff.. for analysis in the rationale doc.
import graphs
import aspect_lifetime_graph

# Creates character sheets.
from character_sheet_writer import (
    create_character_sheet_for_archetype,
    create_empty_abilities_sheet,
    create_blank_character_sheet)

from generate_level_progression_tables import generate_level_progression_tables
from generate_ability_trees import build_ability_trees
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

import latex_utils
import jinja_utils


# Jinja2 doesn't like absolute paths.
# We must supply a relative path!
ARCHETYPE_TEMPLATE_FNAME = join("docs", "archetype_template.xml")
PATRON_TEMPLATE_FNAME = join("docs", "patron_template.xml")


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


def _parse_xml(processed_xml_fname):
    doc = Doc(processed_xml_fname)
    if not doc.parse():
        raise Exception(f"Problem parsing {processed_xml_fname}")
    return doc


def build_book(dir_name, xml_fname,
               verbosity=0,
               only_build_tex_files=False,
               validate_only=False):
    """
    Build a single book/document.

    """
    full_doc_xml_fname = join(dir_name, xml_fname)
    print(" ==================================== ")
    print(f" Processing {xml_fname}")
    print(f"\tTemplating {full_doc_xml_fname}")
    processed_xml_fname = jinja_utils.render_xml(
        jinja_env,
        db=db,
        xml_fname_in=full_doc_xml_fname,
        verbosity=verbosity)

    # parse an xml document
    print(f"\tParsing {processed_xml_fname}")
        
    doc = _parse_xml(processed_xml_fname)
    if validate_only:
        return

    print(f"\tBuilding {full_doc_xml_fname}")
    print(f"\t\tBuilding pdf")
    if not latex_utils.build_pdf(
            xml_fname=full_doc_xml_fname,
            doc=doc,
            db=db,
            only_build_tex_files=only_build_tex_files,
            verbosity=verbosity):
        raise Execption(f"Problem building pdf from {full_doc_xml_fname}!")

    # build_epub(
    #     xml_fname=archetype.get_id(),
    #     verbosity=verbosity,
    #     doc=doc,
    #     db=db,
    #     archetype=archetype) 
    return



def create_release(db, verbosity=0):
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



def usage(msg = "", return_code = 0):
    prog_name = basename(sys.argv[0])
    print(
        ("Usage: %s -h | -s | -c | -x \n"
         "\n"
         "\t-h\tHelp! print this message.\n"
         "\t-c\tClean all the files before building, e.g. pdfs etc\n"
         "\t-C\tClean all the files and exit.\n"
         "\t-V\tValidate the xml and exit.\n"
         "\t-s\tFail slow! Ignore xml errors and try and build the doc anyway.\n"
         "\t-t\tOnly build the .tex diles don't build the pdf.\n"
         "\t-u\tProduce an unused resources report.\n"
         "\t-v\tVerbose.\n"
         "\t-r\tBuild a release zip with contents defined in config and version"
         "from docs/version.xml.\n"
         "\n"
         "%s" % (prog_name, msg)))
    exit(return_code)    


if __name__ == "__main__":
    try:
        opts, args = getopt(
            sys.argv[1:],
            "vVhcCrtu",
            ["verbose", "validate", "help", "clean",
             "clobber", "release", "tex", "unusedresources"])

    except GetoptError as err:
        usage(msg = str(err), return_code = 2)        

    verbosity = 0
    debug = True
    release = False
    validate_only = False
    only_build_tex_files = False
    produce_unused_resources_report = False
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbosity += 1            
        elif o in ("-t", "--tex"):
            only_build_tex_files = True
        elif o in ("-u", "--unusedresources"):
            produce_unused_resources_report = True
        elif o in ("-V", "--validate"):
            validate_only = True
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

    # make any dirs we need
    if not exists(build_dir):
        mkdir(build_dir)

    if not exists(pdfs_dir):
        mkdir(pdfs_dir)

    # load the game database (archetypes, abilties etc).
    with DB() as db:
        db.load(root_dir=root_dir, fail_fast=True)

        jinja_env = jinja_utils.get_jinja_env(db)
        generate_level_progression_tables(jinja_env, db)

        # Build the ability trees (these are the eps diagrams that show ability
        # prereqs)
        build_ability_trees(db.ability_groups)

        #
        # Build Pdf Files.
        #

        # Build doc books (in the docs dir)
        for doc_xml_fname, _, _ in config.doc_files_to_build:
            build_book(
                "docs",
                doc_xml_fname,
                verbosity=verbosity,
                validate_only=validate_only,
                only_build_tex_files=only_build_tex_files)

        # Build background books (in the background dir)
        for doc_xml_fname, _, _ in config.background_files_to_build:
            build_book("background", doc_xml_fname, verbosity, validate_only)

        # Build archetypes
        for archetype_id, _, _ in config.archetypes_to_build:
            archetype = db.archetypes[archetype_id]
            assert archetype is not None

            full_doc_xml_fname = join("archetypes", archetype.get_id() + ".xml")
            processed_xml_fname = jinja_utils.render_xml(
                jinja_env,
                xml_fname_in=full_doc_xml_fname,
                template_fname=ARCHETYPE_TEMPLATE_FNAME,
                archetype=archetype,
                db=db,
                verbosity=verbosity) or die()
            
            # parse an xml document
            doc = _parse_xml(processed_xml_fname)

            # Parsing runs all the xsd and schematron validation.
            if validate_only:
                continue                
            if not latex_utils.build_pdf(
                xml_fname=processed_xml_fname,
                verbosity=verbosity,
                doc=doc,
                db=db,
                archetype=archetype):
                raise Exception("Failed to build pdf!")

            # build_epub(
            #     xml_fname=archetype.get_id(),
            #     verbosity=verbosity,
            #     doc=doc,
            #     db=db,
            #     archetype=archetype) or die()


        # Build latex/pdf module files.
        for module_id, _, _ in config.modules_to_build:
            module_name = join("modules", module_id)
            build_book(module_name, f"{module_id}.xml", verbosity)

        # Build latex/pdf patron files.
        for patron_id, _, _ in config.patrons_to_build:
            patron = db.patrons[patron_id]
            full_doc_xml_fname = join("docs", patron.get_id() + ".xml")
            processed_xml_fname = jinja_utils.render_xml(
                jinja_env,
                xml_fname_in=full_doc_xml_fname,
                template_fname=PATRON_TEMPLATE_FNAME,           
                patron=patron,
                db=db,
                verbosity=verbosity) or die()

            
            doc = _parse_xml(processed_xml_fname)
            if validate_only:
                continue

            if not latex_utils.build_pdf(
                    xml_fname=patron.get_id(),
                    verbosity=verbosity,
                    doc=doc,
                    db=db,
                    patron=patron):
                raise Exception("Failed to build pdf")

        # Build latex/pdf encounter files.
        for encounter_id, _, _ in config.encounters_to_build:
            xml_fname = join(encounter_id, f"{encounter_id}.xml")
            build_book("encounters", xml_fname, verbosity)            

        #
        # Build HTML Files (mostly a placeholder at this stage)
        #

        # Build html docs.
        #for doc_xml_fname, _, _ in config.files_to_build:
        #    build_html_doc(doc_xml_fname, verbosity=verbosity)


        #
        # Create the index.pdf file
        #
        if config.build_meta_index:
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
        create_empty_abilities_sheet()
        _ids_to_build = set(
            [a[0] for a in config.archetypes_to_build])    
        for archetype in db.archetypes:
            if archetype.archetype_id in _ids_to_build:
                print(f"Creating char sheet for {archetype.get_title()}")
                create_character_sheet_for_archetype(db, archetype)

        #
        # Generate a resource report
        #
        # We want to make sure everything has a license,
        # and also list unused art resources to help us
        # cull stuff from the repo.
        #
        if config.print_resource_report or produce_unused_resources_report:
            db.resources.print_report(verbose=True)

        #
        # If we're releasing then zip a bunch of pdfs from
        # the zip dir and put them in the release dir.
        #
        if release:
            create_release(db, verbosity)

