#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

  Code that creates the character sheets.

  We make the character sheets by filling in pdf forms.
  We create the initial pdf forms using Scribus, and we 
  fill in the forms automatically using an external tool
  called pdftk.  This is a two step process.  First write
  an fdf file that contains the form data.  Then use pdftk 
  to put the fdf data into a new pdf file.  Finally we use
  PyPDF to glue all our generated pages together.


  To get the fdf from a form
    pdftk test.pdf fill_form test.fdf output out.pdf verbose

  To set the form values in a pdf
    pdftk test.pdf fill_form test.fdf output out.pdf verbose    

  We also merge using pdftk.


  FIX FOR BLACK SQUARES.. OPEN PDF IN evince .. add space to 
  a text field and save!!!


"""
from shutil import copy
from os.path import join, dirname, abspath, exists
import platform
from subprocess import call, check_output, CalledProcessError
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfFileMerger
from archetypes import Archetypes
from abilities import FAMILY_TYPES, AbilityRank

from utils import (
    char_sheet_dir,
    build_dir,
    pdfs_dir,
)

# The character sheet template (a pdf form)
PG1_TEMPLATE = join(char_sheet_dir, "character_sheet_pg1.pdf")
ABILITIES_TEMPLATE = join(char_sheet_dir, "character_sheet_abilities.pdf")

N_ROWS_PER_ABILITY_PAGE = 26
N_COLS_PER_ABILITY_PAGE = 2
EXTRA_ABILITIES = 20        # Make sure we have some space on the ability pages for leveling up.
ABILITIES_PER_PAGE = N_ROWS_PER_ABILITY_PAGE * N_COLS_PER_ABILITY_PAGE


fdf_header = b"""\
%FDF-1.2
%<E2><E3><CF><D3>
1 0 obj 
<<
/FDF
<<
/Fields ["""

FDF_PG1_BODY = """
<<
/V ({archetype_title})
/T (ArchetypeTitle)
>>"""

FDF_ABILITY_BODY = """
<<
/V ({ability_name})
/T (AbilityName{ability_number})
>> 
<<
/V ({ability_description})
/T (AbilityDescription{ability_number})
>>
<<
/V ({ability_mastery})
/T (AbilityMastery{ability_number})
>>"""

# FDF_ABILITY_BODY = """
# <<
# /V ({ability_check})
# /T (AbilityCheck{ability_number})
# >> 
# <<
# /V ({ability_class})
# /T (AbilityClass{ability_number})
# >>  
# <<
# /V ({ability_name})
# /T (AbilityName{ability_number})
# >> 
# <<
# /V ({ability_effect_type})
# /T (AbilityEffectType{ability_number})
# >> 
# <<
# /V ({ability_effect})
# /T (AbilityEffect{ability_number})
# >>
# <<
# /V ({ability_mastery})
# /T (AbilityMastery{ability_number})
# >>
# <<
# /V ({ability_overcharge_type})
# /T (AbilityOverchargeType{ability_number})
# >>
# <<
# /V ({ability_overcharge})
# /T (AbilityOvercharge{ability_number})
# >>"""

fdf_footer = b"""]
>>
>>
endobj 
trailer

<<
/Root 1 0 R
>>
%%EOF
"""
    

def find_pdftk():
    """
    Return a path to the pdftk executable on this platform.

    """
    pdftk_executable = None
    if platform.system() == "Linux":
        for fname in ["/usr/local/bin/pdftk",
                      "/usr/bin/pdftk"]:
            if exists(fname):
                pdftk_executable = fname
                break
    else:
        #pdftk_executable = "C:/Program Files (x86)/MiKTeX 2.9/miktex/bin/xelatex.exe"
        raise Exception("I wonder where pdftk will be on windows.")

    if not exists(pdftk_executable):
        raise Exception("Can't find pdftk executable.")
        
    return pdftk_executable

#
# FIXME: don't want to fix this now!!
#
pdftk_executable = find_pdftk()
pdfunite_executable = "/usr/bin/pdfunite"


def pdftk_fill(pdf_in, fdf_in, pdf_out):
    """
    Run pdftk to fill in pdf_out from the pdf form template and data given.

    """
    cmd_line = [pdftk_executable,
                pdf_in,
                "fill_form",
                fdf_in,
                "output",
                pdf_out,
                "verbose"]
    try:
        pdftk_output = check_output(cmd_line) # , env=env)
    except OSError as e:
        print("Can't find file either %s or %s" % (pdf_in, fdf_in))
        raise e
    except CalledProcessError as e:
        pdftk_output = e.output
        pdftk_error = True
    return


def pdf_merge(pdfs, pdf_out):
    """
    Run pdftk to merge pdfs

    """
    cmd_line = [
        pdftk_executable,
    ] + pdfs +[
        "cat",
        "output",
        pdf_out,
        "verbose"]
    try:
        pdftk_output = check_output(cmd_line) # , env=env)
    except CalledProcessError as e:
        pdftk_output = e.output
        pdftk_error = True
    return


def create_first_page_fdf(fdf_name, archetype=None):
    with open(fdf_name, "wb") as f:
        # if we have another ability rank put fill in the form for
        # that ability, otherwise make it blank.
        if archetype is not None:        
            # write info from the ability
            fdf_info = FDF_PG1_BODY.format(
                archetype_title = archetype.get_title(),
            )
        else:
            # write empty info
            fdf_info = FDF_PG1_BODY % b""

        # write the fdf
        f.write(fdf_header)
        f.write(fdf_info.encode())
        f.write(fdf_footer)
    return


def get_ability_check_name(check, no_name=False):
    if check.overcharge is not None:
        if no_name: 
            return f"ddc: {check.dc}/{check.overcharge}"
        else:
            return f"{check.name}: ddc {check.dc}/{check.overcharge}"
    if no_name:
        return f"ddc {check.dc}"
    else:
        return f"ddc {check.name}: {self.dc}"



def create_abilities_fdf(fdf_name, ability_ranks=None):
    with open(fdf_name, "wb") as f:
        f.write(fdf_header)

        for i in range(ABILITIES_PER_PAGE):
            if ability_ranks is None:
                ability_rank = None                
            else:
                try:
                    ability_rank = next(ability_ranks)
                except StopIteration:
                    ability_rank = None

            # if we have another ability rank put fill in the form for
            # that ability, otherwise make it blank.
            if isinstance(ability_rank, AbilityRank):
                ability = ability_rank.get_ability()
                description = ""
                description += "Type: " + ability.check_type

                # add any check configurations
                checks = ability.get_checks()
                check_strings = []
                if len(checks) > 1:
                    for check in check:
                        check_strings.append(get_ability_check_name(check))
                else:                
                    check = list(ability.get_checks())[0]
                    check_strings.append(get_ability_check_name(check, no_name=True))
                description += ", " + ", ".join(check_strings)
                    
                #description += ", DDC: " + str(check.dc)
                
                ability_class = ability.__class__
                #if ability.overcharge:
                if check.overcharge:
                    description += " <= DC + " + check.overcharge

                # Damage?
                dmg = ability.damage
                if dmg:
                    description += " Dmg: " + dmg

                mastery = "ooo"

                # write info from the ability
                fdf_info = FDF_ABILITY_BODY.format(
                    ability_number=i,
                    ability_name=ability_rank.get_title(),
                    ability_description=description,
                    ability_mastery=mastery,
                )
            elif isinstance(ability_rank, str):
                # write info from the ability
                fdf_info = FDF_ABILITY_BODY.format(
                    ability_number=i,
                    ability_name=ability_rank,
                    ability_description="",
                    ability_mastery="",
                )                
            else:
                # write empty info
                fdf_info = FDF_ABILITY_BODY % {
                    "ability_number": i,
                    "ability_name": "",
                    "ability_description": "",
                    "ability_mastery": "",
                }
                
            f.write(fdf_info.encode())
        f.write(fdf_footer)
    return


from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, TextStringObject


def cmp_titles(ability, ability2):
    return cmp(ability.get_title(), ability2.get_title())



class MockAbilityRank:
    """
    Rather ugly hack to allow titles in our ability rank lists..

    """

    def __init__(self, title):
        self.title = title
        return

    def get_ability(self):        
        return MockAbility()
    

def create_character_sheet_for_archetype(db, archetype):
    # build a list containing all the archetypes available abilities.

    # Sort by (family, ability name, ability rank)
    info = []
    families_seen = set()
    for ability_group in db.ability_groups:
        for ability in ability_group:
            if ability.is_untrained():                
                ability_rank = ability.get_untrained_rank()
                if ability_rank is not None and not ability_rank.get_ability().is_templated():
                    family = ability_group.get_family()
                    info.append((family, ability_rank.get_title(), ability_rank))
                    families_seen.add(family)
                    
            # ability_rank = ability.get_highest_innate_rank()
            # if ability_rank is not None and not ability_rank.get_ability().is_templated():
            #     family = ability_group.get_family()
            #     info.append((family, ability_rank.get_title(), ability_rank))
            #     families_seen.add(family)

    # Add titles to groups of abilities also add some extra space at the end of groups of abilities
    # characters that appear before and after letters
    # (so we can make sure things go before or after blocks of abilities).
    before = "!"
    after = "~"
    for family in FAMILY_TYPES:        
        if family in families_seen:
            family_name = f"-- {family[1:-2].title()} --"
            info.append((family, before, family_name))
            for i in range(5):
                info.append((family, after, ""))
     
    info.sort()
    ability_ranks = [x[2] for x in info]

    # the pages we want to stick together.
    pdf_pages = []

    # create the first page
    archetype_id = archetype.get_id()
    pdf_fname_out = join(build_dir, "%s_pg1.pdf" % archetype_id)
    fdf_fname = join(build_dir,  "%s_pg1.fdf" % archetype_id)
    create_first_page_fdf(fdf_fname, archetype)
    pdftk_fill(PG1_TEMPLATE, fdf_fname, pdf_fname_out)
    pdf_pages.append(pdf_fname_out)

    # work out how many ability pages we need
    # (+2 because we want a whole extra clean sheet of abilities)
    n_pages = (len(ability_ranks) + EXTRA_ABILITIES) // ABILITIES_PER_PAGE + 1
    
    # create all the ability pages    
    ability_rank_iterator = iter(ability_ranks)
    for i in range(n_pages):
        page_number = i + 2
        pdf_fname_out = join(build_dir,"%s_abilities_pg%s.pdf" % (archetype_id, page_number))
        fdf_fname = join(build_dir, "%s_abilities_pg%s.fdf" % (archetype_id, page_number))
        pdf_pages.append(pdf_fname_out)

        # create one character sheet abilities pdf page
        create_abilities_fdf(fdf_fname, ability_rank_iterator)
        pdftk_fill(ABILITIES_TEMPLATE, fdf_fname, pdf_fname_out)        
        
    # now compose the pdf.
    pdf_pages.append(join(char_sheet_dir, "character_sheet_equipment.pdf"))
    pdf_pages.append(join(char_sheet_dir, "character_sheet_notes.pdf"))
    char_sheet_fname = join(build_dir, "%s_char_sheet.pdf" % archetype.get_id())

    # compose_pdf(char_sheet_fname, pdf_pages)
    pdf_merge(pdfs=pdf_pages, pdf_out=char_sheet_fname)

    # copy the final pdf to the pdfs dir
    if exists(char_sheet_fname):
        copy(char_sheet_fname, pdfs_dir)
    else:
        print(f"Missing pdf: {char_sheet_fname}") #  pdf_fname)
    return


def create_empty_abilities_sheet():
    pdf_fname_out = join(build_dir, "character_sheet_extra_abilities.pdf")
    fdf_fname = join(build_dir, "character_sheet_extra_abilities.fdf")
    create_abilities_fdf(fdf_fname)
    pdftk_fill(ABILITIES_TEMPLATE, fdf_fname, pdf_fname_out)        
        
    # copy the final pdf to the pdfs dir
    if exists(pdf_fname_out):
        copy(pdf_fname_out, pdfs_dir)
    else:
        print("Missing pdf: %s" % pdf_fname)
    return


def create_blank_character_sheet():
    return


if __name__ == "__main__":
    from db import DB
    db = DB()
    db.load(root_dir=root_dir, fail_fast=True)
    for archetype in db.archetypes:
        create_character_sheet_for_archetype(db, archetype)
        break

    #create_blank_character_sheet()
    # done.
