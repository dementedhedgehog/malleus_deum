# -*- coding: utf-8 -*-
from os.path import join, splitext
import sys
import config
from utils import (
    normalize_ws,
    convert_str_to_bool,
    convert_str_to_int,
    COMMENT,
    attrib_is_true
)
from config import use_imperial

from npcs import NPC, NPCGroup


# \usepackage[paperwidth=8.125in,paperheight=10.250in]{geometry}
#%% lulu
# %%\usepackage[paperwidth=21.59cm,paperheight=27.94cm]{geometry}
#%% documentclass[twocolumn,oneside]{book}
#%% blurb

latex_frontmatter = r"""
\documentclass[%s,twocolumn,oneside]{book}
\usepackage[unicode]{hyperref} %% for hyperlinks in pdf
\usepackage{bookmark}          %% fixes a hyperref warning.
\usepackage{caption}           %% extra captions
\usepackage{color}             %% color.. what can I say
\usepackage{fancyhdr}          %% header control
\usepackage{fancybox}          %% fancy boxes.. eg box outs
\usepackage{graphicx}          %% for including images
\usepackage{fontspec}          %% fine font control
\usepackage{titlesec}          %% for fancy titles
\usepackage{lettrine}          %% for drop capitals
\usepackage{tabularx}          %% for tables  
\usepackage[table]{xcolor}     %% for tables with colour
\usepackage{booktabs}          %% for tables
\usepackage{calc}              %% for table width calculations
\usepackage{xcolor}            %% for color aliases    
\usepackage{wallpaper}         %% for the paper background
\usepackage{enumerate}         %% for roman numerals in enumerations
\usepackage{lipsum}            %% for generating debug text
\usepackage{wrapfig}           %% sidebar thingy
\usepackage{makeidx}           %% for building the index
\usepackage{amssymb}           %% for special maths symbols, e.g. slanted geq
\usepackage{xtab}              %% for multipage tables
\usepackage{rotating}          %% for sidewaystable
\usepackage{parskip}           %% non indented paragraphs
\usepackage{multicol}          %% used for four column mode.
\usepackage{epstopdf}

%% include subsubsections in the table of contents
\setcounter{tocdepth}{3}


%% fonts
\newfontfamily{\cloisterblack}[Path=fonts/]{Cloister Black}
\newfontfamily{\carolingia}[Path=fonts/]{Carolingia}
\newfontfamily{\rpgdice}[Path=fonts/]{RPGDice}
\newfontfamily{\sherwood}[Path=fonts/]{Sherwood}
\newfontfamily{\libertine}{Linux Libertine O}

\newfontfamily{\rpgtitlefont}[Path=fonts/, Scale=10.0]{Dogma}
\newfontfamily{\rpgchapterfont}[Path=fonts/, Scale=1.0]{Cloister Black}
\newfontfamily{\rpgtitlesubtitlefont}[Path=fonts/]{Cloister Black}
\newfontfamily{\rpgtitleauthorfont}[Path=fonts/]{Dogma}
\newfontfamily{\rpgdropcapfont}[Path=fonts/, Scale=1.2]{Cloister Black}            
\newcommand{\rpgsectionfont}{\cloisterblack}


%% colours
\definecolor{maroon}{RGB}{128,0,0}
\definecolor{darkred}{RGB}{139,0,0}
\definecolor{barnred}{RGB}{124,10,2}
\definecolor{rosetaupe}{RGB}{144,93,93}
\definecolor{rosewood}{RGB}{101,0,11}
\definecolor{black}{RGB}{0,0,0}

%% colour aliases
\colorlet{rpgtitlefontcolor}{black}
\colorlet{rpgchapterfontcolor}{black}
\colorlet{rpgsectionfontcolor}{rosewood}
\colorlet{monstertitlecolor}{rosewood}
\colorlet{monstertagscolor}{black}


%% spacing
%% drop is a vspace 1/100th the page text height.
\newlength\drop
\drop = 0.01\textheight

\titleformat{name=\chapter}[hang]
{\Huge\bfseries\rpgchapterfont\color{rpgchapterfontcolor}}
{}{1em}{}

\titleformat{\section}
{\rpgsectionfont\LARGE\color{rpgsectionfontcolor}}
{\thesection}{0.5em}{}

\newcommand{\rpgtableheader}{\bfseries\selectfont}{}

\newcommand\rpgtablesection[1]{
\rule{0pt}{1ex}\bfseries\scriptsize #1}

%% symbols
\newcommand{\reactionsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}R\endgroup}{reaction}}

\newcommand{\startsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}1\endgroup}{start}}

\newcommand{\talksymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}t\endgroup}{talk}}

\newcommand{\fastsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}2\endgroup}{fast}}

\newcommand{\mediumsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}3\endgroup}
{medium}}

\newcommand{\slowsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}4\endgroup}{slow}}

\newcommand{\startandreactionsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}1+R\endgroup}
{startandreactionsymbol}}

\newcommand{\mediumorslowsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}3/4\endgroup}
{mediumorslowsymbol}}

\newcommand{\resolutionsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}5\endgroup}{resolution}}

\newcommand{\surprisesymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}s\endgroup}
{surprise}}

\newcommand{\ambushsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}a\endgroup}
{ambush}}

\newcommand{\initiativesymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}i\endgroup}
{initiative}}

\newcommand{\fightreachsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}3:4\endgroup}
{fight-reach}}

\newcommand{\noncombatsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}n\endgroup}
{non-combat}}

\newcommand{\tagsymbol}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}T\endgroup}
{tag}}

\newcommand{\arrowleft}
{\texorpdfstring{\begingroup\rpgdice\selectfont{}<\endgroup}
{arrowleft}}

%% the font for the body of the text
\setmainfont[Scale=0.95]{Linux Libertine O}
\setromanfont[
  Mapping=tex-text, 
  Mapping=tex-text, 
  Ligatures={Common,Rare,Discretionary}]{Linux Libertine O}
            
%% special bullet symbol
\newcommand{\rpgbullet}
{\begingroup\rpgdice\large\selectfont{}*\endgroup}
\renewcommand{\labelitemi}{\rpgbullet}        

%% success/fail/attempt symbols
\newcommand{\rpgsuccess}
 {\begingroup\rpgdice\selectfont{}y\endgroup}
\newcommand{\rpgfail}
 {\begingroup\rpgdice\selectfont{}x\endgroup}
\newcommand{\rpgattempt}
 {\begingroup\rpgdice\selectfont{}?\endgroup}          


%% achetype ability mark up symbols (star, empty-star and exclamation)
\newcommand{\rpginnatearchetypeabilitysymbol}%%
{\begingroup\rpgdice\selectfont\symbol{"201C}\endgroup}

\newcommand{\rpginnateabilitysymbol}%%
{\begingroup\rpgdice\selectfont\symbol{"201D}\endgroup}

\newcommand{\rpgrecommendedabilitylevelsymbol}%%
{\begingroup\rpgdice\selectfont{}!\endgroup}

%% dice pool notation          
\newcommand{\dfour} 
 {\begingroup\rpgdice\selectfont{}A\endgroup}
\newcommand{\dsix}
 {\begingroup\rpgdice\selectfont{}B\endgroup}
\newcommand{\deight}
 {\begingroup\rpgdice\selectfont{}C\endgroup}
\newcommand{\dten}
 {\begingroup\rpgdice\selectfont{}D\endgroup}
\newcommand{\dtwelve}
 {\begingroup\rpgdice\selectfont{}E\endgroup}
\newcommand{\dtwenty}
 {\begingroup\rpgdice\selectfont{}F\endgroup}
\newcommand{\dany}
 {\begingroup\rpgdice\selectfont{}G\endgroup}
\newcommand{\dpool}
 {\begingroup\rpgdice\selectfont{}H\endgroup}
\newcommand{\firststage}
 {\begingroup\rpgdice\selectfont{}1\endgroup}
\newcommand{\secondstage}
 {\begingroup\rpgdice\selectfont{}2\endgroup}
\newcommand{\thirdstage}
{\begingroup\rpgdice\selectfont{}3\endgroup}
\newcommand{\fourthstage}
{\begingroup\rpgdice\selectfont{}4\endgroup}
\newcommand{\fifthstage}
{\begingroup\rpgdice\selectfont{}5\endgroup}



%% skill point symbols
\newcommand{\lore}{%%
\begingroup\rpgdice\selectfont{}l\endgroup}
\newcommand{\martial}{%%
\begingroup\rpgdice\selectfont{}m\endgroup}
\newcommand{\general}{%%
\begingroup\rpgdice\selectfont{}g\endgroup}
\newcommand{\magical}{%%
\begingroup\rpgdice\selectfont{}z\endgroup}


%% special provenance symbol
\newcommand{\rpgprovenancesymbol}
{\begingroup\fontspec{rpgdice}\Large\selectfont{}>\endgroup}

\newcommand{\flourish}{}

%% the index 
\makeindex

%% start other evironments in newenvironments like this 
%% put it after a section, not just before

\newenvironment{playexample}{ 
\vspace{0.4em}
\flourish
\begin{quote}
\small
\carolingia
\setlength{\parindent}{0pt}
\raggedright}
{\end{quote}\flourish\vspace{0.4em}}

%% don't break paragraphs
\widowpenalties 1 10000
\raggedbottom

\hypersetup{%%
colorlinks=false,%% hyperlinks will be black
linkbordercolor=blue,%% hyperlink borders will be red
pdfborderstyle={/S/U/W 1}%% border style will be underline of width 1pt
}

%% Archetype table formatting
\newcommand\achetypenameformat[1]{\begingroup\scriptsize#1\endgroup}

%% "\AtEndDocument{\clearpage\ifodd\value{page}\else\null\clearpage\fi}


%%
%% Monsters
%%

\newcommand\mbsep{%%
\includegraphics[width=\columnwidth,height=0.1cm]{./resources/hrule/hrule.png}%%
\vspace{-0.5cm}\hfill\break}

\newenvironment{mbtitle}%%
{\sherwood\color{monstertitlecolor}\begin{large}}%%
{\end{large}\vspace{0.0cm}\hfill}

\newenvironment{mbtags}%%
{\color{monstertagscolor}\begin{normalsize}}%%
{\end{normalsize}\vspace{0.0cm}\break}

\newenvironment{mbac}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbmove}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbhp}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbresolve}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbinitiativebonus}
{\color{monstertitlecolor}\normalsize}{}

\newenvironment{mbmagic}
{\color{monstertitlecolor}\normalsize}{}

\newenvironment{npcname}
{\color{monstertitlecolor}\normalsize}{}

\newenvironment{npchp}
{\color{monstertitlecolor}\normalsize}{}


\newcommand\mbattrtitleformat[1]{\normalsize\textbf{#1}}

%% the document! 
\begin{document}

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


class LatexFormatter:
    
    def __init__(self, latex_file, db):

        # open latex file pointer
        self.latex_file = latex_file
        
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
        #self.index_entry_see = None
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
        """We've got a lot of handlers that don't need to do anything.. do nothing once."""
        pass

    
    def start_book(self, book):
        
        # must be a valid latex paper size
        if config.paper_size == "a4":
            paper_size = "a4paper"
        elif config.paper_size == "letter":
            paper_size = "letterpaper"
        else:
            raise Exception("Unknown paper size.  Pick one of [a4, letter] in config.py")

        orientation = ""
        landscape = attrib_is_true(book, "landscape")
        formatting = paper_size + orientation
        self.latex_file.write(latex_frontmatter % formatting)

        if config.display_page_background:
            self.latex_file.write(
                "\n"
                "% use a background image\n"
                "\\CenterWallPaper{1.0}{./resources/paper_" + paper_size + ".jpg}"
                "\n\n")
        return


    def end_book(self, book):
        self.latex_file.write("\\end{document}\n")        
        return


    def start_appendix(self, appendix):
        self.latex_file.write("\\appendix\n"
                              "\\addcontentsline{toc}{chapter}{APPENDICES}\n")
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
        self.latex_file.write("\\fightreachsymbol{}")
        return
    end_fightreach = no_op    

    def start_start(self, symbol):
        self.latex_file.write("\\startsymbol{}")
        return
    end_start = no_op    
    
    def start_fast(self, symbol):
        self.latex_file.write("\\fastsymbol{}")
        return
    end_fast = no_op
    
    def start_medium(self, symbol):
        self.latex_file.write("\\mediumsymbol{}")
        return
    end_medium = no_op
    
    def start_mediumorslow(self, symbol):
        self.latex_file.write("\\mediumorslowsymbol{}")
        return
    end_mediumorslow = no_op
    
    def start_startandreaction(self, symbol):
        self.latex_file.write("\\startandreactionsymbol{}")
        return
    end_startandreaction = no_op
    
    def start_slow(self, symbol):
        self.latex_file.write("\\slowsymbol{}")
        return
    end_slow = no_op
    
    def start_noncombat(self, symbol):
        self.latex_file.write("\\noncombatsymbol{}")
        return
    end_noncombat = no_op    

    def start_tag(self, symbol):
        self.latex_file.write("\\tagsymbol{}")
        return
    end_tag = no_op    

    def start_newpage(self, symbol):
        self.latex_file.write("\\newpage[4]\n")
        return
    end_newpage = no_op    

    def start_resolution(self, symbol):
        self.latex_file.write("\\resolutionsymbol{}")
        return
    end_resolution = no_op
    
    def start_talk(self, symbol):
        self.latex_file.write("\\talksymbol{}")
        return
    end_talk = no_op
    
    def start_act(self, symbol):
        self.latex_file.write("\\actsymbol{}")
        return
    end_act = no_op

    def start_ambush(self, symbol):
        self.latex_file.write("\\ambushsymbol{}")
        return
    end_ambush = no_op
    
    def start_surprise(self, symbol):
        self.latex_file.write("\\surprisesymbol{}")
        return
    end_surprise = no_op
    
    def start_reaction(self, symbol):
        self.latex_file.write("\\reactionsymbol{}")
        return
    end_reaction = no_op
    
    def start_initiative(self, symbol):
        self.latex_file.write("\\initiativesymbol{}")
        return
    end_initiative = no_op

    def start_arrowleft(self, symbol):
        self.latex_file.write("\\arrowleft{}")
        return
    end_arrowleft = no_op    

    
    # def get_latex_symbols(self, title):
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
    #     tex += self.get_latex_symbols(title)
        
    #     self.latex_file.write(tex) 
    #     self.latex_file.write("}\n") 
    #     return
    # end_subsubsection = no_op

    start_subsubsection = no_op
    end_subsubsection = no_op

    #start_subsectiontitle = no_op    
    #end_subsectiontitle = no_op
    def start_subsubsectiontitle(self, section_title):
        self.latex_file.write("\\subsubsection{")
        return
    def end_subsubsectiontitle(self, section_title):
        self.latex_file.write("}")
        return
    
        
    start_ability_title = no_op
    end_ability_title = no_op

    def start_ability_id(self, ability_id):        
        self.latex_file.write("ID: %s\\\n" % ability_id) 
        return
    end_ability_id = no_op

    start_ability_group = no_op
    def end_ability_group(self, ability_group):
        self.latex_file.write("%s\n" % normalize_ws(ability_group.text))
        return

    start_ability_class = no_op
    def end_ability_class(self, ability_class):
        self.latex_file.write("%s\n" % normalize_ws(ability_class.text))
        return

    start_action_points = no_op
    def end_action_points(self, action_points):
        self.latex_file.write("%s\n" % normalize_ws(action_points.text))
        return

    def start_and(self, and_element):
        self.latex_file.write("\\&")
        return
    end_and = no_op


    def start_lore(self, element):
        self.latex_file.write("\\lore{}")
        return    
    end_lore = no_op

    def start_martial(self, element):
        self.latex_file.write("\\martial{}")
        return    
    end_martial = no_op

    def start_general(self, element):
        self.latex_file.write("\\general{}")
        return    
    end_general = no_op

    def start_magical(self, element):
        self.latex_file.write("\\magical{}")
        return    
    end_magical = no_op

    def start_geqqsymbol(self, geqq_element):
        self.latex_file.write("$\stackrel{\scriptscriptstyle ?}{\geq}{}$")
        return
    end_geqqsymbol = no_op

    def start_leqqsymbol(self, geqq_element):
        self.latex_file.write("$\stackrel{\scriptscriptstyle ?}{\leq}{}$")
        return
    end_leqqsymbol = no_op

    def start_newline(self, newline):
        self.latex_file.write("\\newline\n")
        return
    end_newline = no_op

    start_pageref = no_op
    def end_pageref(self, pageref):
        self.latex_file.write("~\\pageref{%s}" % normalize_ws(pageref.text))
        return

    start_ref = no_op
    def end_ref(self, ref):
        self.latex_file.write("~\\ref{%s}" % normalize_ws(ref.text))
        return

    def start_index(self, index):
        self.latex_file.write("\\clearpage\n")               
        self.latex_file.write("\\addcontentsline{toc}{chapter}{Index}\n")               
        self.latex_file.write("\\printindex\n")
        return
    end_index = no_op

    # def start_section(self, section):
    #     title_element = section.find("sectiontitle")
    #     if title_element is None:
    #         title = ""
    #     else:
    #         title = title_element.text

    #     self.latex_file.write("\\section{%s}\n" % title)               
    #     return
    start_section = no_op
    end_section = no_op

    def start_sectiontitle(self, section_title):
        self.latex_file.write("\\section{")#  % title)               
        return

    def end_sectiontitle(self, section_title):
        self.latex_file.write("}\n")#  % title)               
        return
    
    start_subsection = no_op
    end_subsection = no_op

    def start_subsectiontitle(self, section_title):
        self.latex_file.write("\\subsection{")
        return
    def end_subsectiontitle(self, section_title):
        self.latex_file.write("}")
        return

    def start_playexample(self, playexample):
        self.latex_file.write("\\begin{playexample}\n")
        return

    def end_playexample(self, playexample):
        self.latex_file.write(playexample.text)                
        self.latex_file.write("\\end{playexample}\n")        
        return
        
    def start_level(self, level):
        self._current_row_in_level_table += 1
        if self._current_row_in_level_table % 2 == 1:            
            self.latex_file.write("\\rowcolor{blue!20} \n")
        else:
            self.latex_file.write("\\rowcolor{white!20} \n")
        return
    
    def end_level(self, level):
        self.latex_file.write(" \\\\\n")
        return        
        
    def start_level_xp(self, element):
        self.latex_file.write(" %s &" % element.text)
        return    
    end_level_xp = no_op
    
    def start_level_number(self, element):
        self.latex_file.write(" %s &" % element.text)
        return    
    end_level_number = no_op

    def start_level_combat(self, element):
        self.latex_file.write("\\rpgcombatsymbol %s " % element.text)
        return    
    end_level_combat = no_op

    def start_level_training(self, element):
        self.latex_file.write("\\rpgtrainingsymbol %s " % element.text)
        return    
    end_level_training = no_op

    def start_level_learning(self, element):
        self.latex_file.write("\\rpglearningsymbol %s " % element.text)
        return    
    end_level_learning = no_op
    
    def start_level_description(self, element):
        self.latex_file.write(" %s " % element.text)
        return

    def end_level_description(self, element):
        pass

    def start_titlepage(self, chapter):
        self.latex_file.write("\\begin{titlepage}\n"
                              "\\begin{center}\n")
        return

    def end_titlepage(self, chapter):
        self.latex_file.write("\\end{center}\n"
                              "\\end{titlepage}\n")
        return

    def start_emph(self, emph):
        return

    def end_emph(self, emph):
        self.latex_file.write("\\emph{%s}" % normalize_ws(emph.text))
        return

    def start_equation(self, equation):
        self._equation_first_line = True
        self.latex_file.write("\\begin{tabbing}\n "
                              "\\hspace*{0.5cm}\= \kill \\nopagebreak \n")
        return

    def end_equation(self, equation):
        self.latex_file.write("\\end{tabbing}\\vspace{-0.5cm}\n ")
        return


    def start_line(self, line):
        """
        Start equation line.
        
        """
        if not self._equation_first_line:
            self.latex_file.write("\\> ") 
        self._equation_first_line = False
        if line.text:
            self.latex_file.write(" %s " % normalize_ws(line.text))
        return

    def end_line(self, line):
        self.latex_file.write("\\\\\n ")
        return


    def start_bold(self, bold):
        self.latex_file.write("\\textbf{%s} " % normalize_ws(bold.text))
        return
    end_bold = no_op

    def start_smaller(self, smaller):
        self.latex_file.write("\\scriptsize{%s} " % normalize_ws(smaller.text))
        return
    end_smaller = no_op

    def handle_text(self, text):
        if text is not None:
            if isinstance(text, unicode):                           
                #self.latex_file.write(text.encode('utf8'))
                self.latex_file.write(text)
            else:
                self.latex_file.write(text)
        return

    start_indexentry = no_op
    def end_indexentry(self, index_entry):
        if self.index_entry_subentry is not None:
            self.latex_file.write("\\index{%s!%s}" % (
                normalize_ws(index_entry.text), self.index_entry_subentry))
            self.index_entry_subentry = None
            
        else:
            self.latex_file.write("\\index{%s}" % normalize_ws(index_entry.text))
        return

    # subentry element in index entry
    start_subentry = no_op
    def end_subentry(self, index_subentry):
        self.index_entry_subentry = normalize_ws(index_subentry.text)
        return

    def start_defn(self, defn):
        self.latex_file.write(" \\textbf{%s}" % (normalize_ws(defn.text)))
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

        self.latex_file.write(normalize_ws(distance_text).strip())
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
        self.latex_file.write("\\chapter{%s}\n" % title)
        return

    def end_chapter(self, chapter):
        # remember to drop cap the first letter of the word in this chapter
        self._drop_capped_first_letter_of_chapter = False
        return

    def start_p(self, paragraph):
        """
        Start paragraph.

        """
        self.latex_file.write("\n\n")

        # turn of paragraph indentation?
        no_indent = attrib_is_true(paragraph, "noindent")
        if no_indent:
            self.latex_file.write("\\noindent ")
                
        # add drop caps to the first word of every chapter
        if not self._drop_capped_first_letter_of_chapter:
            self._drop_capped_first_letter_of_chapter = True
            if paragraph.text:
                words = paragraph.text.split()
            else:
                words = []
            if len(words) > 0:
                first_word = words[0]
                if len(first_word) > 0:
                    first_letter = first_word[0]
                    other_letters = first_word[1:]

                    drop_cap_word = ("\\lettrine["
                                     "lines=2, "
                                     "lraise=0.1, "
                                     # horizontal displacement of the indented text
                                     "findent=-0.14em, " 
                                     "nindent=0.3em, "
                                     "slope=0em]{\\rpgdropcapfont %s}{%s}" %
                                     (first_letter, other_letters))
                words = [drop_cap_word, ] + words[1:]
        return

    def end_p(self, paragraph):
        self.latex_file.write("\n\n")
        return

    def start_design(self, design):
        if config.print_design_notes:
            self.latex_file.write("\n\n")
            self.latex_file.write(design.text)        
        return

    def end_design(self, design):
        self.latex_file.write("\n\n")
        return


    def start_provenance(self, provenance):
        self.latex_file.write("\n\n")        

        if config.print_provenence_notes:
            self.latex_file.write("\\begin{center}")
            self.latex_file.write("\\begin{minipage}[c]{0.9\linewidth}")
            self.latex_file.write("\\rpgprovenancesymbol\\hspace{0.2em}") 
            self.latex_file.write(provenance.text)        
        return

    def end_provenance(self, provenance):
        if config.print_provenence_notes:
            self.latex_file.write("\\end{minipage}")        
            self.latex_file.write("\\end{center}")
            self.latex_file.write("\n\n")
        return


    def start_author(self, author):
        self.latex_file.write("{\\LARGE \\rpgtitleauthorfont %s}\\\\" % author.text)        
        return

    def end_author(self, author):
        return

    def start_version(self, version):
        #self.latex_file.write("{\\LARGE \\rpgtitleauthorfont %s}\\\\" % version.text)        
        return
    
    def end_version(self, npchps):
        return

    
    def start_title(self, title):
        self.latex_file.write("{ \\color{rpgtitlefontcolor} \\rpgtitlefont %s }\\\\\n"
                              % title.text)
        return

    def end_title(self, title):
        return

    def start_caption(self, caption):
        self.latex_file.write("\\caption{%s}" % caption.text)
        return

    def end_caption(self, caption):
        return

    def start_subtitle(self, subtitle):        
        self.latex_file.write("{\\large \\rpgtitlesubtitlefont  %s}\\\\\n" % subtitle.text)
        return

    def end_subtitle(self, title):
        return

    start_chaptertitle = no_op
    end_chaptertitle = no_op

    def start_img(self, img):
        if config.draw_imgs:
            if config.debug_outline_images:
                self.latex_file.write("\\fbox{")

            self.latex_file.write("\t\\begin{center}\n")

            filename = img.get("src")
            # image without a box
            self.latex_file.write("\t\\includegraphics[scale=%s]{%s}\n"
                                  % (img.get("scale", default="1.0"), filename))
            # image with a box around the outside!
            #self.latex_file.write("\t\\fbox{\\includegraphics[scale=%s]{%s}}\n"
            #                      % (img.get("scale", default="1.0"), filename))
        return

    def end_img(self, img):
        if img.text is not None:
            self.latex_file.write("\t%s\n" % img.text)
        self.latex_file.write("\t\\end{center}\n")
        if config.debug_outline_images:
            self.latex_file.write("}")
        return

    def start_figure(self, figure):
        position = "ht"
        if "position" in figure.attrib:
            position = figure.get("position")

                    
        if attrib_is_true(figure, "fullwidth"):
            if attrib_is_true(figure, "sideways"):
                figure_name = "sidewaysfigure*"
            else:
                figure_name = "figure*"
        else:
            if attrib_is_true(figure, "sideways"):
                figure_name = "sidewaysfigure"
            else:
                figure_name = "figure"
            
        self.latex_file.write("\\begin{%s}[%s]\n" % (figure_name, position))
        self.latex_file.write("\\centering\n")
        return

    def end_figure(self, figure):
        caption = figure.get("caption")
        if caption is not None:
            self.latex_file.write("\\caption{%s}\n" % caption)        

        # fullwidth = False
        # if "fullwidth" in figure.attrib:
        #     fullwidth = figure.get("fullwidth")

        # if attrib_is_true(figure, "fullwidth"):
        #     figure_name = "figure*"
        # else:
        #     figure_name = "figure"

        if attrib_is_true(figure, "fullwidth"):
            if attrib_is_true(figure, "sideways"):
                figure_name = "sidewaysfigure*"
            else:
                figure_name = "figure*"
        else:
            if attrib_is_true(figure, "sideways"):
                figure_name = "sidewaysfigure"
            else:
                figure_name = "figure"
            
 
        # if attrib_is_true(figure, "fullwidth"):
        #     self.latex_file.write("\\end{figure*}\n")
        # else:
        #     self.latex_file.write("\\end{figure}\n")

        self.latex_file.write("\\end{%s}\n" % figure_name)            
        return

    def start_olist(self, enumeration):
        """
        Start enumeration, ordered list of things.

        """
        # the [i] gets us roman numerals in the enumeration
        self.latex_file.write("\\begin{enumerate}[i.]\n")
        return

    def end_olist(self, enumeration):
        self.latex_file.write("\\end{enumerate}\n")
        return

    def start_descriptions(self, description_list):
        self.latex_file.write("\\begin{description}\n")

        self.description_terms_on_their_own_line = False
        if "termonnewline" in description_list.attrib:
            self.description_terms_on_their_own_line = description_list.get("termonnewline")
        return

    def end_descriptions(self, description_list):
        # note seeing weird artifacts in embedded latex lists without the extra newline
        self.latex_file.write("\\end{description}\n\n")
        return

    def start_term(self, term):
        """
        A description term.

        """
        #if term.text is not None:
        #    assert not self.description_terms_on_their_own_line
        #    # if self.description_terms_on_their_own_line:
        #    #     self.latex_file.write("\\item[%s] \hfill \n" % term.text)
        #    # else:
        #    #     self.latex_file.write("\\item[%s]" % term.text)
        self.latex_file.write("\\item[")
        return
    def end_term(self, term):
        self.latex_file.write("]")

    def start_description(self, description):
        #if description.text is not None:
        #    self.latex_file.write("%s" % description.text)
        return

    def end_description(self, list_item):
        return


    def start_list(self, list_element):
        self.latex_file.write("\\begin{itemize}\n")
        return

    def end_list(self, list_element):
        self.latex_file.write("\\end{itemize}\n")
        return

    def start_li(self, list_item):
        """
        Start list item.

        """
        self.latex_file.write("\\item ")
        
        if list_item.text is not None:
            self.latex_file.write(normalize_ws(list_item.text))
        return
    end_li = no_op

    def start_comment(self, comment):
        return

    def end_comment(self, comment):
        return

    start_tablespec = no_op
    end_tablespec = no_op

    def start_table(self, table):
        category = get_text_for_child(table, "tablecategory")
        if category is None:
            raise Error("Table requires a tablecategory child element.")

        # Check whether we want compact tables!
        compact = attrib_is_true(table, "compact")
        
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

            if child.tag == "fixed":
                percent_width = float(child.text)
                table_spec_str += "p{%s\\hsize}" % percent_width
                
            elif child.tag is COMMENT:
               # ignore comments!
               pass

            else:
                raise Exception("Unknown table spec: %s" % child.tag)

            if DEBUG_COLUMN_WIDTH:
                table_spec_str += "|"
        self._number_of_columns_in_table = columns
        
        # veritcal space
        if compact:
            self.latex_file.write("\n\\vspace{-0.2cm}")
        else:
            self.latex_file.write("\n\\vspace{0.05cm}")

        # don't have paragraph indents buggering up our table layouts
        self.latex_file.write("\\noindent{}")
            

        # wrap single page tables in a table environment
        # (we use xtabular for multi-page tables and the table environment
        # confuses it about page size).        
        if figure:
            if sideways:
                self.latex_file.write("\\begin{sidewaystable*}[htp]")                
            elif fullwidth:
                self.latex_file.write("\\begin{table*}[ht]")
            else:
                self.latex_file.write("\\begin{table}")
        #else:
            #self.latex_file.write("\\captionsetup{type=figure}")

        #self.latex_file.write("\\centering")

        # reduce the line spacing in compact tables
        if compact:
            self.latex_file.write("\\begingroup\n")
            self.latex_file.write("\\renewcommand\\arraystretch{0.75}\n")
        
        self.latex_file.write(" \\begin{center} ")
        if fullwidth:
            # normal table environment
            self.latex_file.write("\\begin{tabularx}{1.0\\textwidth}{%s} " 
                                  % table_spec_str)
        else:
            self.latex_file.write("\\begin{tabularx}{1.0\\linewidth}{%s}" 
                                  % table_spec_str)

        if figure:
            self.latex_file.write(" \\toprule{}")

        return


    def end_table(self, table): # , use_xtabular = False):

        # Check whether we want compact tables!
        compact = attrib_is_true(table, "compact")
        
        category = get_text_for_child(table, "tablecategory")
        if category is None:
            raise Error("Table requires a tablecategory child element.")

        table_title = table.find("tabletitle")        
        if table_title is not None:
            if hasattr(table_title, "text"):
                table_title = table_title.text
            table_title = table_title.strip()
        else:
            table_title = ""

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
            self.latex_file.write("\\bottomrule ")    

        # normal table environment
        self.latex_file.write("\\end{tabularx}")
        
        if table_title != "":
            self.latex_file.write(" \\captionof{table}{%s}" % table_title)

        #if 
        self.latex_file.write(" \\end{center}")
        #if compact
        #self.latex_file.write(" \\end{center}\\vspace{0.4cm}")
        
        if compact:
            self.latex_file.write("\\vspace{0.14cm}")
            self.latex_file.write("\\endgroup{}\n")
        
            
        # we also need to find any labels! (place them after the caption!)
        label = table.find("tablelabel")
        if label is not None:
            self.start_label(label)
            self.end_label(label)
            
        if figure:
            if sideways:
                self.latex_file.write("\\end{sidewaystable*}")        
            elif fullwidth:
                self.latex_file.write("\\end{table*}")        
            else:
                self.latex_file.write("\\end{table}")
                # vertical space
                self.latex_file.write("\n\\\\\n")
            
        self.latex_file.write("\n\n")
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
        self.latex_file.write("\\rpgtablesection{%s}" % tablesection.text.strip())
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
            self.latex_file.write("\\rowcolor{blue!33}\n")
            assert False

        elif (self._current_row_in_table + 1) % 2 == 1:                
            self.latex_file.write("\\rowcolor{blue!20}\n")
        return

    def end_tablerow(self, table_title):
        self.latex_file.write("\\tabularnewline ")
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

        # override for table headers
        parent = table_data.getparent()
        if parent.tag == "tableheaderrow":
            text = "\\begin{rpgtableheader}"

        if width > 1 or align != "l":
           self.latex_file.write("\\multicolumn{%s}{%s}{" % (width, align))
        return

    def end_td(self, table_data):
        width = table_data.get("width")
        if width is not None:
            width = int(width)
        else: 
            width = 1
            
        align = table_data.get("align")
        if align is None:
            align = "l"
        
        parent = table_data.getparent()
        if parent.tag == "tableheaderrow":
            text = "\\end{rpgtableheader}"

        if width > 1 or align != "l":
            # multicolumn table data
            self.latex_file.write("}")

        if self._current_column_in_table != 0:
            self.latex_file.write(" & ")                
        return    

    # table headers are a type of table data
    start_th = start_td
    end_th = end_td


    # def start_multicolumntd(self, table_data):
    #     """
    #     Start muilticolumn table data.

    #     """
    #     if "columns" in table_data.attrib:
    #         columns = int(table_data.get("columns"))

    #     if ((self._current_column_in_table + columns) > self._number_of_columns_in_table):
    #         raise Exception("Multicolumn table data overflows table!")

    #     self._current_column_in_table = (
    #         (self._current_column_in_table + columns) % self._number_of_columns_in_table)

    #     #if self._current_row_in_table == 0:
    #     #     self.latex_file.write("\\rpgtableheader{%s} \n" %
    #     #                           table_data.text)
    #     #else:

        
    #     # self.latex_file.write("\\multicolumn{%s}{c}{\\rpgtableheader{%s}}" % 
    #     #                        (columns, table_data.text))
    #     self.latex_file.write("\\multicolumn{%s}{c}{\\rpgtableheader{%s" %
    #                           (columns, table_data.text))

    #     # if self._current_column_in_table != 0:
    #     #     self.latex_file.write(" & ")                        
    #     # return
    # #end_multicolumntd = no_op
    # def end_multicolumntd(self, table_data):

    #     self.latex_file.write("}}")
        
    #     if self._current_column_in_table != 0:
    #         self.latex_file.write(" & ")
    #     return


    def start_tableofcontents(self, table_of_contents):
        self.latex_file.write("\\tableofcontents\n")
        return

    def end_tableofcontents(self, table_of_contents):
        return

    def start_list_of_figures(self, list_of_figures):
        self.latex_file.write("\\listoffigures\n")
        return

    def end_list_of_figures(self, list_of_figures):
        return

    def start_list_of_tables(self, list_of_tables):
        self.latex_file.write("\\listoftables\n")
        return

    def end_list_of_tables(self, list_of_tables):
        return

    def start_combat_symbol(self, combat_symbol):
        self.latex_file.write("\\rpgcombatsymbol{}")
        return
    end_combat_symbol = no_op

    def start_innateabilitylevelsymbol(self, innate_ability_symbol):
        self.latex_file.write("\\rpginnateabilitysymbol{}")
        return
    end_innateabilitylevelsymbol = no_op

    def start_innatearchetypeabilitylevelsymbol(self, innate_ability_symbol):
        self.latex_file.write("\\rpginnatearchetypeabilitysymbol{}")
        return
    end_innatearchetypeabilitylevelsymbol = no_op

    def start_recommendedabilitylevelsymbol(self, recommended_ability_level_symbol):
        self.latex_file.write("\\rpgrecommendedabilitylevelsymbol{}")
        return
    end_recommendedabilitylevelsymbol = no_op

    def start_training_symbol(self, training_symbol):
        self.latex_file.write("\\rpgtrainingsymbol{}")
        return
    end_training_symbol = no_op

    def start_learning_symbol(self, learning_symbol):
        self.latex_file.write("\\rpglearningsymbol{}")
        return
    end_learning_symbol = no_op


    def start_label(self, label):
        self.latex_file.write("\n\\label{%s} " % normalize_ws(label.text))
        return
    end_label = no_op


    def start_fourcolumns(self, threecolumns):
        self.latex_file.write("\\onecolumn\\begin{multicols}{4}\n")
        return
    
    def end_fourcolumns(self, ability_group):
        self.latex_file.write("\\end{multicols}\\twocolumn\n")
        return


    
    def start_attempt(self, success):
        self.latex_file.write("\\rpgattempt{}")
        return
    end_attempt = no_op

    def start_success(self, success):
        self.latex_file.write("\\rpgsuccess{}")
        return
    end_success = no_op

    def start_fail(self, fail):
        self.latex_file.write("\\rpgfail{}")
        return
    end_fail = no_op

    def start_eg(self, fail):
        self.latex_file.write("e.g.\@{}")
        return
    end_eg = no_op

    def start_ie(self, fail):
        self.latex_file.write("i.e.\@{}")
        return
    end_ie = no_op

    def start_etc(self, fail):
        self.latex_file.write("etc.\@{}")
        return
    end_etc = no_op

    def start_notapplicable(self, fail):
        self.latex_file.write("ⁿ/ₐ")
        return
    end_notapplicable = no_op

    def start_d4(self, fail):
        self.latex_file.write("\\dfour{}")
        return
    end_d4 = no_op

    def start_d6(self, fail):
        self.latex_file.write("\\dsix{}")
        return
    end_d6 = no_op

    def start_d8(self, fail):
        self.latex_file.write("\\deight{}")
        return
    end_d8 = no_op
    
    def start_d10(self, fail):
        self.latex_file.write("\\dten{}")
        return
    end_d10 = no_op

    def start_d12(self, fail):
        self.latex_file.write("\\dtwelve{}")
        return
    end_d12 = no_op

    def start_d20(self, fail):
        self.latex_file.write("\\dtwenty{}")
        return
    end_d20 = no_op

    def start_dany(self, fail):
        self.latex_file.write("\\dany{}")
        return
    end_dany = no_op

    def start_dpool(self, fail):
        self.latex_file.write("\\dpool{}")
        return
    end_dpool = no_op


    def start_vspace(self, vspace):
        if vspace.text is None:
            drop = 1
        else:
            drop = convert_str_to_int(vspace.text)
        self.latex_file.write("\\vspace{%s\drop}\n" % drop)
        return

    def end_vspace(self, vspace):
        return

    #
    #
    #
               
    def bold_begin(self):
        self.latex_file.write("\\textbf{")
        return
    
    def bold_finish(self):
        self.latex_file.write("s} ")
        return

    def newline(self):
        self.latex_file.write("\\newline\n")
        return

    #
    # Monster blocks.
    #

    def start_monsterblock(self, monsterblock):
        self.latex_file.write(r"\begin{minipage}{\linewidth}")
        return

    def end_monsterblock(self, monsterblock):
        self.latex_file.write(r"\end{minipage}")
        return

    def start_mbtitle(self, mbtitle):
        self.latex_file.write(r"\mbsep{}\begin{mbtitle}")
        return

    def end_mbtitle(self, mbtitle):
        self.latex_file.write(r"\end{mbtitle}\noindent{}")
        return
    
    def start_mbtags(self, mbtags):
        self.latex_file.write(r"\begin{mbtags}")
        return

    def end_mbtags(self, mbtags):
        self.latex_file.write(r"\end{mbtags}\noindent")
        return

    def start_mbac(self, mbac):
        self.latex_file.write(r"\textbf{AC: }\begin{mbac}")
        return

    def end_mbac(self, mbac):
        self.latex_file.write(r"\end{mbac}\enspace{}")
        return

    def start_mbhp(self, mbhp):
        self.latex_file.write(r"\textbf{HP: }\begin{mbhp}")
        return
    
    def end_mbhp(self, mbhp):
        self.latex_file.write("\\end{mbhp}")
        return

    def start_mbmove(self, mbmove):
        self.latex_file.write(r"\textbf{Move: }\begin{mbmove}")
        return

    def end_mbmove(self, mbmove):
        self.latex_file.write("\\end{mbmove}")
        return

    def start_mbinitiativebonus(self, mbresolve):
        self.latex_file.write(r"\textbf{Initiative Bonus: }\begin{mbinitiativebonus}")
        return
    def end_mbinitiativebonus(self, mbresolve):
        self.latex_file.write("\\end{mbinitiativebonus}\\vspace{0.1cm}\\break{}")
        return
    
    def start_mbmagic(self, mbmagic):
        self.latex_file.write(r"\textbf{Magic Pool: }\begin{mbmagic}")
        return
    def end_mbmagic(self, mbmagic):
        self.latex_file.write("\\end{mbmagic}\\vspace{0.1cm}\\break{}")
        return
    
    def start_mbresolve(self, mbresolve):
        self.latex_file.write(r"\textbf{Resolve Pool: }\begin{mbresolve}")
        return
    def end_mbresolve(self, mbresolve):
        self.latex_file.write("\\end{mbresolve}")        
        return
    
    def start_mbstr(self, mbstr):
        self.latex_file.write(
            "% attribute block\n" 
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
        self.latex_file.write("\\end{small} & %\n")
        return

    def start_mbend(self, mbend):
        self.latex_file.write("\\begin{small}")
        return
    def end_mbend(self, mbend):
        self.latex_file.write("\\end{small} & %\n")
        return

    def start_mbag(self, mbag):
        self.latex_file.write("\\begin{small}")
        return
    def end_mbag(self, mbag):
        self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbspd(self, mbspd):
        self.latex_file.write("\\begin{small}")
        return
    def end_mbspd(self, mbspd):
        self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbluck(self, mbluck):
        self.latex_file.write("\\begin{small}")
        return
    def end_mbluck(self, mbluck):
        self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbwil(self, mbwil):
        self.latex_file.write("\\begin{small}")
        return
    def end_mbwil(self, mbwil):
        self.latex_file.write("\\end{small} & %\n")
        return
    
    def start_mbper(self, mbper):
        self.latex_file.write("\\begin{small}")
        return
    def end_mbper(self, mbper):
        self.latex_file.write("\\end{small}"
                              "\\end{tabular}"
                              "\n")
        return
    
    def start_mbabilities(self, mbabilities):
        #self.latex_file.write(r"\textbf{Abilities}: ")
        return
    def end_mbabilities(self, mbabilities):
        #self.latex_file.write("\n")
        return

    def start_mbaspects(self, mbaspects):
        self.latex_file.write(r"\textbf{Aspects:} ")
        return
    def end_mbaspects(self, mbaspects):
        self.latex_file.write("\\\\\n")
        return
    
    def start_mbdescription(self, mbdescription):
        self.latex_file.write(r"\vspace{1.0mm}"
                              r"\textbf{Description:}"
                              r"\hfill"
                              r"\break"
                              r"\vspace{-0.3cm}")
        return
    def end_mbdescription(self, mbdescription):
        self.latex_file.write("\n")
        return
    
    def start_mbnpc(self, mbnpc):
        return
    def end_mbnpc(self, mbnpc):
        self.latex_file.write("\\newline{}")
        return

    def start_npcname(self, npcname):
        self.latex_file.write(r"\textbf{Name: }\begin{npcname}")
        return
    def end_npcname(self, npcname):
        self.latex_file.write("\\end{npcname} ")
        return
    
    def start_npchps(self, npchps):
        self.latex_file.write(r"\textbf{HPs: }\begin{npchp}")
        return
    def end_npchps(self, npchps):
        self.latex_file.write("\\end{npchp}")
        return


    #
    #
    #
