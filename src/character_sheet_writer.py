#!/usr/bin/python
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
from abilities import AbilityClass

root_dir = abspath(join(dirname(__file__), ".."))
build_dir = join(root_dir, "build")
pdfs_dir = join(root_dir, "pdfs")
fonts_dir = join(root_dir, "fonts")
resources_dir = join(root_dir, "resources")
char_sheet_dir = join(resources_dir, "character_sheets")
archetypes_dir = join(root_dir, "archetypes")
ability_groups_dir = join(root_dir, "abilities")

# The character sheet template (a pdf form)
PG1_TEMPLATE = join(char_sheet_dir, "character_sheet_pg1.pdf")
ABILITIES_TEMPLATE = join(char_sheet_dir, "character_sheet_abilities.pdf")

N_ROWS_PER_ABILITY_PAGE = 11
N_COLS_PER_ABILITY_PAGE = 2
ABILITIES_PER_PAGE = N_ROWS_PER_ABILITY_PAGE * N_COLS_PER_ABILITY_PAGE


fdf_header = u"""\
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
/V ({ability_check})
/T (AbilityCheck{ability_number})
>> 
<<
/V ({ability_class})
/T (AbilityClass{ability_number})
>> 
<<
/V ({ability_name})
/T (AbilityName{ability_number})
>> 
<<
/V ({ability_effect_type})
/T (AbilityEffectType{ability_number})
>> 
<<
/V ({ability_effect})
/T (AbilityEffect{ability_number})
>>
<<
/V ({ability_mastery})
/T (AbilityMastery{ability_number})
>>
<<
/V ({ability_overcharge_type})
/T (AbilityOverchargeType{ability_number})
>>
<<
/V ({ability_overcharge})
/T (AbilityOvercharge{ability_number})
>>"""

fdf_footer = """]
>>
>>
endobj 
trailer

<<
/Root 1 0 R
>>
%%EOF
"""




fdf_hack = u"""\
%FDF-1.2
%<E2><E3><CF><D3>
1 0 obj 
<<
/FDF
<<
/Fields [
/V (X)
/T (Notes1)
>>]
>>
>>
endobj 
trailer

<<
/Root 1 0 R
>>
%%EOF
"""



ability_class_lookup = {
    AbilityClass.AMBUSH: "a",
    AbilityClass.SURPRISE: "s",
    AbilityClass.INITIATIVE: "i",
    AbilityClass.IMMEDIATE: "z",
    #AbilityClass.TALK: "Talk",
    AbilityClass.FIGHT_REACH: "3:4",
    # AbilityClass.START: "1",
    # AbilityClass.FAST: "2",
    # AbilityClass.MEDIUM: "3",
    # AbilityClass.MEDIUM_OR_SLOW: "3/4",
    # AbilityClass.START_AND_REACTION: "1+R",
    # AbilityClass.SLOW: "4",
    AbilityClass.MELEE: "m",
    AbilityClass.RESOLUTION: "5",
    AbilityClass.REACTION: "R",
    AbilityClass.NON_COMBAT: "n",
    }


def find_pdftk():
    """
    Return a path to the pdftk executable on this platform.

    """
    if platform.system() == "Linux":
        pdftk_executable = "/usr/bin/pdftk"
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
    #print pdftk_executable
    cmd_line = [pdftk_executable,
                pdf_in,
                "fill_form",
                fdf_in,
                "output",
                pdf_out,
                "verbose"]
    print " ".join(cmd_line)
    try:
        pdftk_output = check_output(cmd_line) # , env=env)
    except OSError as e:
        print("Can't find file either %s or %s" % (pdf_in, fdf_in))
        raise e
    except CalledProcessError as e:
        pdftk_output = e.output
        pdftk_error = True
    return


#
#  Introduces weird artifacts in 
#

def pdf_merge(pdfs, pdf_out):
    """
    Run pdftk to merge pdfs

    """
    #print pdftk_executable
    cmd_line = [
        pdftk_executable,
    ] + pdfs +[
        "cat",
        "output",
        pdf_out,
        "verbose"]
    print " ".join(cmd_line)
    try:
        pdftk_output = check_output(cmd_line) # , env=env)
    except CalledProcessError as e:
        pdftk_output = e.output
        pdftk_error = True


    # fdf_name = "xx.fdf"
    # with file(fdf_name, "wb") as f:
    #     # if we have another ability level put fill in the form for
    #     # that ability, otherwise make it blank.
    #     #if archetype is not None:
    #     # 
    #     #     # write info from the ability
    #     #     fdf_info = FDF_PG1_BODY.format(
    #     #         archetype_title=archetype.get_title(),
    #     #         )
    #     # else:
    #     #     # write empty info
    #     #    fdf_info = FDF_PG1_BODY.format(
    #     #         archetype_title="",
    #     #         )

    #     # write the fdf
    #     #f.write(fdf_header)
    #     #f.write(fdf_info)
    #     f.write(fdf_hack)
        
    # # Hack to get rid of the black box that appears in
    # # the background notes pdf form text field for some
    # # strange reason.. (bug elsewhere).
    # print("XXXXXXXXXXXXXX")
    # pdftk_fill(pdf_out, fdf_name, "y.pdf")        
    return


# def pdf_merge(pdfs, pdf_out):
#     """
#     Run pdfunite to merge pdfs

#     """
#     ok = True
#     #print pdftk_executable
#     cmd_line = [
#         pdfunite_executable,
#     ] + pdfs + [pdf_out,]
#     print " ".join(cmd_line)
#     try:
#         output = check_output(cmd_line)
#     except CalledProcessError as e:
#         output = e.output
#         ok = False
#     return ok


def create_first_page_fdf(fdf_name, archetype=None):
    with file(fdf_name, "wb") as f:
        # if we have another ability level put fill in the form for
        # that ability, otherwise make it blank.
        if archetype is not None:
        
            # write info from the ability
            fdf_info = FDF_PG1_BODY.format(
                archetype_title=archetype.get_title(),
                )
        else:
            # write empty info
            fdf_info = FDF_PG1_BODY.format(
                archetype_title="",
                )

        # write the fdf
        f.write(fdf_header)
        f.write(fdf_info)
        f.write(fdf_footer)
    return



def create_abilities_fdf(fdf_name, ability_levels = None):
    with file(fdf_name, "wb") as f:
        f.write(fdf_header)
        
        for i in range(ABILITIES_PER_PAGE):

            # See if we can get another ability level to put in our char sheet.
            if ability_levels is None:
                ability_level = None
            else:
                try:
                    ability_level = ability_levels.next()
                except StopIteration:
                    ability_level = None

            # if we have another ability level put fill in the form for
            # that ability, otherwise make it blank.
            if ability_level is not None:

                mastery = ("y" * ability_level.get_mastery_successes() +
                           "?" * ability_level.get_mastery_attempts() +
                           "x" * ability_level.get_mastery_failures())
                check = ability_level.get_check()

                modifiers = ability_level.get_ability().get_attr_modifiers()
                #if len(modifiers) > 0:
                #   check += "  (%s)" % ", ".join(modifiers)
                check += "  " + ability_level.get_ability().get_attr_modifiers_str()
                # check = " X? "

                effect_type = ""
                effect = ""
                dmg = ability_level.get_damage()
                if dmg != "":
                    effect_type = "Dmg:"
                    effect = ability_level.get_damage()
                else:
                    effect = ability_level.get_effect()
                    if effect != "":
                        effect_type = "Effect:"                        

                overcharge_type = ""
                overcharge = ability_level.get_overcharge()
                if overcharge != "":
                    overcharge_type = "Overcharge:"
                else:
                    overcharge = ""

                ability_class = ability_level.get_ability_class()
                ability_class_str = ability_class_lookup[ability_class]

                # write info from the ability
                fdf_info = FDF_ABILITY_BODY.format(
                    ability_number=i,
                    ability_check=check,
                    ability_class=ability_class_str,
                    ability_name=ability_level.get_title(),
                    ability_effect_type=effect_type,
                    ability_effect=effect,
                    ability_overcharge_type=overcharge_type,
                    ability_overcharge=overcharge,
                    ability_mastery=mastery)
            else:
                # write empty info
                fdf_info = FDF_ABILITY_BODY.format(
                    ability_number=i,
                    ability_check="",
                    ability_class="",
                    ability_name="",
                    ability_effect_type="",
                    ability_effect="",
                    ability_overcharge_type="",
                    ability_overcharge="",
                    ability_mastery="")
                
            f.write(fdf_info)
        f.write(fdf_footer)
    return


from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, TextStringObject
# def x(pdf):
#     if "/AcroForm" in pdf.trailer["/Root"]:
#         pdf.trailer["/Root"]["/AcroForm"].update(
#             {NameObject("/NeedAppearances"): BooleanObject(True), }
#         )
#     pdf = PdfFileWriter()

#     if "/AcroForm" in pdf._root_object:
#         pdf._root_object["/AcroForm"].update(
#             {NameObject("/NeedAppearances"): BooleanObject(True), }
#         )        

# def compose_pdf(dest_fname, src_fnames):
#     char_sheet = PdfFileWriter()
#     for page_fname in src_fnames:
#         print "Reading %s" % page_fname
#         f = file(page_fname,"rb")
#         pdf = PdfFileReader(f)
#         #x(pdf)
#         page = pdf.getPage(0)
#         char_sheet.addPage(page)

#     char_sheet_file = file(dest_fname, "wb")
#     char_sheet.write(char_sheet_file)
#     return


# def compose_pdf(dest_fname, src_fnames):
#     char_sheet = PdfFileWriter()
#     fields = {}
#     for page_fname in src_fnames:
#         print "Reading %s" % page_fname
#         f = file(page_fname,"rb")
#         pdf = PdfFileReader(f)
#         #x(pdf)
#         page = pdf.getPage(0)

#         for i in range(pdf.getNumPages()):
#             page = pdf.getPage(i)

#             fields = pdf.getFormTextFields()
#             print "========"
#             print fields
#             for k, v in fields.items():
#                 print str((k, v))

#             #char_sheet.updatePageFormFieldValues(page, fields)

#             # Iterate through pages, update field values
#             for j in range(0, len(page['/Annots'])):
#                 writer_annot = page['/Annots'][j].getObject()
#                 for field in fields:
#                     print "FIELD  ... %s %s" % (field, fields[field])
#                     if writer_annot.get('/T') == field:
#                         writer_annot.update({
#                             NameObject("/V"): TextStringObject("X")
#                             # TextStringObject(fields[field])
#                         })
#             char_sheet.addPage(page)


#         #fields = pdf.getFields()
#         fields = pdf.getFormTextFields()
#         print fields
#         for k, v in fields.items():
#             print str((k, v))
#         #char_sheet.addPage(page)
 
#         # page2 = char_sheet.getPage(0)
        
#     char_sheet_file = file(dest_fname, "wb")
#     char_sheet.write(char_sheet_file)
#     # char_sheet.close()
#     char_sheet_file.close()

#     print "----------------"
#     f = file(dest_fname, "rb")
#     pdf = PdfFileReader(f)
#     print pdf.getFields()
    
#     return


# def compose_pdf(dest_fname, src_fnames):
#     char_sheet = PdfFileMerger()
#     fields = {}
#     for page_fname in src_fnames:
#         print "Reading %s" % page_fname
#         with file(page_fname, "rb") as f:
#             pdf = PdfFileReader(f)
#             #page = pdf.getPage(0)
#             #char_sheet.addPage(page)
#             fields.update(pdf.getFields())
#             char_sheet.merge(0, pdf)

#     char_sheet_file = file(dest_fname, "wb")
#     char_sheet.write(char_sheet_file)
#     char_sheet.close()
#     char_sheet_file.close()


#     print "----------------"
#     writer = PdfFileWriter()
#     writer.updatePageFormFieldValues(0, fields)
    
#     print "----------------"
#     f = file(dest_fname, "rb")
#     pdf = PdfFileReader(f)
#     print pdf.getFields()
    
#     return


def cmp_titles(ability, ability2):
    return cmp(ability.get_title(), ability2.get_title())


def create_character_sheet_for_archetype(archetype):

    print("============================")
    
    # build a list containing all the archetypes available abilities.
    ability_levels = []
    for ability_group in archetype.modified_ability_groups:
        print("\t%s" % ability_group.get_title())        
        for ability in ability_group:
            print("\t\t%s" % ability.get_title())            
            ability_level = ability.get_highest_innate_level()
            print("\t\t%s" % ability_level)
            #if ability_level is not None:
            #    raise Exception("XXXXX")
            if ability_level is not None and ability_level.is_enabled():
                print("\t\t%s" % ability_level.get_title())                        
                ability_levels.append(ability_level)

                
            #if ability_level is not None and ability_level.is_innate_for_this_archetype():
            #    print("GG")
            #    raise Exception("GG")

    ability_levels.sort(cmp_titles)
    
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
    n_pages = len(ability_levels) / ABILITIES_PER_PAGE + 2

    # create all the ability pages    
    ability_level_iterator = iter(ability_levels)
    for i in range(n_pages):
        page_number = i + 2
        pdf_fname_out = join(build_dir,"%s_abilities_pg%s.pdf" % (archetype_id, page_number))
        fdf_fname = join(build_dir, "%s_abilities_pg%s.fdf" % (archetype_id, page_number))
        pdf_pages.append(pdf_fname_out)

        # create one character sheet abilities pdf page
        create_abilities_fdf(fdf_fname, ability_level_iterator)
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
        print("Missing pdf: %s" % pdf_fname)
    return

                     
def create_character_sheets_for_all_archetypes(archetypes):
    for archetype in archetypes:
        create_character_sheet_for_archetype(archetype)
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
    

if __name__ == "__main__":

    from abilities import AbilityGroups
    ability_groups = AbilityGroups()
    ability_groups.load(ability_groups_dir, fail_fast=True)

    archetypes = Archetypes()
    archetypes.load(ability_groups, archetypes_dir, fail_fast=True)
            
    create_character_sheets_for_all_archetypes(archetypes=archetypes)
    create_empty_abilities_sheet()
    # done.
