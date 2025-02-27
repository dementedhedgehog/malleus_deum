# -*- coding: utf-8 -*-
# from os import exists
from os.path import join, splitext, exists
import sys
import config
from utils import (
    normalize_ws,
    convert_str_to_bool,
    convert_str_to_int,
    COMMENT,
    attrib_is_true,
    get_text_for_child
)
from config import use_imperial

from npcs import NPC, NPCGroup

from ebooklib import epub



table_state = None

class TableState:

    def __init__(self):
        self.label = None

        # list of (index entry / sub entry)
        self.index_entries = []


class TableCategory:
    Standard = "Standard"
    Figure = "Figure"
    Fullwidth = "FullWidth"
    Sideways = "Sideways"    


class EPubFormatter:
    
    def __init__(self, epub_fname, db):

        # epub filename
        self.epub_fname = epub_fname
        self.book = None
        
        # for tables
        self._number_of_columns_in_table = 0
        self._current_column_in_table = 0
        self._current_row_in_table = 0

        # for equations (indent second and subsequent lines)
        self._equation_first_line = True

        # for level tables FIXME: remove this.
        self._current_row_in_level_table = 0

        # for descriptions
        self.description_terms_on_their_own_line = False

        # for the index_entry see field (None or a string).
        self.index_entry_subentry = None

        # keep track of state for npc blocks
        self._in_npc_group = False

        # game db
        self.db = db
        return

    def verify(self):
        verifyObject(IFormatter, self)
        return

    def no_op(self, obj):
        """
        We've got a lot of handlers that don't need to do anything..
        do nothing once.
        """
        pass

    
    def start_book(self, book):        
        # must be a valid latex paper size
        # if config.paper_size == "a4":
        #     paper_size = "a4paper"
        # elif config.paper_size == "letter":
        #     paper_size = "letterpaper"
        # else:
        #     raise Exception("Unknown paper size.  "
        #                     "Pick one of [a4, letter] in config.py")
        # orientation = ""
        # landscape = attrib_is_true(book, "landscape")
        # formatting = paper_size + orientation
        # self.latex_file.write(latex_frontmatter % formatting)

        # if config.display_page_background:
        #     self.latex_file.write(
        #         "\n"
        #         "% use a background image\n"
        #         "\\CenterWallPaper{1.0}{./resources/paper_" + paper_size + ".jpg}"
        #         "\n\n")
        self.book = epub.EpubBook()
        self.book.set_language('en')
        return

    def end_book(self, book):
        #self.latex_file.write("\\end{document}\n")
        
        # write to the file
        epub.write_epub(self.epub_fname, self.book, {})
        return

    def start_appendix(self, appendix):
        # self.latex_file.write("\\appendix\n"
        #                       "\\addcontentsline{toc}{chapter}{APPENDICES}\n")
        return
    end_appendix = no_op

    # symbols handled specially by the subsectiontitle
    # HACK!!
    # start_ambushsymbol = no_op
    # end_ambushsymbol = no_op
    # start_surprisesymbol = no_op
    # end_surprisesymbol = no_op    
    # start_initiativesymbol = no_op
    # end_initiativesymbol = no_op
    # start_talksymbol = no_op
    # end_talksymbol = no_op
    # start_fightreachsymbol = no_op
    # end_fightreachsymbol = no_op
    # start_startsymbol = no_op
    # end_startsymbol = no_op
    # start_fastsymbol = no_op
    # end_fastsymbol = no_op
    # start_mediumsymbol = no_op
    # end_mediumsymbol = no_op
    # start_slowsymbol = no_op
    # end_slowsymbol = no_op
    # start_mediumorslowsymbol = no_op
    # end_mediumorslowsymbol = no_op
    # start_startandreactionsymbol = no_op
    # end_startandreactionsymbol = no_op
    # start_resolutionsymbol = no_op
    # end_resolutionsymbol = no_op
    # start_noncombatsymbol = no_op
    # end_noncombatsymbol = no_op
    # start_reactionsymbol = no_op
    # end_reactionsymbol = no_op

    def start_fightreach(self, symbol):
        #self.latex_file.write("\\fightreachsymbol{}")
        return
    end_fightreach = no_op    

    def start_start(self, symbol):
        #self.latex_file.write("\\startsymbol{}")
        return
    end_start = no_op    
    
    def start_melee(self, symbol):
        #self.latex_file.write("\\meleesymbol{}")
        return
    end_melee = no_op
    
    def start_immediate(self, symbol):
        #self.latex_file.write("\\immediatesymbol{}")
        return
    end_immediate = no_op

    #
    # Corollarys
    #
    def start_corollary(self, symbol):
        #self.latex_file.write("\\begin{corollary}")
        return
    
    def end_corollary(self, symbol):
        #self.latex_file.write("\\end{corollary}")
        return

    def start_corollary(self, symbol):
        #self.latex_file.write("\\begin{corollary}")
        return

    def start_corollarytitle(self, symbol):
        #self.latex_file.write("[")
        return
    
    def end_corollarytitle(self, symbol):
        #self.latex_file.write("]")
        return
    
    start_corollarybody = no_op
    end_corollarybody = no_op
    
    def end_corollary(self, symbol):
        #self.latex_file.write("\\end{corollary}")
        return


    #
    # Principles
    #
    start_principlebody = no_op
    end_principlebody = no_op

    def start_principle(self, symbol):
        #self.latex_file.write("\\begin{principle}")
        return
    
    def end_principle(self, symbol):
        #self.latex_file.write("\\end{principle}")
        return    

    def start_principletitle(self, symbol):
        #self.latex_file.write("[")
        return
    
    def end_principletitle(self, symbol):
        #self.latex_file.write("]")
        return
        
    def start_noncombat(self, symbol):
        #self.latex_file.write("\\noncombatsymbol{}")
        return
    end_noncombat = no_op    

    def start_tag(self, symbol):
        #self.latex_file.write("\\tagsymbol{}")
        return
    end_tag = no_op    

    def start_newpage(self, symbol):
        #self.latex_file.write("\\newpage[4]\n")
        return
    end_newpage = no_op    

    def start_resolution(self, symbol):
        #self.latex_file.write("\\resolutionsymbol{}")
        return
    end_resolution = no_op
    
    def start_talk(self, symbol):
        #self.latex_file.write("\\talksymbol{}")
        return
    end_talk = no_op
    
    def start_act(self, symbol):
        #self.latex_file.write("\\actsymbol{}")
        return
    end_act = no_op

    def start_ambush(self, symbol):
        #self.latex_file.write("\\ambushsymbol{}")
        return
    end_ambush = no_op
    
    def start_surprise(self, symbol):
        #self.latex_file.write("\\surprisesymbol{}")
        return
    end_surprise = no_op
    
    def start_reaction(self, symbol):
        #self.latex_file.write("\\reactionsymbol{}")
        return
    end_reaction = no_op
    
    def start_initiative(self, symbol):
        #self.latex_file.write("\\initiativesymbol{}")
        return
    end_initiative = no_op

    def start_physical(self, symbol):
        #self.latex_file.write("\\physicalsymbol{}")
        return
    end_physical = no_op

    def start_defensive(self, symbol):
        #self.latex_file.write("\\defensivesymbol{}")
        return
    end_defensive = no_op

    def start_arrowleft(self, symbol):
        #self.latex_file.write("\\arrowleft{}")
        return
    end_arrowleft = no_op    

    start_subsubsection = no_op
    end_subsubsection = no_op

    def start_subsubsectiontitle(self, section_title):
        #self.latex_file.write("\\subsubsection{")
        return
    def end_subsubsectiontitle(self, section_title):
        #self.latex_file.write("}")
        return    

    def start_abilitytitle(self, section_title):
        #self.latex_file.write("\\ability{")
        return
    def end_abilitytitle(self, section_title):
        #self.latex_file.write("}")
        return    
        
    start_ability_title = no_op
    end_ability_title = no_op

    def start_ability_id(self, ability_id):        
        #self.latex_file.write("ID: %s\\\n" % ability_id) 
        return
    end_ability_id = no_op

    start_ability_group = no_op
    def end_ability_group(self, ability_group):
        #self.latex_file.write("%s\n" % normalize_ws(ability_group.text))
        return

    start_ability_class = no_op
    def end_ability_class(self, ability_class):
        #self.latex_file.write("%s\n" % normalize_ws(ability_class.text))
        return

    start_action_points = no_op
    def end_action_points(self, action_points):
        #self.latex_file.write("%s\n" % normalize_ws(action_points.text))
        return

    def start_and(self, and_element):
        #self.latex_file.write("\\&")
        return
    end_and = no_op

    def start_lore(self, element):
        #self.latex_file.write("\\lore{}")
        return    
    end_lore = no_op

    def start_martial(self, element):
        #self.latex_file.write("\\martial{}")
        return    
    end_martial = no_op

    def start_percent(self, element):
        #self.latex_file.write("\\%")
        return    
    end_percent = no_op

    def start_general(self, element):
        #self.latex_file.write("\\general{}")
        return    
    end_general = no_op

    def start_magical(self, element):
        #self.latex_file.write("\\magical{}")
        return    
    end_magical = no_op

    def start_geqqsymbol(self, geqq_element):
        #self.latex_file.write("$\stackrel{\scriptscriptstyle ?}{\geq}{}$")
        return
    end_geqqsymbol = no_op

    def start_leqqsymbol(self, geqq_element):
        #self.latex_file.write("$\stackrel{\scriptscriptstyle ?}{\leq}{}$")
        return
    end_leqqsymbol = no_op

    def start_leqsymbol(self, leq_element):
        #self.latex_file.write("$\leq$")
        return
    end_leqsymbol = no_op

    def start_geqsymbol(self, geq_element):
        #self.latex_file.write("$\geq$")
        return
    end_geqsymbol = no_op

    def start_newline(self, newline):
        #self.latex_file.write("\\newline\n")
        return
    end_newline = no_op

    start_pageref = no_op
    def end_pageref(self, pageref):
        #self.latex_file.write("~\\pageref{%s}" % normalize_ws(pageref.text))
        return

    start_ref = no_op
    def end_ref(self, ref):
        #self.latex_file.write("~\\ref{%s}" % normalize_ws(ref.text))
        return

    def start_index(self, index):
        #self.latex_file.write("\\clearpage\n")               
        #self.latex_file.write("\\addcontentsline{toc}{chapter}{Index}\n")               
        #self.latex_file.write("\\printindex\n")
        return
    end_index = no_op

    start_section = no_op
    end_section = no_op

    def start_sectiontitle(self, section_title):
        #self.latex_file.write("\\section{")#  % title)               
        return

    def end_sectiontitle(self, section_title):
        #self.latex_file.write("}\n")#  % title)               
        return
    
    start_subsection = no_op
    end_subsection = no_op

    def start_subsectiontitle(self, section_title):
        #self.latex_file.write("\\subsection{")
        return
    def end_subsectiontitle(self, section_title):
        #self.latex_file.write("}")
        return

    def start_playexample(self, playexample):
        #self.latex_file.write("\\begin{playexample}\n")
        return

    def end_playexample(self, playexample):
        #self.latex_file.write(playexample.text)                
        #self.latex_file.write("\\end{playexample}\n")        
        return
        
    def start_level(self, level):
        #self._current_row_in_level_table += 1
        #if self._current_row_in_level_table % 2 == 1:            
        #    self.latex_file.write("\\rowcolor{blue!20} \n")
        #else:
        #    self.latex_file.write("\\rowcolor{white!20} \n")
        return
    
    def end_level(self, level):
        #self.latex_file.write(" \\\\\n")
        return

    def start_leveltitle(self, level_title_node):
        #self.latex_file.write("\\subsection{")
        return
    def end_leveltitle(self, level_title_node):
        #self.latex_file.write("}")
        return

    
        
    # def start_level_xp(self, element):
    #     #self.latex_file.write(" %s &" % element.text)
    #     return    
    # end_level_xp = no_op
    
    # def start_level_number(self, element):
    #     #self.latex_file.write(" %s &" % element.text)
    #     return    
    # end_level_number = no_op

    # def start_level_combat(self, element):
    #     #self.latex_file.write("\\rpgcombatsymbol %s " % element.text)
    #     return    
    # end_level_combat = no_op

    # def start_level_training(self, element):
    #     #self.latex_file.write("\\rpgtrainingsymbol %s " % element.text)
    #     return    
    # end_level_training = no_op

    # def start_level_learning(self, element):
    #     #self.latex_file.write("\\rpglearningsymbol %s " % element.text)
    #     return    
    # end_level_learning = no_op
    
    # def start_level_description(self, element):
    #     #self.latex_file.write(" %s " % element.text)
    #     return

    # def end_level_description(self, element):
    #     pass

    def start_titlepage(self, chapter):
        #self.latex_file.write("\\begin{titlepage}\n"
        #                      "\\begin{center}\n")
        return

    def end_titlepage(self, chapter):
        #self.latex_file.write("\\end{center}\n"
        #                      "\\end{titlepage}\n")
        return

    def start_emph(self, emph):
        return

    def end_emph(self, emph):
        #self.latex_file.write("\\emph{%s}" % normalize_ws(emph.text))
        return

    def start_equation(self, equation):
        #self._equation_first_line = True
        #self.latex_file.write("\\begin{tabbing}\n "
        #                      "\\hspace*{0.5cm}\= \kill \\nopagebreak \n")
        return

    def end_equation(self, equation):
        #self.latex_file.write("\\end{tabbing}\\vspace{-0.5cm}\n ")
        return


    def start_line(self, line):
        """
        Start equation line.
        
        """
        #if not self._equation_first_line:
        #    self.latex_file.write("\\> ") 
        #self._equation_first_line = False
        #if line.text:
        #    self.latex_file.write(" %s " % normalize_ws(line.text))
        return

    def end_line(self, line):
        #self.latex_file.write("\\\\\n ")
        return


    def start_bold(self, bold):
        #self.latex_file.write("\\textbf{%s} " % normalize_ws(bold.text))
        return
    end_bold = no_op

    def start_smaller(self, smaller):
        #self.latex_file.write("\\begin{smaller} ")
        return
    def end_smaller(self, smaller):
        #self.latex_file.write("\\end{smaller}")
        return

    def handle_text(self, text):
        #if text is not None:
        #    if isinstance(text, str):                           
        #        self.latex_file.write(text)
        #    else:
        #        self.latex_file.write(text)
        return


    def write_index(self, index_entry, index_subentry):
        #if index_subentry is not None:
        #    self.latex_file.write("\\index{%s!%s}" % (
        #        normalize_ws(index_entry.text), index_subentry))
        #else:
        #    self.latex_file.write("\\index{%s}" % normalize_ws(index_entry.text))
        return


    start_indexentry = no_op
    def end_indexentry(self, index_entry):
        #global table_state
        #if table_state is not None:
        #    table_state.index_entries.append(
        #        (index_entry, self.index_entry_subentry))
        #else:
        #    self.write_index(index_entry, self.index_entry_subentry)
        #self.index_entry_subentry = None
        return

    # subentry element in index entry
    start_subentry = no_op
    def end_subentry(self, index_subentry):
        #self.index_entry_subentry = normalize_ws(index_subentry.text)
        return

    def start_defn(self, defn):
        #self.latex_file.write(" \\textbf{%s}" % (normalize_ws(defn.text)))
        return
    end_defn = no_op


    def start_measurement(self, distance):
        #if use_imperial:
        #    distance_text = get_text_for_child(distance, "imperial")
        #    if distance_text is None:
        #        raise Exception("Imperial distance not specified!")
        #
        #else:
        #    distance_text = get_text_for_child(distance, "metric")
        #    if distance_text is None:
        #        raise Exception("Metric distance not specified!")
        #
        #self.latex_file.write(normalize_ws(distance_text).strip())
        return
    end_measurement = no_op

    start_metric = no_op
    end_metric = no_op
    start_imperial = no_op
    end_imperial = no_op    
    
    def start_chapter(self, chapter):
        title_element = chapter.find("chaptertitle")
        if title_element is None:
           title = ""
        else:
           title = title_element.text
        #self.latex_file.write("\\chapter{%s}\n" % title)

        # add chapter
        chapter_fname = f'{title}.xhtml'
        chapter = epub.EpubHtml(title=title, file_name=chapter_fname, lang='en')
        chapter.content=u'<h1>Intro heading</h1><p>Zaba je skocila u baru.</p>'
        self.book.add_item(chapter)

        # define Table Of Contents
        self.book.toc = (
            epub.Link(chapter_fname, 'Introduction', 'intro'),
            (epub.Section('Simple book'), (chapter, )))
        return

    def end_chapter(self, chapter):
        # remember to drop cap the first letter of the word in this chapter
        #self._drop_capped_first_letter_of_chapter = False
        return

    def start_p(self, paragraph):
        """
        Start paragraph.

        """
        #self.latex_file.write("\n\n")

        # turn of paragraph indentation?
        #no_indent = attrib_is_true(paragraph, "noindent")
        #if no_indent:
        #    self.latex_file.write("\\noindent ")
                
        # add drop caps to the first word of every chapter
        #if not self._drop_capped_first_letter_of_chapter:
        #    self._drop_capped_first_letter_of_chapter = True
        #    if paragraph.text:
        #        words = paragraph.text.split()
        #    else:
        #        words = []
        #    if len(words) > 0:
        #        first_word = words[0]
        #        if len(first_word) > 0:
        #            first_letter = first_word[0]
        #            other_letters = first_word[1:]
        #
        #            drop_cap_word = ("\\lettrine["
        #                             "lines=2, "
        #                             "lraise=0.1, "
        #                             # horizontal displacement of the indented text
        #                             "findent=-0.14em, " 
        #                             "nindent=0.3em, "
        #                             "slope=0em]{\\rpgdropcapfont %s}{%s}" %
        #                             (first_letter, other_letters))
        #        words = [drop_cap_word, ] + words[1:]
        return

    def end_p(self, paragraph):
        #self.latex_file.write("\n\n")
        return

    def start_design(self, design):
        #if config.print_design_notes:
        #    self.latex_file.write("\n\n")
        #    self.latex_file.write(design.text)        
        return

    def end_design(self, design):
        #self.latex_file.write("\n\n")
        return

    def start_provenance(self, provenance):
        #self.latex_file.write("\n\n")
        #if config.print_provenence_notes:
        #    self.latex_file.write("\\begin{center}")
        #    self.latex_file.write("\\begin{minipage}[c]{0.9\linewidth}")
        #    self.latex_file.write("\\rpgprovenancesymbol\\hspace{0.2em}") 
        #    self.latex_file.write(provenance.text)        
        return

    def end_provenance(self, provenance):
        #if config.print_provenence_notes:
        #    self.latex_file.write("\\end{minipage}")        
        #    self.latex_file.write("\\end{center}")
        #    self.latex_file.write("\n\n")
        return


    def start_author(self, author):
        #self.latex_file.write("{\\LARGE \\rpgtitleauthorfont %s}\\\\" % author.text)        
        self.book.add_author(author.text,
                             #file_as='Gospodin Danko Bananko',
                             #role='ill',
                             uid='coauthor')
        return

    def end_author(self, author):
        return

    def start_version(self, version):
        return
    
    def end_version(self, npchps):
        return

    
    def start_title(self, title):
        #self.latex_file.write("{ \\color{rpgtitlefontcolor} \\rpgtitlefont %s }\\\\\n"
        #                      % title.text)
        self.book.set_title(title.text)
        return

    def end_title(self, title):
        return

    def start_caption(self, caption):
        #self.latex_file.write("\\caption{%s}" % caption.text)
        return

    def end_caption(self, caption):
        return

    def start_subtitle(self, subtitle):        
        #self.latex_file.write("{\\large \\rpgtitlesubtitlefont  %s}\\\\\n" % subtitle.text)
        return

    def end_subtitle(self, title):
        return

    start_chaptertitle = no_op
    end_chaptertitle = no_op

    def start_img(self, img):
        #if config.draw_imgs:
        #    if config.debug_outline_images:
        #        self.latex_file.write("\\fbox{")
        #
        #    self.latex_file.write("\t\\begin{center}\n")
        #
        #    # 
        #    if "src" in img.attrib:
        #        filename = img.get("src")
        #        
        #    elif "id" in img.attrib:
        #        resource_id = img.get("id")
        #        resource = self.db.licenses.find(resource_id)
        #        filename = resource.get_fname()
        #        self.latex_file.write("\\addcontentsline{loa}{section}{%s}"
        #                              % resource.get_contents_desc())
        #    else:
        #        raise Exception("Image missing source or id!")
        #
        #    if not exists(filename):
        #        raise Exception("Image does not exist: %s" % filename)
        #    
        #    # image without a box
        #    self.latex_file.write("\t\\includegraphics[scale=%s]{%s}\n"
        #                          % (img.get("scale", default="1.0"), filename))
        return

    def end_img(self, img):
        #if img.text is not None:
        #    self.latex_file.write("\t%s\n" % img.text)
        #self.latex_file.write("\t\\end{center}\n")
        #if config.debug_outline_images:
        #    self.latex_file.write("}")
        return

    def start_figure(self, figure):
        #position = "ht"
        #if "position" in figure.attrib:
        #    position = figure.get("position")
        #
        #if attrib_is_true(figure, "fullwidth"):
        #    if attrib_is_true(figure, "sideways"):
        #        figure_name = "sidewaysfigure*"
        #    else:
        #        figure_name = "figure*"
        #else:
        #    if attrib_is_true(figure, "sideways"):
        #        figure_name = "sidewaysfigure"
        #    else:
        #        figure_name = "figure"
        #
        #self.latex_file.write("\\begin{%s}[%s]\n" % (figure_name, position))
        #self.latex_file.write("\\centering\n")
        return

    def end_figure(self, figure):
        #caption = figure.get("caption")
        #if caption is not None:
        #    self.latex_file.write("\\caption{%s}\n" % caption)        
        #
        #if attrib_is_true(figure, "fullwidth"):
        #    if attrib_is_true(figure, "sideways"):
        #        figure_name = "sidewaysfigure*"
        #    else:
        #        figure_name = "figure*"
        #else:
        #    if attrib_is_true(figure, "sideways"):
        #        figure_name = "sidewaysfigure"
        #    else:
        #        figure_name = "figure"
            
        #self.latex_file.write("\\end{%s}\n" % figure_name)            
        return

    def start_olist(self, enumeration):
        """
        Start enumeration, ordered list of things.

        """
        # the [i] gets us roman numerals in the enumeration
        #self.latex_file.write("\\begin{enumerate}[i.]\n")
        return

    def end_olist(self, enumeration):
        #self.latex_file.write("\\end{enumerate}\n")
        return

    def start_descriptions(self, description_list):
        #self.latex_file.write("\\begin{description}\n")
       
        #self.description_terms_on_their_own_line = False
        #if "termonnewline" in description_list.attrib:
        #    self.description_terms_on_their_own_line = description_list.get("termonnewline")
        return

    def end_descriptions(self, description_list):
        # note seeing weird artifacts in embedded latex lists without the extra newline
        #self.latex_file.write("\\end{description}\n\n")
        return

    def start_term(self, term):
        """
        A description term.

        """
        #self.latex_file.write("\\item[")
    def end_term(self, term):
        #self.latex_file.write("]")
        return

    def start_description(self, description):
        return
    def end_description(self, list_item):
        return

    def start_list(self, list_element):
        #self.latex_file.write("\\begin{itemize}\n")
        return

    def end_list(self, list_element):
        #self.latex_file.write("\\end{itemize}\n")
        return

    def start_li(self, list_item):
        """
        Start list item.

        """
        #self.latex_file.write("\\item ")
        
        #if list_item.text is not None:
        #    self.latex_file.write(normalize_ws(list_item.text))
    end_li = no_op

    def start_comment(self, comment):
        return

    def end_comment(self, comment):
        return

    #
    # Table
    #
    start_tablespec = no_op
    end_tablespec = no_op
    
    
    def start_table(self, table):        
        #global table_state
        #assert table_state is None

        #category = get_text_for_child(table, "tablecategory")
        #if category is None:
        #    raise Error("Table requires a tablecategory child element.")

        # Check whether we want compact tables!
        #table_state.compact = attrib_is_true(table, "compact")
        
        #table_state.figure = False
        #table_state.fullwidth = False
        #table_state.sideways = False
        #if category == TableCategory.Figure:
        #    table_state.figure = True

        #elif category == TableCategory.Fullwidth:
        #    table_state.figure = True
        #    table_state.fullwidth = True

        #elif category == TableCategory.Sideways:
        #    table_state.figure = True
        #    table_state.fullwidth =  True
        #    table_state.sideways = True

        #elif category == TableCategory.Standard:
            # the default
        #    pass
        #else:
        #    raise Exception("Unknown table category: '%s'" % category)        
        
        # we need to work out in advance the table layout (e.g. |c|c|c|
        # or whatever).
        #table_spec = table.find("tablespec")
        #table_spec_str = ""
        #self._number_of_columns_in_table = 0
        #self._current_column_in_table = 0
        #self._current_row_in_table = 0

        # turn this on to draw vertical lines between columns
        #DEBUG_COLUMN_WIDTH = False

        #columns = 0
        #for child in table_spec.iterchildren():
        #    columns += 1

        #    if child.tag == "fixed":
        #        percent_width = float(child.text)
        #        table_spec_str += "p{%s\\hsize}" % percent_width
                
        #    elif child.tag is COMMENT:
        #       # ignore comments!
        #       pass

        #    else:
        #        raise Exception("Unknown table spec: %s" % child.tag)

        #    if DEBUG_COLUMN_WIDTH:
        #        table_spec_str += "|"
        #self._number_of_columns_in_table = columns

        # vertical space
        ##if table_state.compact:
        #self.latex_file.write("\n\\vspace{-0.3cm}")
        ##else:
        ##    self.latex_file.write("\n\\vspace{0.05cm}")

        # don't have paragraph indents buggering up our table layouts
        #self.latex_file.write("\\noindent{}")            

        # wrap single page tables in a table environment
        # (we use xtabular for multi-page tables and the table environment
        # confuses it about page size).        
        #if table_state.figure:
        #    if table_state.sideways:
        #        self.latex_file.write("\\begin{sidewaystable*}[htp]")
        #    elif table_state.fullwidth:
        #        self.latex_file.write("\\begin{table*}[ht]")
        #    else:
        #        self.latex_file.write("\\begin{table}")
        #else:
        #     self.latex_file.write("\\begin{table}[H]")
                
        # The table caption
        #table_title = table.find("tabletitle")        
        #if table_title is not None:
        #    if hasattr(table_title, "text"):
        #        table_title = table_title.text
        #    table_title = table_title.strip()
        #    self.latex_file.write(" \\captionof{table}{%s} " % table_title)
            
        # reduce the line spacing in compact tables
        #if table_state.compact:
        #    self.latex_file.write("\\begingroup\n")
        #    self.latex_file.write("\\renewcommand\\arraystretch{0.75}\n")
            
        #self.latex_file.write(" \\begin{center} ")

        # Tabular
        #if table_state.fullwidth:
        #    # normal table environment
        #    self.latex_file.write("\\begin{tabularx}{1.0\\textwidth}{%s} " 
        #                          % table_spec_str)
        #else:
        #    self.latex_file.write("\\begin{tabularx}{1.0\\linewidth}{%s}" 
        #                          % table_spec_str)

        # horizontal line
        #if table_state.figure:
        #    self.latex_file.write(r" \toprule{}\\")
        #else:
        #    self.latex_file.write(r" \hline ")            
        return


    def end_table(self, table):
        #global table_state

        # Check whether we want compact tables!
        #table_state.compact = attrib_is_true(table, "compact")
        
        #category = get_text_for_child(table, "tablecategory")
        #if category is None:
        #    raise Error("Table requires a tablecategory child element.")

        #figure = False
        #fullwidth = False
        #sideways = False
        #if category == TableCategory.Figure:
        #    figure = True

        #elif category == TableCategory.Fullwidth:
        #    figure = True
        #    fullwidth = True

        #elif category == TableCategory.Sideways:
        #    figure = True
        #    fullwidth =  True
        #    sideways = True

        #elif category == TableCategory.Standard:
        #    # the default
        #    pass

        #else:
        #    raise Exception("Unknown table category: '%s'" % category)
                
        #if figure:
        #    self.latex_file.write("\\bottomrule ")
        #else:
        #    self.latex_file.write(r" \hline ")

        # normal table environment
        #self.latex_file.write("\\end{tabularx}")
                
        #self.latex_file.write(" \\end{center}")

        #if table_state.compact:
        #    self.latex_file.write("\\vspace{0.14cm}")
        #    self.latex_file.write("\\endgroup{}\n")

        #for index, index_subentry in table_state.index_entries:
        #    self.write_index(index, index_subentry)

        #if table_state.figure:
        #    if table_state.sideways:
        #        self.latex_file.write("\\end{sidewaystable*}")        
        #    elif table_state.fullwidth:
        #        self.latex_file.write("\\end{table*}")        
        #    else:
        #        self.latex_file.write("\\end{table}")
        #        # vertical space
        #        self.latex_file.write("\n\\\\\n")
        #else:
        #    self.latex_file.write("\\end{table}")
                    
        #self.latex_file.write("\n\n")
        #table_state = None
        return

    # tablespec and it's children are parsed by the table element (it's special)
    start_tablecategory = no_op
    end_tablecategory = no_op
    start_tablespec = no_op
    end_tablespec = no_op
    start_fixed = no_op
    end_fixed = no_op
    start_tabletitle = no_op
    end_tabletitle = no_op

    # Tablelabel is also parsed by the table
    def start_tablelabel(self, label):
        #global table_state
        #table_state.label = label.text.strip()
        return
    end_tablelabel = no_op

    def start_tablesection(self, tablesection):
        #self.latex_file.write("\\rpgtablesection{%s}" % tablesection.text.strip())
        return
    end_tablesection = no_op


    def start_tablerow(self, table_row):
        # we can turn off new colours on the next row 
        # (and keep the same colour as the previous row).
        #if "newcolour" in table_row.attrib:
        #    new_colour_attr = table_row.get("newcolour")
        #    new_colour = convert_str_to_bool(new_colour_attr)
        #else:
        #    new_colour = True

        #if new_colour:
        #    self._current_row_in_table += 1

        #if table_row.tag == "tableheaderrow":
        #    self.latex_file.write("\\rowcolor{blue!33}\n")
        #elif (self._current_row_in_table + 1) % 2 == 1:                
        #    self.latex_file.write("\\rowcolor{blue!20}\n")
        return

    def end_tablerow(self, tablerow):
        #self.latex_file.write("\\tabularnewline ")
        return

    start_tableheaderrow = start_tablerow
    end_tableheaderrow = end_tablerow

    def start_td(self, table_data):
        """
        Start table data.

        """
        # width = table_data.get("width")
        # if width is not None:            
        #     width = int(width)
        # else: 
        #     width = 1

        # align = table_data.get("align")
        # if align is None:
        #     align = "l"

        # self._current_column_in_table = (
        #     (self._current_column_in_table + width) % self._number_of_columns_in_table)

        # # override for table headers
        # parent = table_data.getparent()
        # if parent.tag == "tableheaderrow":
        #     text = "\\begin{rpgtableheader}"

        # if width > 1 or align != "l":
        #    self.latex_file.write("\\multicolumn{%s}{%s}{" % (width, align))
        return

    def end_td(self, table_data):
        # width = table_data.get("width")
        # if width is not None:
        #     width = int(width)
        # else: 
        #     width = 1
            
        # align = table_data.get("align")
        # if align is None:
        #     align = "l"
        
        # parent = table_data.getparent()
        # if parent.tag == "tableheaderrow":
        #     text = "\\end{rpgtableheader}"

        # if width > 1 or align != "l":
        #     # multicolumn table data
        #     self.latex_file.write("}")

        # if self._current_column_in_table != 0:
        #     self.latex_file.write(" & ")                
        return    

    # table headers are a type of table data
    start_th = start_td
    end_th = end_td

    def start_tableofcontents(self, table_of_contents):
        #self.latex_file.write("\\tableofcontents\n")
        return
    end_tableofcontents = no_op

    def start_listoffigures(self, list_of_figures):
        # self.latex_file.write(
        #     "\\begin{minipage}[t]{1\\textwidth}\\listoffigures\\end{minipage}")
        return
    end_listoffigures = no_op

    def start_listofart(self, list_of_art):
        #self.latex_file.write(# "\\listofart\n")
        #"\\begin{minipage}[b]{1\\textwidth}\\listofart\\end{minipage}")
        return
    end_listofart = no_op

    def start_list_of_tables(self, list_of_tables):
        #self.latex_file.write("\\listoftables\n")
        return

    def end_list_of_tables(self, list_of_tables):
        return

    def start_combat_symbol(self, combat_symbol):
        #self.latex_file.write("\\rpgcombatsymbol{}")
        return
    end_combat_symbol = no_op

    def start_recommendedabilitylevelsymbol(self, recommended_ability_level_symbol):
        #self.latex_file.write("\\rpgrecommendedabilitylevelsymbol{}")
        return
    end_recommendedabilitylevelsymbol = no_op

    def start_training_symbol(self, training_symbol):
        #self.latex_file.write("\\rpgtrainingsymbol{}")
        return
    end_training_symbol = no_op

    def start_learning_symbol(self, learning_symbol):
        #self.latex_file.write("\\rpglearningsymbol{}")
        return
    end_learning_symbol = no_op

    def start_label(self, label):
        #self.latex_file.write("\n\\label{")
        return
    def end_label(self, label):
        #self.latex_file.write("}")
        return

    def start_fourcolumns(self, threecolumns):
        #self.latex_file.write("\\onecolumn\\begin{multicols}{4}\n")
        return

    def end_fourcolumns(self, ability_group):
        #self.latex_file.write("\\end{multicols}\\twocolumn\n")
        return
    
    def start_attempt(self, success):
        #self.latex_file.write("\\rpgattempt{}")
        return
    end_attempt = no_op

    def start_success(self, success):
        #self.latex_file.write("\\rpgsuccess{}")
        return
    end_success = no_op

    def start_fail(self, fail):
        #self.latex_file.write("\\rpgfail{}")
        return
    end_fail = no_op

    def start_eg(self, fail):
        #self.latex_file.write("e.g.\@{}")
        return
    end_eg = no_op

    def start_ie(self, fail):
        #self.latex_file.write("i.e.\@{}")
        return
    end_ie = no_op

    def start_etc(self, fail):
        #self.latex_file.write("etc.\@{}")
        return
    end_etc = no_op

    def start_notapplicable(self, fail):
        #self.latex_file.write("ⁿ/ₐ")
        return
    end_notapplicable = no_op

    def start_dpool(self, fail):
        #self.latex_file.write("\\dpool{}")
        return
    end_dpool = no_op


    def start_vspace(self, vspace):
        # if vspace.text is None:
        #     drop = 1
        # else:
        #     drop = convert_str_to_int(vspace.text)
        # self.latex_file.write("\\vspace{%s\drop}\n" % drop)
        return

    def end_vspace(self, vspace):
        return

    #
    #
    #               
    def bold_begin(self):
        #self.latex_file.write("\\textbf{")
        return
    
    def bold_finish(self):
        #self.latex_file.write("s} ")
        return

    def newline(self):
        #self.latex_file.write("\\newline\n")
        return

    #
    # Monster blocks.
    #
    def start_monsterblock(self, monsterblock):
        #self.latex_file.write(r"\begin{minipage}{\linewidth}")
        return

    def end_monsterblock(self, monsterblock):
        #self.latex_file.write(r"\end{minipage}")
        return

    def start_mbtitle(self, mbtitle):
        #self.latex_file.write(r"\mbsep{}\begin{mbtitle}")
        return

    def end_mbtitle(self, mbtitle):
        #self.latex_file.write(r"\end{mbtitle}\noindent{}")
        return
    
    def start_mbtags(self, mbtags):
        #self.latex_file.write(r"\begin{mbtags}")
        return

    def end_mbtags(self, mbtags):
        #self.latex_file.write(r"\end{mbtags}\noindent")
        return

    def start_mbac(self, mbac):
        #self.latex_file.write(r"\textbf{AC: }\begin{mbac}")
        return

    def end_mbac(self, mbac):
        #self.latex_file.write(r"\end{mbac}\enspace{}")
        return

    def start_mbhp(self, mbhp):
        #self.latex_file.write(r"\textbf{HP: }\begin{mbhp}")
        return
    
    def end_mbhp(self, mbhp):
        #self.latex_file.write("\\end{mbhp}")
        return

    def start_mbmove(self, mbmove):
        #self.latex_file.write(r"\textbf{Move: }\begin{mbmove}")
        return

    def end_mbmove(self, mbmove):
        #self.latex_file.write("\\end{mbmove}")
        return

    def start_mbinitiativebonus(self, mbresolve):
        #self.latex_file.write(r"\textbf{Initiative Bonus: }\begin{mbinitiativebonus}")
        return
    def end_mbinitiativebonus(self, mbresolve):
        #self.latex_file.write("\\end{mbinitiativebonus}\\vspace{0.1cm}\\break{}")
        return
    
    def start_mbmagic(self, mbmagic):
        #self.latex_file.write(r"\textbf{Magic Pool: }\begin{mbmagic}")
        return
    def end_mbmagic(self, mbmagic):
        #self.latex_file.write("\\end{mbmagic}\\vspace{0.1cm}\\break{}")
        return
    
    def start_mbmettle(self, mbmettle):
        #self.latex_file.write(r"\textbf{Resolve Pool: }\begin{mbmettle}")
        return
    def end_mbmettle(self, mbresolve):
        #self.latex_file.write("\\end{mbmettle}")
        return
    
    def start_mbstr(self, mbstr):
        # self.latex_file.write(
        #     "% attribute block\n" 
        #     "\\begin{tabular}{@{}ccccccc@{}}%\n"
        #     "\\mbattrtitleformat{STR} & %\n"
        #     "\\mbattrtitleformat{END} & %\n"
        #     "\\mbattrtitleformat{AG} & %\n"
        #     "\\mbattrtitleformat{SPD} & %\n"
        #     "\\mbattrtitleformat{LUCK} & %\n"
        #     "\\mbattrtitleformat{WIL} & %\n"
        #     "\\mbattrtitleformat{PER}\\\\%\n"
        #     "\\begin{small}")
        return
    def end_mbstr(self, mbstr):
        #self.latex_file.write("\\end{small} & %\n")
        return

    def start_mbend(self, mbend):
        #self.latex_file.write("\\begin{small}")
        return
    def end_mbend(self, mbend):
        #self.latex_file.write("\\end{small} & %\n")
        return

    def start_mbag(self, mbag):
        #self.latex_file.write("\\begin{small}")
        return
    def end_mbag(self, mbag):
        #self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbspd(self, mbspd):
        #self.latex_file.write("\\begin{small}")
        return
    def end_mbspd(self, mbspd):
        #self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbluck(self, mbluck):
        #self.latex_file.write("\\begin{small}")
        return
    def end_mbluck(self, mbluck):
        #self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbwil(self, mbwil):
        #self.latex_file.write("\\begin{small}")
        return
    def end_mbwil(self, mbwil):
        #self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbper(self, mbper):
        #self.latex_file.write("\\begin{small}")
        return
    def end_mbper(self, mbper):
        #self.latex_file.write("\\end{small}"
        #                      "\\end{tabular}"
        #                      "\n")
        return
    
    def start_mbabilities(self, mbabilities):
        #self.latex_file.write(r"\textbf{Abilities}: ")
        return
    def end_mbabilities(self, mbabilities):
        #self.latex_file.write("\n")
        return

    def start_mbaspects(self, mbaspects):
        #self.latex_file.write(r"\textbf{Aspects:} ")
        return
    def end_mbaspects(self, mbaspects):
        #self.latex_file.write("\\\\\n")
        return
    
    def start_mbdescription(self, mbdescription):
        # self.latex_file.write(r"\vspace{1.0mm}"
        #                       r"\textbf{Description:}"
        #                       r"\hfill"
        #                       r"\break"
        #                       r"\vspace{-0.3cm}")
        return
    def end_mbdescription(self, mbdescription):
        #self.latex_file.write("\n")
        return
    
    def start_mbnpc(self, mbnpc):
        return
    def end_mbnpc(self, mbnpc):
        #self.latex_file.write("\\newline{}")
        return

    def start_npcname(self, npcname):
        #self.latex_file.write(r"\textbf{Name: }\begin{npcname}")
        return
    def end_npcname(self, npcname):
        #self.latex_file.write("\\end{npcname} ")
        return
    
    def start_npchps(self, npchps):
        #self.latex_file.write(r"\textbf{HPs: }\begin{npchp}")
        return
    def end_npchps(self, npchps):
        #self.latex_file.write("\\end{npchp}")
        return

    def start_inspiration(self, inspiration):
        # img = inspiration.getparent()
        # if "id" in img.attrib:
        #     resource_id = img.get("id")
        #     resource = self.db.licenses.find(resource_id)
        #     sig = resource.get_sig()
            
        #     self.latex_file.write(r"{\attributionfont %s}" % sig)
        # else:
        #     raise Exception("Image inspiration missing id!")        
        return
    end_inspiration = no_op

    def start_attribution(self, attribution):
        # img = attribution.getparent()
        # if "id" in img.attrib:
        #     resource_id = img.get("id")
        #     resource = self.db.licenses.find(resource_id)
        #     sig = resource.get_sig()
            
        #     self.latex_file.write(r"{\attributionfont %s}" % sig)
        # else:
        #     raise Exception("Image attribution missing id!")
        return
    end_attribution = no_op

    def start_ellipsis(self, ellipsis):
        #self.latex_file.write("\ldots")
        return
    end_ellipsis = no_op
        


    def start_abilityref(self, ability_ref):

        try:
            ability_id = ability_ref.attrib["id"]
            ab = self.db.lookup_ability_or_ability_rank(ability_id)

            # if isinstance(ab, abilities.AbilityRank):
            #     name = ab.get_ability().get_title()
                
            # elif isinstance(ab, abilities.Ability):
            #     name = ab.get_title()

            # else:
            #     raise Exception(f"Bad abilityref!!  No ability has id: {ability_id}")


            # rank_num = ab.get_rank_number()
            # if rank_num is not None:
            #     rank_num = convert_to_roman_numerals(rank_num)
                
            # if ab.is_innate():
            #     if rank_num is None:
            #         self.latex_file.write(f"{name}^i")
            #     else:
            #         self.latex_file.write(f"{name}^i {rank_num}")
            # else:
            #     if rank_num is None:
            #         self.latex_file.write(f"{name} {rank_num}")
            #     else:
            #         self.latex_file.write(f"{name}")
            
        except KeyError:
            # bad ability ref...
            raise Exception("Bad abilityref!!  Missing ability id.")
        
            
        
        return    
    def end_abilityref(self, _):
        return    
    
    
