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
from spreadsheet_writer import write_game_balance_spreadsheet, write_ability_summary_spreadsheet

# Graph creation stuff.. for analysis in the rationale doc.
import graphs
import d6_graph
import aspect_lifetime_graph

# FIXME: didn't want to deal with pdftk at the moment.
from character_sheet_writer import (
    create_character_sheet_for_archetype,
    create_empty_abilities_sheet,
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

from latex_utils import (
    #xelatex
    build_pdf
)

from jinja_utils import apply_template_to_xml, get_jinja_env


# Jinja2 doesn't like absolute paths.
# We must supply a relative path!
ARCHETYPE_TEMPLATE_FNAME = join("docs", "archetype_template.xml")
PATRON_TEMPLATE_FNAME = join("docs", "patron_template.xml")



def die():
    raise Exception("Fatal Error")        


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
        #morale_graph.build_morale_graph()
        d6_graph.draw_d6_graph()
        aspect_lifetime_graph.draw_aspect_lifetime_graph()

    # load the game database (archetypes, abilties etc).
    with DB() as db:
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



        # # Add the local styles dir
        # # The trailing // means that TeX programs will search recursively in that 
        # # folder; the trailing colon means "append the standard value of TEXINPUTS" 
        # # (which you don't need to provide).
        # tex_inputs = styles_dir + "//:"

        # # Get a copy of the environment with TEXINPUTS set.
        #env = deepcopy(os.environ)
        # env["TEXINPUTS"] = tex_inputs

        jinja_env = get_jinja_env(db)
        generate_level_progression_tables(jinja_env, db)
        #sys.exit() # FIXME:!!    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


        # Build the ability trees (these are the eps diagrams that should skill prereqs)
        build_skill_trees(db.ability_groups)


        #
        # Build Pdf Files.
        #

        # Build doc books (in the docs dir)
        for doc_xml_fname, _, _ in config.doc_files_to_build:
            build_book("docs", doc_xml_fname, verbosity)

        # Build background books (in the background dir)
        for doc_xml_fname, _, _ in config.background_files_to_build:
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
            module_name = join("modules", module_id)
            build_book(module_name, f"{module_id}.xml", verbosity)


        # Build latex/pdf patron files.
        for patron_id, _, _ in config.patrons_to_build:
            patron = db.patrons[patron_id]
            full_doc_xml_fname = join("docs", patron.get_id() + ".xml")
            doc = apply_template_to_xml(
                jinja_env,
                xml_fname_in=full_doc_xml_fname,
                template_fname=PATRON_TEMPLATE_FNAME,           
                patron=patron,
                db=db,
                verbosity=verbosity) or die()

            build_pdf(
                xml_fname=patron.get_id(),
                verbosity=verbosity,
                doc=doc,
                db=db,
                patron=patron) or die()


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
        if config.print_resource_report:
            db.resources.print_report(verbose=True)

        #
        # If we're releasing then zip a bunch of pdfs from
        # the zip dir and put them in the release dir.
        #
        if release:
            create_release(config, db, verbosity)

