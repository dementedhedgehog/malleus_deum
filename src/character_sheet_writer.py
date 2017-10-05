#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

To get the fdf from a form
pdftk 1.pdf dump_data_fields output test2.txt


pdftk ./resources/character_sheets/character_sheet_abilities.pdf generate_fdf output x.fdf verbose

To set the form values in a pdf
pdftk test.pdf fill_form test.fdf output out.pdf verbose


"""
from shutil import copy

# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.lib.units import inch
# from reportlab.pdfbase.pdfmetrics import stringWidth
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
from os.path import join, dirname, abspath, exists
# from reportlab.platypus import SimpleDocTemplate, Image
import platform


from utils import resources_dir, build_dir
from archetypes import Archetypes
from abilities import AbilityClass

from subprocess import call, check_output, CalledProcessError


tick = u""
cross = u""
question_mark = u""

# fdf = """\
# %FDF-1.2
# 1 0 obj<</FDF<< /Fields[
# << /T(AbilityName0) /V(sfdg) 
# ] >> >>
# endobj
# trailer
# <</Root 1 0 R>>
# %%EOF
# """

# fdf = """
# %FDF-1.2
# %âãÏÓ
# 1 0 obj 
# <<
# /FDF 
# <<
# /Fields [
# <<
# /V (X)
# /T (AbilityCheck0)
# >> 
# <<
# /V (a)
# /T (AbilityClass0)
# >> 
# <<
# /V (e)
# /T (AbilityEffect0)
# >> 
# <<
# /V (t)
# /T (AbilityEffectType0)
# >> 
# <<
# /V (Z)
# /T (AbilityName0)
# >>]
# >>
# >>
# endobj 
# trailer

# <<
# /Root 1 0 R
# >>
# %%EOF
# """


fdf_header = """
%FDF-1.2
%<E2><E3><CF><D3>
1 0 obj 
<<
/FDF 
"""

fdf_body = """
<<
/Fields [
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
/V ({ability_effect_number})
/T (AbilityEffectType{ability_number})
>> 
<<
/V ({ability_effect})
/T (AbilityEffect{ability_number})
>>
"""

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

character_sheets_dir = join(resources_dir, "character_sheets")

ability_class_lookup = {
    AbilityClass.AMBUSH: "a",
    AbilityClass.SURPRISE: "s",
    AbilityClass.INITIATIVE: "i",
    #AbilityClass.RESOLVE: "r",
    #AbilityClass.AMBUSH: "a",
    #AbilityClass.AMBUSH: "a",
    #AbilityClass.AMBUSH: "a",
    #AbilityClass.AMBUSH: "a",
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
    return pdftk_executable

pdftk_executable = find_pdftk()


def pdftk(pdf_in, fdf_in, pdf_out):

    print pdftk_executable
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
    except CalledProcessError as e:
        pdftk_output = e.output
        pdftk_error = True
    return


def create_fdf(fdf_name, abilities):
    with file(fdf_name, "wb") as f:
        f.write(fdf_header)
        for ability in abilities:
            f.write(fdf_body.format(**ability.__dict__()))
        f.write(fdf_footer)
    return


if __name__ == "__main__":
    #create_character_sheets_for_all_archetypes()
    #create_empty_abilities_sheet()

    pdf_in = join(character_sheets_dir, "character_sheet_abilities.pdf")
    fdf_name = join(build_dir, "character_sheet_abilities.fdf")
    pdf_out = join(build_dir, "character_sheet_abilities.pdf")

    

    #print fdf_name
    
    create_fdf(fdf_name, None)
    pdftk(pdf_in, fdf_name, pdf_out)

    #pdftk = find_pdftk()
    
    # done.


# def register_font(font_name):
#     font = TTFont(font_name, join(fonts_dir, '%s.ttf' % font_name))
#     pdfmetrics.registerFont(font)
#     return font_name

# # Fonts.
# SHERWOOD = register_font('Sherwood')
# LIBERTINE_BOLD = register_font("LiberationSerif-Bold")
# FONTAWESOME = register_font("fontawesome-webfont")
# RPGDICE =  register_font("RPGDice")

# SMALL = 5
# MEDIUM = 8
# LARGE = 10
# HUGE = 14

# _font_name = LIBERTINE_BOLD
# _font_size = 12
# _font_ascent = 1


# def draw_string(c, x, y, text):
#     c.drawString(x, y, text)
#     text_width = stringWidth(text, _font_name, _font_size)        
#     return (x + text_width, y)


# def set_font(c, font_name = None, font_size = None):
#     global _font_name
#     global _font_size
#     global _font_ascent
    
#     if font_name is not None:
#         _font_name = font_name

#     if font_size is not None:
#         _font_size = font_size
        
#     c.setFont(_font_name, _font_size)
#     _font_ascent, _ = pdfmetrics.getAscentDescent(_font_name, _font_size)
#     return


# def get_font_height():
#     return _font_ascent

# def get_text_width(text):
#     return stringWidth(text, _font_name, _font_size)        
    

# def draw_cell(c, x, y, cell_width, cell_height, ability_level=None):
#     y2 = y + cell_height
#     x2 = x + cell_width

#     # draw the cell border
#     c.line(x, y, x, y2)
#     c.line(x, y2, x2, y2)
#     c.line(x, y, x2, y)
#     c.line(x2, y, x2, y2)

#     # Set the font and starting point
#     set_font(c, font_name=LIBERTINE_BOLD, font_size=SMALL)
#     left_margin = x + 3
#     top_margin = y + 7

#     # Name:
#     x3, y3 = draw_string(c, left_margin, top_margin, "Name: ")

#     # <ability_name>
#     if ability_level is not None:
#         set_font(c, font_name=SHERWOOD, font_size=MEDIUM)
#         draw_string(c, x3, y3, ability_level.get_title())

#     # Check:
#     set_font(c, font_name=LIBERTINE_BOLD, font_size=SMALL)
#     x4, y4 = draw_string(c, left_margin, top_margin + 10, "Check: ")

#     # <ability_name>
#     if ability_level is not None:
#         check = ability_level.get_check()
#         if check is not None:
#             #set_font(c, font_name=SHERWOOD, font_size=12)
#             x5, y5 = draw_string(c, x4, y4, check)

#     # Dmg: ????
#     if ability_level is not None and ability_level.get_family() == "Combat":
#         dmg = ability_level.get_damage()
#         if dmg is not None and dmg.strip() != "":            
#             set_font(c, font_name=LIBERTINE_BOLD, font_size=SMALL)
#             x6, y6 = draw_string(c, left_margin, y5 + 10, "Dmg: ")
#             draw_string(c, x6, y6, dmg)


#     # ability class
#     set_font(c, font_name=RPGDICE, font_size=HUGE)
#     ability_class_str = "a"
#     draw_string(c,
#                 x + cell_width - get_text_width(ability_class_str) - 3,
#                 y + 13,
#                 ability_class_str)
   
#     # mastery
#     if ability_level is not None:
#         mastery = (tick * ability_level.get_mastery_successes() +
#                    question_mark * ability_level.get_mastery_attempts() +
#                    cross * ability_level.get_mastery_failures())
#         if mastery != "":    
#             set_font(c, font_name=FONTAWESOME, font_size=MEDIUM)
#             draw_string(c,
#                         x + cell_width - get_text_width(mastery) - 2,
#                         y + cell_height - 5,
#                         mastery)
#     return


# def draw_character_sheet_abilities(
#         rows, cols,
#         page_name,
#         page_size,
#         ability_levels_iterator):
#     c = canvas.Canvas(page_name,
#                       pagesize=page_size,
#                       bottomup=False)
    
#     width, height = page_size
#     left_margin = 0.22 * inch  # 1 * inch
#     right_margin = width - 0.27 * inch
#     top_margin = 0.49 * inch
#     bottom_margin = height - 0.22 * inch

#     draw_height = bottom_margin - top_margin
#     draw_width = right_margin - left_margin
#     row_height = draw_height / rows
#     col_width = draw_width / cols

    
#     # draw the cells
#     for col in range(cols):
#         x1 = left_margin + col * col_width
#         for row in range(rows):
#             y1 = top_margin + row * row_height

#             # draw the cell contents
#             try:
#                 ability_level = ability_levels_iterator.next()
#             except StopIteration:
#                 ability_level = None
#             draw_cell(c, x1, y1, col_width, row_height, ability_level)

#     # draw the watermark
#     img = join(resources_dir, "dragon_title_watermark.png")
#     c.drawImage(img,
#                 left_margin, top_margin,
#                 width = draw_width,
#                 height = draw_height,
#                 mask='auto')    
#     c.save()
#     return


# def compose_pdf(dest_fname, src_fnames):
#     from PyPDF2 import PdfFileWriter, PdfFileReader

#     char_sheet = PdfFileWriter()
#     for page_fname in src_fnames:
#         print "Reading %s" % page_fname
#         f = file(page_fname,"rb")
#         pdf = PdfFileReader(f)
#         page = pdf.getPage(0)
#         char_sheet.addPage(page)

#     char_sheet_file = file(dest_fname, "wb")
#     char_sheet.write(char_sheet_file)
#     return
    

# def create_character_sheet_for_archetype(archetype):

#     N_ROWS_PER_ABILITY_PAGE = 16
#     N_COLS_PER_ABILITY_PAGE = 2
#     ABILITIES_PER_PAGE = N_ROWS_PER_ABILITY_PAGE * N_COLS_PER_ABILITY_PAGE

#     ability_levels = []
#     for ability_group in archetype.modified_ability_groups:
#         print("\t%s" % ability_group.get_title())
        
#         for ability in ability_group:
#             ability_level = ability.get_highest_innate_level()
#             if ability_level is not None:
#                 ability_levels.append(ability_level)

#     # work out how many ability pages we need
#     n_pages = len(ability_levels) / ABILITIES_PER_PAGE
#     if ABILITIES_PER_PAGE - (len(ability_levels) % ABILITIES_PER_PAGE) < 10:
#         n_pages += 1

        
#     ability_level_iterator = iter(ability_levels)
#     pdf_pages = []
#     for i in range(n_pages):

#         pdf_fname = join(build_dir,
#                          "%s_abilities_%spg.pdf" % (archetype.get_id(), i + 2))
#         pdf_pages.append(pdf_fname)
    
#         # draw the character sheet
#         draw_character_sheet_abilities(
#             16, 2,
#             pdf_fname,
#             A4,
#             ability_level_iterator)
    
#     # now compose the pdf.
#     pdf_pages.insert(0, join(char_sheet_dir, "character_sheet_pg1.pdf"))
#     pdf_pages.append(join(char_sheet_dir, "character_sheet_equipment.pdf"))
#     pdf_pages.append(join(char_sheet_dir, "character_sheet_notes.pdf"))
#     char_sheet_fname = join(build_dir, "%s_char_sheet.pdf" % archetype.get_id())
#     compose_pdf(char_sheet_fname, pdf_pages)

#     # copy the final pdf to the pdfs dir
#     if exists(char_sheet_fname):
#         copy(char_sheet_fname, pdfs_dir)
#     else:
#         print("Missing pdf: %s" % pdf_fname)
#     return
    
                     
# def create_character_sheets_for_all_archetypes():
#     from abilities import AbilityGroups
#     ability_groups = AbilityGroups()
#     ability_groups.load(ability_groups_dir, fail_fast = True)

#     archetypes = Archetypes()
#     archetypes.load(ability_groups, archetypes_dir, fail_fast = True)
#     for archetype in archetypes:
#         print("Archetype: %s" % archetype.get_title())
#         create_character_sheet_for_archetype(archetype)
#     return

# def create_empty_abilities_sheet():

#     pdf_fname = join(build_dir, "extra_abilities.pdf")
    
#     # draw the character sheet
#     draw_character_sheet_abilities(
#         16, 2,
#         pdf_fname,
#         A4,
#         iter([]))
    
#     # copy the final pdf to the pdfs dir
#     if exists(pdf_fname):
#         copy(pdf_fname, pdfs_dir)
#     else:
#         print("Missing pdf: %s" % pdf_fname)
#     return
    

# if __name__ == "__main__":
#     create_character_sheets_for_all_archetypes()
#     create_empty_abilities_sheet()
#     # done.
