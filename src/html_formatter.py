# -*- coding: utf-8 -*-
from os.path import join, splitext
import config
from utils import (
    normalize_ws,
    convert_str_to_bool,
    convert_str_to_int,
    COMMENT# ,
    #resources_dir
)
from config import use_imperial



html_frontmatter = r"""<!DOCTYPE html>
<html lang="en">
  <head>

    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="Malleus Deum.. The open, free pen & paper, fantasy RPG.">
    <meta name="author" content="Blaize Rhodes">
    <link rel="icon" href="favicon.png">

    <title>Malleus Deum!</title>


    <link href="https://fonts.googleapis.com/css?family=Uncial+Antiqua" rel="stylesheet">
    <!--
    <link href="https://fonts.googleapis.com/css?family=UnifrakturCook:700" rel="stylesheet">
    -->
    
    <!-- Bootstrap CSS -->
    <link
       rel="stylesheet"
       href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css"
       integrity="sha384-rwoIResjU2yc3z8GV/NPeZWAv56rSmLldC3R/AZzGRnGxQQKnKkoFVhFQhNUwEyJ"
       crossorigin="anonymous">

    <!-- Custom styles for this template -->
    <link href="malleus_deum.css" rel="stylesheet">    
  </head>
  <body>

"""


html_endmatter = r"""

    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script
       src="https://code.jquery.com/jquery-3.1.1.slim.min.js"
       integrity="sha384-A7FZj7v+d/sdmMqp/nOQwliLvUsJfDHW+k9Omg/a/EheAdgtzNs3hpfag6Ed950n"
       crossorigin="anonymous">
    </script>
    <script
       src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.0/js/tether.min.js"
       integrity="sha384-DztdAPBWPRXSA/3eYEEUWrWCy7G5KFbe8fFjk5JAIxUYHKkDx6Qin1DkWx51bBrb"
       crossorigin="anonymous">
    </script>
    <script
       src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/js/bootstrap.min.js"
       integrity="sha384-vBWWzlZJ8ea9aCX4pEW3rVHjgjt7zpkNpZk+02D9phzyeVkE+jo0ieGizqPLForn"
       crossorigin="anonymous">
    </script>

      
    <script src="../../dist/js/bootstrap.min.js"></script>
    <!-- Just to make our placeholder images work. Don't actually copy the next line! -->
    <script src="../../assets/js/vendor/holder.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="../../assets/js/ie10-viewport-bug-workaround.js"></script>
  </body>
</html>
"""

def get_text_for_child(element, child_name):
    """
    Find text for a child element.

    """
    child = element.find(child_name)
    if child is None or child.text is None:
        text = ""
    else:
        text = child.text.strip()
    return text


class TableCategory:
    Standard = "Standard"
    Figure = "Figure"
    Fullwidth = "FullWidth"
    Sideways = "Sideways"    


class HtmlFormatter:
    
    def __init__(self, html_file):

        # open html file pointer
        self.html_file = html_file
        
        # internal state
        self._drop_capped_first_letter_of_chapter = False

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
        self.index_entry_see = None
        self.index_entry_subentry = None

        #
        # configuration
        #        
        return

    def verify(self):
        verifyObject(IFormatter, self)
        return

    def no_op(self, obj):
        """We've got a lot of handlers that don't need to do anything.. do nothing once."""
        pass

    
    def start_book(self, book):
        
        # must be a valid html paper size
        # if config.paper_size == "a4":
        #     paper_size = "a4paper"
        # elif config.paper_size == "letter":
        #     paper_size = "letterpaper"
        # else:
        #     raise Exception("Unknown paper size.  Pick one of [a4, letter] in config.py")

        # orientation = ""
        # if "landscape" in book.attrib:
        #     landscape = book.get("landscape").lower()
        #     if landscape == "true":
        #         formatting = ",landscape"

        # formatting = paper_size + orientation
        # #print html_frontmatter
        # #print html_frontmatter % formatting
        # #self.html_file.write(html_frontmatter % formatting)
        self.html_file.write(html_frontmatter)

        # if config.display_page_background:
        #     self.html_file.write(
        #         "\n"
        #         "% use a background image\n"
        #         "\\CenterWallPaper{1.0}{./resources/paper_" + paper_size + ".jpg}"
        #         "\n\n")
        return

    def end_book(self, book):
        #self.html_file.write("\\end{document}\n")
        self.html_file.write(html_endmatter)        
        return


    def start_appendix(self, appendix):
        self.html_file.write("\\appendix\n"
                              "\\addcontentsline{toc}{chapter}{APPENDICES}\n")
        return
    end_appendix = no_op

    def start_fightreach(self, symbol):
        self.html_file.write("\\fightreachsymbol{}")
        return
    end_fightreach = no_op    

    def start_start(self, symbol):
        self.html_file.write("\\startsymbol{}")
        return
    end_start = no_op    
    
    def start_fast(self, symbol):
        self.html_file.write("\\fastsymbol{}")
        return
    end_fast = no_op
    
    def start_medium(self, symbol):
        self.html_file.write("\\mediumsymbol{}")
        return
    end_medium = no_op
    
    def start_mediumorslow(self, symbol):
        self.html_file.write("\\mediumorslowsymbol{}")
        return
    end_mediumorslow = no_op
    
    def start_startandreaction(self, symbol):
        self.html_file.write("\\startandreactionsymbol{}")
        return
    end_startandreaction = no_op
    
    def start_slow(self, symbol):
        self.html_file.write("\\slowsymbol{}")
        return
    end_slow = no_op
    
    def start_noncombat(self, symbol):
        self.html_file.write("\\noncombatsymbol{}")
        return
    end_noncombat = no_op    

    def start_newpage(self, symbol):
        self.html_file.write("\\newpage[4]\n")
        return
    end_newpage = no_op    

    def start_resolution(self, symbol):
        self.html_file.write("\\resolutionsymbol{}")
        return
    end_resolution = no_op
    
    def start_talk(self, symbol):
        self.html_file.write("\\talksymbol{}")
        return
    end_talk = no_op
    
    def start_act(self, symbol):
        self.html_file.write("\\actsymbol{}")
        return
    end_act = no_op

    def start_ambush(self, symbol):
        self.html_file.write("\\ambushsymbol{}")
        return
    end_ambush = no_op
    
    def start_surprise(self, symbol):
        self.html_file.write("\\surprisesymbol{}")
        return
    end_surprise = no_op
    
    def start_initiative(self, symbol):
        self.html_file.write("\\initiativesymbol{}")
        return
    end_initiative = no_op

    def start_reaction(self, symbol):
        self.html_file.write("\\reactionsymbol{}")
        return
    end_reaction = no_op

    
    
    # def get_html_symbols(self, title):
    #     tex = ""
    #     for symbol in ("ambushsymbol",
    #                    "surprisesymbol",
    #                    "initiativesymbol",
    #                    "talksymbol",
    #                    "fightreachsymbol",
    #                    "startsymbol",
    #                    "fastsymbol",
    #                    "mediumsymbol",
    #                    "slowsymbol",
    #                    "mediumorslowsymbol",
    #                    "startandreactionsymbol",
    #                    "resolutionsymbol",
    #                    "reactionsymbol",
    #                    "noncombatsymbol"):
    #         symbol_node = title.find(symbol)
    #         if symbol_node is not None:
    #             tex += " \\%s{}" % symbol
    #         #else:
    #         #    raise Exception("UNKNOWN SYMBOL: %s" % symbol)
    #     return tex               
    
    # def start_subsubsection(self, subsubsection):
    #     tex = ""
    #     anonymous = subsubsection.get("anonymous")
    #     if anonymous is not None and anonymous.lower() == "true":
    #         tex = "\\subsubsection*{"
    #     else:
    #         tex = "\\subsubsection{"

    #     title = subsubsection.find("subsubsectiontitle")
    #     if title is not None:
    #         tex += title.text.strip()        
    #     tex += self.get_html_symbols(title)
        
    #     self.html_file.write(tex) 
    #     self.html_file.write("}\n") 
    #     return
    # end_subsubsection = no_op
        
    start_ability_title = no_op
    end_ability_title = no_op

    def start_ability_id(self, ability_id):        
        self.html_file.write("ID: %s\\\n" % ability_id) 
        return
    end_ability_id = no_op

    start_ability_group = no_op
    def end_ability_group(self, ability_group):
        self.html_file.write("%s\n" % normalize_ws(ability_group.text))
        return

    start_ability_class = no_op
    def end_ability_class(self, ability_class):
        self.html_file.write("%s\n" % normalize_ws(ability_class.text))
        return

    start_action_points = no_op
    def end_action_points(self, action_points):
        self.html_file.write("%s\n" % normalize_ws(action_points.text))
        return

    def start_and(self, and_element):
        self.html_file.write("\\&")
        return
    end_and = no_op


    def start_lore(self, element):
        self.html_file.write("\\lore{}")
        return    
    end_lore = no_op

    def start_martial(self, element):
        self.html_file.write("\\martial{}")
        return    
    end_martial = no_op

    def start_general(self, element):
        self.html_file.write("\\general{}")
        return    
    end_general = no_op

    def start_magical(self, element):
        self.html_file.write("\\magical{}")
        return    
    end_magical = no_op

    def start_geqqsymbol(self, geqq_element):
        self.html_file.write("$\stackrel{\scriptscriptstyle ?}{\geq}{}$")
        return
    end_geqqsymbol = no_op

    def start_leqqsymbol(self, geqq_element):
        self.html_file.write("$\stackrel{\scriptscriptstyle ?}{\leq}{}$")
        return
    end_leqqsymbol = no_op

    def start_newline(self, newline):
        self.html_file.write("\\newline\n")
        return
    end_newline = no_op

    start_pageref = no_op
    def end_pageref(self, pageref):
        self.html_file.write("~\\pageref{%s}" % normalize_ws(pageref.text))
        return

    start_ref = no_op
    def end_ref(self, ref):
        self.html_file.write("~\\ref{%s}" % normalize_ws(ref.text))
        return

    def start_index(self, index):
        self.html_file.write("\\clearpage\n")               
        self.html_file.write("\\addcontentsline{toc}{chapter}{Index}\n")               
        self.html_file.write("\\printindex\n")
        return
    end_index = no_op

    
    # def start_section(self, section):
    #     title_element = section.find("sectiontitle")
    #     if title_element is None:
    #         title = ""
    #     else:
    #         title = title_element.text

    #     return
    start_section = no_op
    end_section = no_op

    #def start_sectiontitle(self, sectiontitle):
    #    self.html_file.write("\\section{%s}\n" % title)                       
    # start_sectiontitle = no_op
    # end_sectiontitle = no_op

    def start_sectiontitle(self, section_title):
        self.html_file.write("<h2>")                       
        return

    def end_sectiontitle(self, section_title):
        self.html_file.write("</h2>")                       
        return
    

    # def start_subsection(self, subsection):
    #     tex = ""
    #     anonymous = subsection.get("anonymous")
    #     if anonymous is not None and anonymous.lower() == "true":
    #         tex = "\\subsection{"
    #     else:
    #         tex = "\\subsection{"

    #     title = subsection.find("subsectiontitle")
    #     if title is not None:
    #         tex += title.text.strip()
    #         tex += self.get_html_symbols(title)

    #     tex += "}\n"
    #     self.html_file.write(tex) 
    #     return
    start_subsection = no_op
    end_subsection = no_op

    def start_subsectiontitle(self, section_title):
        self.html_file.write("<h3>")                       
        return

    def end_subsectiontitle(self, section_title):
        self.html_file.write("</h3>")                       
        return
    # start_subsectiontitle = no_op
    # end_subsectiontitle = no_op

    start_subsubsection = no_op
    end_subsubsection = no_op
    
    def start_subsubsectiontitle(self, section_title):
        self.html_file.write("<h4>")                       
        return

    def end_subsubsectiontitle(self, section_title):
        self.html_file.write("</h4>")                       
        return

    def start_playexample(self, playexample):
        self.html_file.write("\\begin{playexample}\n")
        return

    def end_playexample(self, playexample):
        self.html_file.write(playexample.text)                
        self.html_file.write("\\end{playexample}\n")        
        return
        
    def start_level(self, level):
        self._current_row_in_level_table += 1
        if self._current_row_in_level_table % 2 == 1:            
            self.html_file.write("\\rowcolor{blue!20} \n")
        else:
            self.html_file.write("\\rowcolor{white!20} \n")
        return
    
    def end_level(self, level):
        self.html_file.write(" \\\\\n")
        return        
        
    def start_level_xp(self, element):
        self.html_file.write(" %s &" % element.text)
        return    
    end_level_xp = no_op
    
    def start_level_number(self, element):
        self.html_file.write(" %s &" % element.text)
        return    
    end_level_number = no_op

    def start_level_combat(self, element):
        self.html_file.write("\\rpgcombatsymbol %s " % element.text)
        return    
    end_level_combat = no_op

    def start_level_training(self, element):
        self.html_file.write("\\rpgtrainingsymbol %s " % element.text)
        return    
    end_level_training = no_op

    def start_level_learning(self, element):
        self.html_file.write("\\rpglearningsymbol %s " % element.text)
        return    
    end_level_learning = no_op
    
    def start_level_description(self, element):
        self.html_file.write(" %s " % element.text)
        return

    def end_level_description(self, element):
        pass

    def start_titlepage(self, chapter):
        self.html_file.write("<h1>")
        return

    def end_titlepage(self, chapter):
        self.html_file.write("</h1>")
        return

    def start_emph(self, emph):
        return

    def end_emph(self, emph):
        self.html_file.write("\\emph{%s}" % normalize_ws(emph.text))
        return

    def start_equation(self, equation):
        self._equation_first_line = True
        self.html_file.write("\\begin{tabbing}\n "
                              "\\hspace*{0.5cm}\= \kill \\nopagebreak \n")    
        return

    def end_equation(self, equation):
        self.html_file.write("\\end{tabbing}\n ")
        return


    def start_line(self, line):
        """
        Start equation line.
        
        """
        if not self._equation_first_line:
            self.html_file.write("\\> ") 
        self._equation_first_line = False
        if line.text:
            self.html_file.write(" %s " % normalize_ws(line.text))
        return

    def end_line(self, line):
        self.html_file.write("\\\\\n ")
        return


    def start_bold(self, bold):
        self.html_file.write("\\textbf{%s} " % normalize_ws(bold.text))
        return
    end_bold = no_op

    def start_smaller(self, smaller):
        self.html_file.write("\\scriptsize{%s} " % normalize_ws(smaller.text))
        return
    end_smaller = no_op

    def handle_text(self, text):
        if text is not None:
            if isinstance(text, unicode):                           
                #self.html_file.write(text.encode('utf8'))
                self.html_file.write(text)
            else:
                self.html_file.write(text)
        return

    start_indexentry = no_op
    def end_indexentry(self, index_entry):
        if self.index_entry_see is not None:
            self.html_file.write("\\index{%s|see {%s}}" % (
                normalize_ws(index_entry.text), self.index_entry_see))
            self.index_entry_see = None

        elif self.index_entry_subentry is not None:
            self.html_file.write("\\index{%s!%s}" % (
                normalize_ws(index_entry.text), self.index_entry_subentry))
            self.index_entry_subentry = None
            
        else:
            self.html_file.write("\\index{%s}" % normalize_ws(index_entry.text))
        return

    # see element in index entry
    start_see = no_op
    def end_see(self, index_entry):
        self.index_entry_see = normalize_ws(index_entry.text)
        return

    # see element in index entry
    start_subentry = no_op
    def end_subentry(self, index_subentry):
        self.index_entry_subentry = normalize_ws(index_subentry.text)
        return

    def start_defn(self, defn):
        # self.html_file.write(" \\textbf{%s}\\index{%s}" % (normalize_ws(defn.text),
        #                                                     normalize_ws(defn.text)))
        self.html_file.write(" \\textbf{%s}" % (normalize_ws(defn.text)))
        return
    end_defn = no_op


    def start_measurement(self, distance):
        if use_imperial:
            distance_text = get_text_for_child(distance, "imperial")
            if distance_text is None:
                raise Exception("Imperial distance not specified!")

        else:
            distance_text = get_text_for_child(distance, "metric")
            if distance_text is None:
                raise Exception("Metric distance not specified!")

        self.html_file.write(normalize_ws(distance_text).strip())
        return
    end_measurement = no_op

    start_metric = no_op
    end_metric = no_op
    start_imperial = no_op
    end_imperial = no_op    
    
    # def start_chapter(self, chapter):
    #     title_element = chapter.find("chaptertitle")
    #     if title_element is None:
    #         title = ""
    #     else:
    #         title = title_element.text
    #     self.html_file.write("\\chapter{%s}\n" % title)
    #     return

    # def end_chapter(self, chapter):
    #     # remember to drop cap the first letter of the word in this chapter
    #     self._drop_capped_first_letter_of_chapter = False
    #     return
    start_chapter = no_op
    end_chapter = no_op

    def start_chaptertitle(self, chapter_title):
        self.html_file.write("<h1>")                       
        return

    def end_chaptertitle(self, chapter_title):
        self.html_file.write("</h1>")                       
        return    

    def start_p(self, paragraph):
        """
        Start paragraph.

        """
        self.html_file.write("\n")

        # turn of paragraph indentation?
        # if "noindent" in paragraph.attrib:
        #     no_indent = paragraph.get("noindent").lower()
        #     if no_indent == "true":
        #         self.html_file.write("\\noindent ")
                
        # add drop caps to the first word of every chapter
        if not self._drop_capped_first_letter_of_chapter:
            self._drop_capped_first_letter_of_chapter = True
            # words = paragraph.text.split()
            # if len(words) > 0:
            #     first_word = words[0]
            #     if len(first_word) > 0:
            #         first_letter = first_word[0]
            #         other_letters = first_word[1:]

            #         drop_cap_word = ("\\lettrine["
            #                          "lines=2, "
            #                          "lraise=0.1, "
            #                          # horizontal displacement of the indented text
            #                          "findent=-0.14em, " 
            #                          "nindent=0.3em, "
            #                          "slope=0em]{\\rpgdropcapfont %s}{%s}" %
            #                          (first_letter, other_letters))

            #     words = [drop_cap_word, ] + words[1:]
            self.html_file.write('<p class="drop-cap">')

            #text = " ".join(words)
        else:
            #text = normalize_ws(paragraph.text)
            self.html_file.write('<p>')

        #self.html_file.write(text)        
        return

    def end_p(self, paragraph):
        self.html_file.write("</p>\n")
        return

    def start_design(self, design):
        if config.print_design_notes:
            self.html_file.write("\n\n")
            self.html_file.write(design.text)        
        return

    def end_design(self, design):
        self.html_file.write("\n\n")
        return


    def start_provenance(self, provenance):
        self.html_file.write("\n\n")        

        if config.print_provenence_notes:
            self.html_file.write("\\begin{center}")
            self.html_file.write("\\begin{minipage}[c]{0.9\linewidth}")
            self.html_file.write("\\rpgprovenancesymbol\\hspace{0.2em}") 
            self.html_file.write(provenance.text)        
        return

    def end_provenance(self, provenance):
        if config.print_provenence_notes:
            self.html_file.write("\\end{minipage}")        
            self.html_file.write("\\end{center}")
            self.html_file.write("\n\n")
        return


    def start_author(self, author):
        self.html_file.write("{\\LARGE \\rpgtitleauthorfont %s}\\\\" % author.text)        
        return

    def end_author(self, author):
        return

    def start_title(self, title):
        self.html_file.write("{ \\color{rpgtitlefontcolor} \\rpgtitlefont %s }\\\\\n"
                              % title.text)
        return

    def end_title(self, title):
        return

    def start_caption(self, caption):
        self.html_file.write("\\caption{%s}" % caption.text)
        return

    def end_caption(self, caption):
        return

    def start_subtitle(self, subtitle):        
        self.html_file.write("{\\large \\rpgtitlesubtitlefont  %s}\\\\\n" % subtitle.text)
        return

    def end_subtitle(self, title):
        return

    start_chaptertitle = no_op
    end_chaptertitle = no_op
    # def start_chaptertitle(self, chapter_title):
    #     return

    # def end_chapter_title(self, chapter_title):
    #     return



    def start_img(self, img):
        if config.draw_imgs:
            if config.debug_outline_images:
                self.html_file.write("\\fbox{")

            self.html_file.write("\t\\begin{center}\n")

            filename = img.get("src")
            #_, ext = splitext(filename)
            #if ext.lower() == ".svg":            
            #    self.html_file.write("\t\\includesvg{%s}\n"
            #                          % (#img.get("scale", default="1.0", ),
            #                              filename))
            #else:
            self.html_file.write("\t\\includegraphics[scale=%s]{%s}\n"
                                  % (img.get("scale", default="1.0"), filename))
        return

    def end_img(self, img):
        if img.text is not None:
            self.html_file.write("\t%s\n" % img.text)
        self.html_file.write("\t\\end{center}\n")
        if config.debug_outline_images:
            self.html_file.write("}")
        return

    def start_figure(self, figure):
        position = "ht"
        if "position" in figure.attrib:
            position = figure.get("position")

        fullwidth = False
        if "fullwidth" in figure.attrib:
            fullwidth = figure.get("fullwidth")

        if fullwidth:
            self.html_file.write("\\begin{figure*}[%s]\n" % position)
        else:
            self.html_file.write("\\begin{figure}[%s]\n" % position)
        self.html_file.write("\\centering\n")
        return

    def end_figure(self, figure):
        caption = figure.get("caption")
        if caption is not None:
            self.html_file.write("\\caption{%s}\n" % caption)        

        fullwidth = False
        if "fullwidth" in figure.attrib:
            fullwidth = figure.get("fullwidth")

        if fullwidth:
            self.html_file.write("\\end{figure*}\n")
        else:
            self.html_file.write("\\end{figure}\n")
        return

    def start_olist(self, enumeration):
        """
        Start enumeration, ordered list of things.

        """
        # the [i] gets us roman numerals in the enumeration
        self.html_file.write("\\begin{enumerate}[i.]\n")
        return

    def end_olist(self, enumeration):
        self.html_file.write("\\end{enumerate}\n")
        return

    # def start_descriptions(self, description_list):
    #     self.html_file.write("\\begin{description}\n")

    #     self.description_terms_on_their_own_line = False
    #     if "termonnewline" in description_list.attrib:
    #         self.description_terms_on_their_own_line = description_list.get("termonnewline")
    #     return

    # def end_descriptions(self, description_list):
    #     # note seeing weird artifacts in embedded html lists without the extra newline
    #     self.html_file.write("\\end{description}\n\n")
    #     return


    def start_descriptions(self, description_list):
        self.html_file.write("<dl>\n")

        #self.description_terms_on_their_own_line = False
        #if "termonnewline" in description_list.attrib:
        #    self.description_terms_on_their_own_line = description_list.get("termonnewline")
        return

    def end_descriptions(self, description_list):
        # note seeing weird artifacts in embedded html lists without the extra newline
        self.html_file.write("</dl>\n\n")
        return
    

    # def start_description(self, description):
    #     if description.text is not None:
    #         self.html_file.write("%s" % description.text)
    #     return

    # def end_description(self, list_item):
    #     return

    def start_description(self, description):
        #if description.text is not None:
        #    self.html_file.write("%s" % description.text)
        self.html_file.write("<dd>")
        return

    def end_description(self, list_item):
        self.html_file.write("</dd>")
        return

    def start_term(self, term):
        """
        A description term.

        """
        # if term.text is not None:
        #     assert not self.description_terms_on_their_own_line
        #     # if self.description_terms_on_their_own_line:
        #     #     self.html_file.write("\\item[%s] \hfill \n" % term.text)
        #     # else:
        #     #     self.html_file.write("\\item[%s]" % term.text)
        #     self.html_file.write("\\item[%s]" % term.text)
        self.html_file.write("<dt>")
        return
    def end_term(self, term):
        self.html_file.write("</dt>")
        return
    
    
    # def start_term(self, term):
    #     """
    #     A description term.

    #     """
    #     if term.text is not None:
    #         assert not self.description_terms_on_their_own_line
    #         # if self.description_terms_on_their_own_line:
    #         #     self.html_file.write("\\item[%s] \hfill \n" % term.text)
    #         # else:
    #         #     self.html_file.write("\\item[%s]" % term.text)
    #         self.html_file.write("\\item[%s]" % term.text)
    #     return
    # end_term = no_op


    def start_list(self, list_element):
        self.html_file.write("\\begin{itemize}\n")
        return

    def end_list(self, list_element):
        self.html_file.write("\\end{itemize}\n")
        return

    def start_li(self, list_item):
        """
        Start list item.

        """
        self.html_file.write("\\item ")
        
        if list_item.text is not None:
            self.html_file.write(normalize_ws(list_item.text))
        return
    end_li = no_op

    def start_comment(self, comment):
        return

    def end_comment(self, comment):
        return

    start_tablespec = no_op
    end_tablespec = no_op

    def start_table(self, table):

        #category = table.find("tablecategory")
        category = get_text_for_child(table, "tablecategory")
        if category is None:
            raise Error("Table requires a tablecategory child element.")
        
        figure = False
        fullwidth = False
        sideways = False
        if category == TableCategory.Figure:
            figure = True

        elif category == TableCategory.Fullwidth:
            figure = True
            fullwidth = True

        elif category == TableCategory.Sideways:
            figure = True
            fullwidth =  True
            sideways = True

        elif category == TableCategory.Standard:
            # the default
            pass
        else:
            raise Exception("Unknown table category: '%s'" % category)        

        # we need to work out in advance the table layout (e.g. |c|c|c| or whatever).
        table_spec = table.find("tablespec")
        table_spec_str = ""
        self._number_of_columns_in_table = 0
        self._current_column_in_table = 0
        self._current_row_in_table = 0


        # turn this on to draw vertical lines between columns
        DEBUG_COLUMN_WIDTH = False

        columns = 0
        for child in table_spec.iterchildren():
            columns += 1
            # if child.tag == "fit":
            #     table_spec_str += "p{\\widthof{%s}}" % child.text
            # elif child.tag == "expand":

            #     # complicated with calculations
            #     table_spec_str += "p{0.3\\linewidth}"

            # elif child.tag == "expand-center":
            #     table_spec_str += ">{\\centering \\arraybackslash}X"

            # el

            if child.tag == "fixed":
                percent_width = float(child.text)
                table_spec_str += "p{%s\\linewidth}" % percent_width
                
            elif child.tag is COMMENT:
               # ignore comments!
               pass

            else:
                raise Exception("Unknown table spec: %s" % child.tag)

            if DEBUG_COLUMN_WIDTH:
                table_spec_str += "|"
        self._number_of_columns_in_table = columns

        # Check whether we want compact tables!
        compact = False
        if "compact" in table.attrib:
            compact = table.get("compact").lower() == "true"        
        

        # don't have paragraph indents buggering up our table layouts
        if compact:
            self.html_file.write("\n\n\\vspace{0.15cm}\\noindent")
        else:
            self.html_file.write("\n\n\\vspace{0.2cm}\\noindent")


        # wrap single page tables in a table environment
        # (we use xtabular for multi-page tables and the table environment
        # confuses it about page size).        
        if figure:
            if sideways:
                self.html_file.write("\\begin{sidewaystable*}[htp]")                
            elif fullwidth:
                self.html_file.write("\\begin{table*}[ht]")
            else:
                self.html_file.write("\\begin{table}")
        else:
            self.html_file.write("\\captionsetup{type=figure}")

        #self.html_file.write("\\centering")

        # reduce the line spacing in compact tables
        if compact:
            self.html_file.write("\\begingroup\n")
            self.html_file.write("\\renewcommand\\arraystretch{0.75}\n")
        
        if fullwidth:
            # normal table environment
            self.html_file.write("\\begin{tabularx}{1.0\\textwidth}{%s} " 
                                  % table_spec_str)
        else:
            self.html_file.write("\\begin{tabularx}{1.0\\linewidth}{%s} " 
                                  % table_spec_str)

        if figure:
            self.html_file.write(" \\toprule ")

        return


    def end_table(self, table): # , use_xtabular = False):
            
        #category = table.find("tablecategory")
        category = get_text_for_child(table, "tablecategory")
        if category is None:
            raise Error("Table requires a tablecategory child element.")

        figure = False
        fullwidth = False
        sideways = False
        if category == TableCategory.Figure:
            figure = True

        elif category == TableCategory.Fullwidth:
            figure = True
            fullwidth = True

        elif category == TableCategory.Sideways:
            figure = True
            fullwidth =  True
            sideways = True

        elif category == TableCategory.Standard:
            # the default
            pass

        else:
            raise Exception("Unknown table category: '%s'" % category)
                
        if figure:
            self.html_file.write("\\bottomrule ")    

        # normal table environment
        self.html_file.write("\\end{tabularx}")
        

        compact = False
        if "compact" in table.attrib:
            compact = table.get("compact").lower() == "true"        
        if compact:
            self.html_file.write("\\endgroup\n")

        
        table_title = table.find("tabletitle")
        if table_title is not None and table_title.text.strip() != "":
            if figure:
                self.html_file.write("\\caption{%s}" % table_title.text)
            
            
        # we also need to find any labels! (place them after the caption!)
        label = table.find("tablelabel")
        if label is not None:
            self.start_label(label)
            self.end_label(label)
            
        if figure:
            if sideways:
                self.html_file.write("\\end{sidewaystable*}")        
            elif fullwidth:
                self.html_file.write("\\end{table*}")        
            else:
                self.html_file.write("\\end{table}")
            
        self.html_file.write("\n\n")
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

    # tablelabel is also parsed by the table
    start_tablelabel = no_op
    end_tablelabel = no_op

    def start_tablesection(self, tablesection):
        self.html_file.write("\\rpgtablesection{%s}" % tablesection.text.strip())
        return
    end_tablesection = no_op


    def start_tablerow(self, table_row):

        # we can turn off new colours on the next row 
        # (and keep the same colour as the previous row).
        if "newcolour" in table_row.attrib:
            new_colour_attr = table_row.get("newcolour")
            new_colour = convert_str_to_bool(new_colour_attr)
        else:
            new_colour = True

        if new_colour:
            self._current_row_in_table += 1

        if table_row.tag == "tableheader":
            self.html_file.write("\\rowcolor{blue!33}\n")
            assert False

        elif (self._current_row_in_table + 1) % 2 == 1:                
            self.html_file.write("\\rowcolor{blue!20} \n")
        return

    def end_tablerow(self, table_title):
        self.html_file.write(" \\tabularnewline ")
        return

    start_tableheaderrow = start_tablerow
    end_tableheaderrow = end_tablerow

    def start_td(self, table_data):
        """
        Start table data.

        """
        width = table_data.get("width")
        if width is not None:
            width = int(width)
        else: 
            width = 1

        align = table_data.get("align")
        if align is None:
            align = "l"

        self._current_column_in_table = (
            (self._current_column_in_table + width) % self._number_of_columns_in_table)

        if table_data.text is not None:
            text = normalize_ws(table_data.text).strip()

            # override for table headers
            parent = table_data.getparent()
            if parent.tag == "tableheaderrow":
                text = "\\rpgtableheader{%s}" % text

            if width > 1 or align != "l":
                # multicolumn table data
                assert align is not None

                self.html_file.write("\\multicolumn{%s}{%s}{%s" % (width, align, text))
            else:
                # normal table data
                self.html_file.write("%s" % text)
        return

    def end_td(self, table_data):
        width = table_data.get("width")
        align = table_data.get("align")
        if width is not None or align is not None:
            self.html_file.write("}")                        

        if self._current_column_in_table != 0:
            self.html_file.write(" & ")                
        return    

    # table headers are a type of table data
    start_th = start_td
    end_th = end_td


    def start_multicolumntd(self, table_data):
        """
        Start muilticolumn table data.

        """
        if "columns" in table_data.attrib:
            columns = int(table_data.get("columns"))

        if ((self._current_column_in_table + columns) > self._number_of_columns_in_table):
            raise Exception("Multicolumn table data overflows table!")

        self._current_column_in_table = (
            (self._current_column_in_table + columns) % self._number_of_columns_in_table)

        #if self._current_row_in_table == 0:
        #     self.html_file.write("\\rpgtableheader{%s} \n" %
        #                           table_data.text)
        #else:

        
        # self.html_file.write("\\multicolumn{%s}{c}{\\rpgtableheader{%s}}" % 
        #                        (columns, table_data.text))
        self.html_file.write("\\multicolumn{%s}{c}{\\rpgtableheader{%s" %
                              (columns, table_data.text))

        # if self._current_column_in_table != 0:
        #     self.html_file.write(" & ")                        
        # return
    #end_multicolumntd = no_op
    def end_multicolumntd(self, table_data):

        self.html_file.write("}}")
        
        if self._current_column_in_table != 0:
            self.html_file.write(" & ")
        return


    def start_tableofcontents(self, table_of_contents):
        self.html_file.write("\\tableofcontents\n")
        return

    def end_tableofcontents(self, table_of_contents):
        return

    def start_list_of_figures(self, list_of_figures):
        self.html_file.write("\\listoffigures\n")
        return

    def end_list_of_figures(self, list_of_figures):
        return

    def start_list_of_tables(self, list_of_tables):
        self.html_file.write("\\listoftables\n")
        return

    def end_list_of_tables(self, list_of_tables):
        return

    def start_combat_symbol(self, combat_symbol):
        self.html_file.write("\\rpgcombatsymbol{}")
        return
    end_combat_symbol = no_op

    def start_innateabilitylevelsymbol(self, innate_ability_symbol):
        self.html_file.write("\\rpginnateabilitysymbol{}")
        return
    end_innateabilitylevelsymbol = no_op

    def start_innatearchetypeabilitylevelsymbol(self, innate_ability_symbol):
        self.html_file.write("\\rpginnatearchetypeabilitysymbol{}")
        return
    end_innatearchetypeabilitylevelsymbol = no_op

    def start_recommendedabilitylevelsymbol(self, recommended_ability_level_symbol):
        self.html_file.write("\\rpgrecommendedabilitylevelsymbol{}")
        return
    end_recommendedabilitylevelsymbol = no_op

    def start_training_symbol(self, training_symbol):
        self.html_file.write("\\rpgtrainingsymbol{}")
        return
    end_training_symbol = no_op

    def start_learning_symbol(self, learning_symbol):
        self.html_file.write("\\rpglearningsymbol{}")
        return
    end_learning_symbol = no_op


    def start_label(self, label):
        self.html_file.write("\n\\label{%s} " % normalize_ws(label.text))
        return
    end_label = no_op


    def start_fourcolumns(self, threecolumns):
        self.html_file.write("\\onecolumn\\begin{multicols}{4}\n")
        return
    
    def end_fourcolumns(self, ability_group):
        self.html_file.write("\\end{multicols}\\twocolumn\n")
        return


    
    def start_attempt(self, success):
        self.html_file.write("\\rpgattempt{}")
        return
    end_attempt = no_op

    def start_success(self, success):
        self.html_file.write("\\rpgsuccess{}")
        return
    end_success = no_op

    def start_fail(self, fail):
        self.html_file.write("\\rpgfail{}")
        return
    end_fail = no_op

    def start_eg(self, fail):
        self.html_file.write("e.g.\@{}")
        return
    end_eg = no_op

    def start_ie(self, fail):
        self.html_file.write("i.e.\@{}")
        return
    end_ie = no_op

    def start_etc(self, fail):
        self.html_file.write("etc.\@{}")
        return
    end_etc = no_op

    def start_notapplicable(self, fail):
        self.html_file.write("ⁿ/ₐ")
        return
    end_notapplicable = no_op

    def start_d4(self, fail):
        self.html_file.write("\\dfour{}")
        return
    end_d4 = no_op

    def start_d6(self, fail):
        self.html_file.write("\\dsix{}")
        return
    end_d6 = no_op

    def start_d8(self, fail):
        self.html_file.write("\\deight{}")
        return
    end_d8 = no_op
    
    def start_d10(self, fail):
        self.html_file.write("\\dten{}")
        return
    end_d10 = no_op

    def start_d12(self, fail):
        self.html_file.write("\\dtwelve{}")
        return
    end_d12 = no_op

    def start_d20(self, fail):
        self.html_file.write("\\dtwenty{}")
        return
    end_d20 = no_op

    def start_dany(self, fail):
        self.html_file.write("\\dany{}")
        return
    end_dany = no_op

    def start_dpool(self, fail):
        self.html_file.write("\\dpool{}")
        return
    end_dpool = no_op


    def start_vspace(self, vspace):
        if vspace.text is None:
            drop = 1
        else:
            drop = convert_str_to_int(vspace.text)
        self.html_file.write("\\vspace{%s\drop}\n" % drop)
        return

    def end_vspace(self, vspace):
        return



    #
    # Monster blocks.
    #

    start_monsterblock = no_op
    end_monsterblock = no_op
    
    def start_mbtitle(self, mbtitle):
        self.html_file.write(r"\begin{mbtitle}")
        return

    def end_mbtitle(self, mbtitle):
        self.html_file.write(r"\end{mbtitle}"
                              r"\\"
                              "\n")
        return
    
    def start_mbtags(self, mbtags):
        self.html_file.write(r"\begin{mbtags}")
        return
    def end_mbtags(self, mbtags):
        self.html_file.write(r"\end{mbtags}"
                              r"\\"
                              r"\mbsep{}\\[-0.36cm]"
                              "\n")
        return

    def start_mbac(self, mbac):
        self.html_file.write(r"\textbf{AC:} \begin{mbac}")
        return
    def end_mbac(self, mbac):
        self.html_file.write(r"\end{mbac} ")
        return

    def start_mbhp(self, mbhp):
        self.html_file.write(r"\textbf{HP:} \begin{mbhp}")
        return
    
    def end_mbhp(self, mbho):
        self.html_file.write("\\end{mbhp} ")
        return

    def start_mbmove(self, mbmove):
        self.html_file.write(r"\textbf{Move:} \begin{mbmove}")
        return
    def end_mbmove(self, mbmove):
        self.html_file.write(r"\end{mbmove}"
                              r"\\[0.1cm]"
                              "\n")
        return


    def start_mbmagic(self, mbmagic):
        #self.latex_file.write(r"\textbf{Magic Pool: }\begin{mbmagic}")
        return
    def end_mbmagic(self, mbmagic):
        #self.latex_file.write("\\end{mbmagic}\\vspace{0.1cm}\\hfill\\break{}")
        return
    
    def start_mbresolve(self, mbresolve):
        #self.latex_file.write(r"\textbf{Resolve Pool: }\begin{mbresolve}")
        return
    def end_mbresolve(self, mbresolve):
        #self.latex_file.write("\\end{mbresolve}\\vspace{0.1cm}\\hfill\\break{}")
        return    

    def start_mbinitiativebonus(self, mbresolve):
        #self.latex_file.write(r"\textbf{Initiative Bonus: }\begin{mbresolve}")
        return
    def end_mbinitiativebonus(self, mbresolve):
        #self.latex_file.write("\\end{mbresolve}\\vspace{0.1cm}\\hfill\\break{}")        
        return
    
    def start_mbstr(self, mbstr):
        self.html_file.write(
            "% attribute block\n" 
            #"\\begin{tabular}{ccccccc@{}}%\n"
            "\\begin{tabular}{@{}ccccccc@{}}%\n"
            "\\mbattrtitleformat{STR} & %\n"
            "\\mbattrtitleformat{END} & %\n"
            "\\mbattrtitleformat{AG} & %\n"
            "\\mbattrtitleformat{SPD} & %\n"
            "\\mbattrtitleformat{LUCK} & %\n"
            "\\mbattrtitleformat{WIL} & %\n"
            "\\mbattrtitleformat{PER}\\\\%\n"
            "\\begin{small}")
        return
    def end_mbstr(self, mbstr):
        self.html_file.write("\\end{small} & %\n")

    def start_mbend(self, mbend):
        self.html_file.write("\\begin{small}")
        return
    def end_mbend(self, mbend):
        self.html_file.write("\\end{small} & %\n")
        return

    def start_mbag(self, mbag):
        self.html_file.write("\\begin{small}")
        return
    def end_mbag(self, mbag):
        self.html_file.write("\\end{small} & %\n")
        return
    
    def start_mbspd(self, mbag):
        self.html_file.write("\\begin{small}")
        return
    def end_mbspd(self, mbag):
        self.html_file.write("\\end{small} & %\n")
        return
    
    def start_mbluck(self, mbag):
        self.html_file.write("\\begin{small}")
        return
    def end_mbluck(self, mbag):
        self.html_file.write("\\end{small} & %\n")
        return
    
    def start_mbwil(self, mbag):
        self.html_file.write("\\begin{small}")
        return
    def end_mbwil(self, mbag):
        self.html_file.write("\\end{small} & %\n")
        return
    
    def start_mbper(self, mbag):
        self.html_file.write("\\begin{small}")
        return
    def end_mbper(self, mbag):
        self.html_file.write("\\end{small}"
                              "\\end{tabular}"
                              "\\\\"
                              "\n")
        # \\%\n"
        #"\\mbsep\\[-0.15cm]%"
        #)
        return
    
    def start_mbabilities(self, mbabilities):
        self.html_file.write(r"\textbf{Abilities}: ")
        return
    def end_mbabilities(self, mbabilities):
        self.html_file.write("\\\\\n")
        return

    def start_mbaspects(self, mbaspects):
        self.html_file.write(r"\textbf{Aspects:} ")
        return
    def end_mbaspects(self, mbaspects):
        self.html_file.write("\\\\\n")
        return
    
    def start_mbdescription(self, mbdescription):
        self.html_file.write(r"\textbf{Description:} ")
        return
    def end_mbdescription(self, mbdescription):
        self.html_file.write("\n")
        return

    
    def start_npcs(self, npcs):
        self.html_file.write(r"NPCS!!")
        return

    def end_npcs(self, npcs):
        self.html_file.write("END NPCS!!\n")
        return
    
    
    def start_npcgroup(self, npcs):
        self.html_file.write(r"X")
        return

    def end_npcgroup(self, npcs):
        self.html_file.write("XX\n")
        return

    
    def start_npc(self, npcs):
        self.html_file.write(r"X")
        return

    def end_npc(self, npcs):
        self.html_file.write("XX\n")
        return

    def start_name(self, name):
        self.html_file.write(r"X")
        return

    def end_name(self, name):
        self.html_file.write("XX\n")
        return

    start_health = no_op
    end_health = no_op
    start_stamina = no_op
    end_stamina = no_op


    def start_monsterid(self, name):
        self.html_file.write(r"X")
        return

    def end_monsterid(self, name):
        self.html_file.write("XX\n")
        return
    

    
