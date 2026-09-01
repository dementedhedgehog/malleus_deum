# -*- coding: utf-8 -*-
from os.path import join, splitext, exists
import sys
import copy
import io
import re
import config
import typing
from utils import (
    normalize_ws,
    convert_str_to_bool,
    convert_str_to_int,
    convert_str_to_float,
    get_error_context,
    is_comment,
    attrib_is_true,
    node_to_string,
    get_child_name,
    get_text_for_child,
    get_child,
    build_dir,
)
import utils

from npcs import NPC, NPCGroup
import abilities
import utils
from db import DB

# Regex to find the boundary between non-digits and digits at the end
# of <sv13/> type elements.
_sv_regex = re.compile(r'(\d+)$')


latex_frontmatter = r"""

%%
%% Magic to make transparency work with Xelatex.
%%
\RequirePackage{pdfmanagement-testphase}
\DeclareDocumentMetadata{}

%%
%% Doc Class
%%
\documentclass[%s,twocolumn,twoside]{book}

%% Lots of error context
\setcounter{errorcontextlines}{999}

\usepackage{adjustbox}             %% better control over frames
\usepackage{amsthm}                %% nice theorem environments
\usepackage[unicode]{hyperref}     %% for hyperlinks in pdf
\usepackage{bookmark}              %% fixes a hyperref warning.
\usepackage{booktabs}              %% for tables
\usepackage{calc}                  %% for table width calculations
\usepackage{caption}               %% extra captions
\usepackage{ccicons}               %% for creative commons icons
\usepackage{color}                 %% color.. what can I say
\usepackage{xcolor}                %% for color aliases    
\usepackage[table]{xcolor}         %% colour for tables
\usepackage{enumitem}              %% customize enumerations, lists etc
\usepackage{environ}               %% converts latex commands into environments
\usepackage{fail-fast}             %% fail on warnings
\usepackage{fancyhdr}              %% header control
\usepackage{fancybox}              %% fancy boxes.. eg box outs
\usepackage{float}                 %% for float[H]
\usepackage{fontspec}              %% fine font control
\usepackage{graphicx}              %% for including images
\usepackage[none]{hyphenat}        %% Don't break words (no hyphenation).
\usepackage{lettrine}              %% for drop capitals
\usepackage{lipsum}                %% for generating debug text
\usepackage{makeidx}               %% for building the index
\usepackage{multirow}              %% for table data with multiple rows
\usepackage{niceframe}             %% fancy boxes around text
\usepackage{parskip}               %% non indented paragraphs
\usepackage{pgfornament}           %% for the page dividers
\usepackage{quoting}               %% more configurable quoting environment.
\usepackage{amssymb}               %% for special maths symbols, eg slanted geq
\usepackage{rotating}              %% for sidewaystable
\usepackage{tabularx}              %% for tables
\usepackage{tcolorbox}             %% color boxes
\tcbuselibrary{skins}              %% more color box stuff
\usepackage[raggedright]{titlesec} %% avoid hyphenating titles
\usepackage{unicode-math}
\usepackage{wrapfig}               %% figures with text wrapping.
\usepackage{xtab}                  %% for multipage tables
\usepackage{transparent}           %% for transparent backgrounds

%% TESTING
\usepackage{changepage}


%% more floats (side-step a build error)
\usepackage[maxfloats=256]{morefloats}
\maxdeadcycles=1000

%% include subsubsections in the table of contents
\setcounter{tocdepth}{3}

%% allow \paragraph{X} as a subsubsubsection "title".
\setcounter{secnumdepth}{3}

%% Ability header format
\newcommand{\ability}[1]{\subsubsection{#1}\vspace{-1.8ex}}

%% Principle and Corollary environments
%% (for the Rationale doc.. don't use these in player facing docs)
%% Redefine the corollary/principle style to not put parentheses around the title.
\newtheoremstyle{customtheoremstyle}%%
  {.5\baselineskip}%%           Space above
  {.5\baselineskip}%%           Space below
  {\itshape}%%                  Body font
  {0pt}%%                       Indent amount
  {\bfseries}%%                 Theorem header font
  {}%%                          Punctuation after theorem head
  {\newline}%%                  Space after theorem head, ' ', or \newline
  {\thmname{#1}\thmnumber{ #2}.\thmnote{ #3}}%% Theorem head spec 
\theoremstyle{customtheoremstyle}
\newtheorem{principle}{Principle}
\newtheorem{corollary}{Corollary}

%%
%% Colours
%%
\definecolor{black}{RGB}{0,0,0}
\definecolor{maroon}{RGB}{128,0,0}
\definecolor{darkred}{RGB}{139,0,0}
\definecolor{barnred}{RGB}{124,10,2}
\definecolor{rosetaupe}{RGB}{144,93,93}
\definecolor{rosewood}{RGB}{101,0,11}
\definecolor{blackbean}{RGB}{61,12,2}
\definecolor{paleparchment}{RGB}{253,250,241}
\definecolor{tan}{cmyk}{0,0.14,0.33,0.18}
%%\definecolor{champagne}{cmyk}{0,0.06,0.17,0.03}
\definecolor{champagne}{RGB}{247,231,206}


%%
%% Colour Aliases
%%
\colorlet{rpgtitlefontcolor}{black}
\colorlet{chapterfontcolor}{black}
\colorlet{rpgsectionfontcolor}{rosewood}
\colorlet{monstertitlecolor}{rosewood}
\colorlet{monstertagscolor}{black}
\colorlet{pagecolor}{paleparchment}
\colorlet{dropcapcolor}{darkred}
\colorlet{dropcapbodycolor}{rosewood}
\colorlet{keywordcolor}{blackbean}
\colorlet{defncolor}{blackbean}
\colorlet{hyperlinkcolor}{tan}
\colorlet{emphcolor}{darkred}
\colorlet{pagecolor}{paleparchment}

%%
%% Page Color
%%
\pagecolor{pagecolor}

%%
%% Page Background
%%

%%\newcommand{\getpagebackground}{
%%\transparent{0.2}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/anon_elder_sign/anon_elder_sign.png}
%%}

\newcounter{modpagenumber}
\setcounter{modpagenumber}{0}

\AddToHook{shipout/background}{%%



\ifodd\value{page}\relax
    \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_border_lhs_1/page_border_lhs_1.png}}
\else
    \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_border_rhs_1/page_border_rhs_1.png}}
\fi


  \stepcounter{modpagenumber}

\ifnum\value{modpagenumber}=1\relax
  \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_background_1/page_background_1.png}}
  \fi

\ifnum\value{modpagenumber}=2\relax
  \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_background_2/page_background_2.png}}
  \fi

  \ifnum\value{modpagenumber}=3\relax
  \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_background_3/page_background_3.png}}
  \fi

  \ifnum\value{modpagenumber}=4\relax
  \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_background_4/page_background_4.png}}
  \fi

  \ifnum\value{modpagenumber}=5\relax
  \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_background_5/page_background_5.png}}
  \fi

  \ifnum\value{modpagenumber}=6\relax
  \put (0pt,-\paperheight) {\transparent{0.1}\includegraphics[width=\paperwidth,height=\paperheight]{./resources/page_background_6/page_background_6.png}}
  \fi


  \ifnum\value{modpagenumber}>5\relax
     \setcounter{modpagenumber}{0}
  \fi
}




%%
%% Fonts
%%
\newfontfamily{\cloisterblack}[Path=fonts/]{CloisterBlack}
\newfontfamily{\dogma}[Path=fonts/]{Dogma}
\newfontfamily{\becker}[Path=fonts/]{Becker-ZVrz}
%%\newfontfamily{\amelies}[Path=fonts/]{Amelies}
\newfontfamily{\isabella}[Path=fonts/, Scale=1.1]{Isabella}
\newfontfamily{\germania}[Path=fonts/]{GermaniaVersalien}
\newfontfamily{\carrickc}[Path=fonts/]{CarrickCaps}
\newfontfamily{\libertine}{Linux Libertine O}
\newfontfamily{\caudex}[Path=fonts/, Scale=1.1]{Caudex-Regular}
%%\newfontfamily{\becker}[Path=fonts/]{Becker Regular}

%% the font for the body of the text
\setmainfont[
  %%Scale=0.95,
  Path = ./fonts/Caudex/,
  UprightFont = {*-Regular},
  BoldFont = {*-Bold},
  BoldItalicFont = {*-BoldItalic},
  ItalicFont = {*-Italic},
  Extension = {.ttf}
]{Caudex}

%%
%% Font Aliases
%%
\newcommand{\quotefont}{\isabella}
\newcommand{\epigraphfont}{\libertine}
\newcommand{\dropcapfont}{\carrickc}
\newcommand{\chapterfont}{\cloisterblack}
\newcommand{\rpgtitlefont}{\dogma}
\newcommand{\rpgtitlesubtitlefont}{\cloisterblack}
\newcommand{\rpgtitleauthorfont}{\dogma}
\newcommand{\versionfont}{\dogma}
\newcommand{\rpgsectionfont}{\cloisterblack}
\newcommand{\attributionfont}{\germania}
\newcommand{\indexlettergroupfont}{\cloisterblack}
\newcommand{\sidebartitlefont}{\cloisterblack} 
\newcommand{\sidebarfont}{\normalfont}





%%
%% Dropcaps
%%
\newcommand{\mddropcap}[2]{%%
\lettrine[%%
 lines=3, %%
 loversize=0.2, %%
 slope=0em]%%
{\dropcapfont\color{dropcapcolor}#1}{\color{dropcapbodycolor}#2}}


%% Arrows with bars, e.g. ↧ and ↥
%% (for use in tables to denote entry for multiple rows)
\setmathfont{TeX Gyre Pagella Math}
\newcommand{\downarrowfrombar}{\ensuremath{\mapsdown}} 
\newcommand{\uparrowfrombar}{\ensuremath{\mapsup}}


%% Custom Environment For Ability Checks
%%\newenvironment{mdindent}{%%
%%\vspace{-0.7em}%%
%%\list{}{\rightmargin0.3cm \leftmargin0.3cm}%%
%%\item\relax}%%
%%{\endlist}

%%\newenvironment{mdindent}{%%
%%  \vspace*{-\baselineskip}
%%  %% Avoid inserting vertical space when we start an indent
%%  %%\setlength{\topsep}{0pt}%%
%%  %%\setlength{\partopsep}{0pt}%%
%%  %%\setlength{\parsep}{\parskip}%%
%%  %%\setlength{\itemsep}{0pt}%%
%%  a\begin{adjustwidth}{0.3cm}{}b%%
%%}{%%
%%  \end{adjustwidth}%%
%%}



%%\newenvironment{mdindent}{%%
%%  \addtolength{\leftskip}{0.3cm}%%
%%}{%%
%%  \addtolength{\leftskip}{-0.3cm}%%
%%}

%%\newenvironment{mdindent}{%%
%%  \addtolength{\leftskip}{0.3cm}%%
%%}{%%
%%  \addtolength{\leftskip}{-0.3cm}%%
%%}


%%n\ifvmode\else\vspace{-\parskip}\fi{}m%%
%%\leavevmode
%%\vspace{-1\parskip}p%%


%% Custom indent environment
%% Inserts no vertical space and is nestable.
\newenvironment{mdindent}{%%
\vspace{-1\parskip}%%
\begin{adjustwidth}{0.3cm}{\rightskip}%%
}{%%
\end{adjustwidth}%%
\vspace{-1\parskip}%%
}


%% Custon Bold Environment
\newenvironment{mdbold}{\bfseries}{}

%% Custom Quote Environment
\newenvironment{mdquote}{%%
\setlength{\parskip}{1.9\parskip}%%
\raggedright%%
\list{}{\rightmargin0.3cm \leftmargin0.3cm}%%
\item\relax\begin{itshape}\quotefont\large}%%
{\end{itshape}\endlist\vspace{1cm}}

%% Custom Epigraph Environment
\newenvironment{mdepigraph}{%%
\setlength{\parskip}{0.3\parskip}%%
\raggedright%%
\list{}{\rightmargin0.2cm \leftmargin0.2cm}%%
\item\relax\begin{small}\begin{em}\epigraphfont}%%
{\end{em}\end{small}\endlist\vspace{0.1cm}}


%% spacing
%% drop is a vspace 1/100th the page text height.
\newlength\drop
\drop = 0.01\textheight

%% Caption Spacing (spacing around table/figure captions)
\setlength{\abovecaptionskip}{2ex}

%% Use a page style that shows chapter headings at the top of the page.
\pagestyle{headings}

\titleformat{name=\chapter}[hang]
{\raggedright\Huge\bfseries\chapterfont\color{chapterfontcolor}}
{}{1em}{}

\titleformat{\section}
{\rpgsectionfont\LARGE\color{rpgsectionfontcolor}}
{\thesection}{0.5em}{}

\newcommand\rpgtablesection[1]{
\rule{0pt}{1ex}\bfseries\scriptsize #1}
            
\newenvironment{smaller}{\begin{footnotesize}}{\end{footnotesize}}

%%
%% Definition
%%
\newenvironment{defn}{\bfseries\color{defncolor}}{}


%% start other evironments in newenvironments like this 
%% put it after a section, not just before

\newenvironment{playexample}
{\begin{list}{}%%
%% before
{\setlength\topsep{\dimexpr0.5cm-\parskip-\partopsep}
\setlength\listparindent{0cm}
\setlength\labelwidth{0cm}
\setlength\itemindent{0em}
\setlength\parsep{\baselineskip}
\setlength\leftmargin{1em}
\setlength\rightmargin{1em}
\setlength\labelsep{1cm}
}\item \em\parindent0pt
}
%% after
{\end{list}\vspace{0.0cm}}


%% Try not to break paragraphs too much
\widowpenalties 1 1000
\raggedbottom

%%
%% Hyperlinks
%%
%%\hypersetup{%%
%%  colorlinks=false, %%            hyperlinks will be black
%%  linkbordercolor=blue, %%        hyperlink border colour
%% pdfborderstyle={/S/U/W 1} %%     border style will be underline of width 1pt
%%}
\hypersetup{%%
  colorlinks=false, %%               hyperlinks will be black
  linkbordercolor=hyperlinkcolor, %% hyperlink border colour
  pdfborderstyle={/S/U/W 1} %%       border style will be underline of width 1pt
}

%% Archetype table formatting
\newcommand\achetypenameformat[1]{\begingroup\scriptsize#1\endgroup}


%%
%% Table formatting.
%%
%% More space between table columns
\setlength{\tabcolsep}{11pt}
%% Save the tabcolsep
\newlength{\originaltabcolsep}
\setlength{\originaltabcolsep}{\tabcolsep}
%% Space between rows
\setlength{\extrarowheight}{2pt}
%% Header background color (tan)
%%\definecolor{tableheadercolor}{cmyk}{0,0.14,0.33,0.18}
\colorlet{tableheadercolor}{tan}
%% Every second row color (champagne)
%%\definecolor{tableoddrowcolor}{cmyk}{0,0.06,0.17,0.03}
\colorlet{tableoddrowcolor}{champagne}

%%
%% Sidebar Formatting
%%
\colorlet{sidebarcolor}{champagne}
\colorlet{sidebarboxcolor}{black}
\newsavebox{\sidebarbox}

%% \newenvironment{mdsidebar}{%%
%% \begin{figure}[t]%%
%% \colorbox{sidebarcolor}{%%
%% \begin{lrbox}{\sidebarbox}%%
%% \begin{minipage}{0.95\linewidth}%%
%% }%%
%% {%%
%% \end{minipage}%%
%% \end{lrbox}\fbox{\usebox{\sidebarbox}}%%
%% }%%
%% \end{figure}%%
%% }

%%
%% Use this length instead of \textheight to calculate the height for scaling
%% images and such (\textheight doesn't take into account the height of chapter
%% titles and the like.. i.e. the textheight on a chapter title page is the same
%% as that on a page with a block of text.  So images scaled to this value are
%% too tall).
%%
%% \newlength{\availabletextheight}

%% %% Call this to set \availabletextheight
%% \newcommand{\resetavailabletextheight}{%%
%% \setlength{\availabletextheight}{\textheight}}

%% \newcommand{\updateavailabletextheight}{%%
%% \setlength{\availabletextheight}{\dimexpr \pagegoal-\pagetotal}}

%% \AddToHook{shipout/after}{\resetavailabletextheight{}}

%%
%% Create custom environments from commands.
%% We do this because the \begin and \end semantics of environments map nicely
%% onto xmls begin  <x> and end </x> elements than fiddling with latex commands
%% like \bold{text}; for example.
%%
%% NewEnviron eats trailing whitespace!! 
%%
\NewEnviron{chaptertitle}{\chapter{\BODY}}
\NewEnviron{mdemph}{\emph{\color{emphcolor}\BODY}}


%%
%% Custom Symbols
%%

%% Declares a new length variable named \mycustomlength
\newlength{\symbolsize}
\setlength{\symbolsize}{0.8em}

\newlength{\largesymbolsize}
\setlength{\largesymbolsize}{0.9em}

\newlength{\symbolverticaloffset}
\setlength{\symbolverticaloffset}{-0.2em}

\newlength{\symbolhorizontalspace}
\setlength{\symbolhorizontalspace}{0.3ex}


%% Ability Bullet
\newcommand\abilitybullet{%%
\includegraphics[width=\symbolsize,height=\symbolsize]%%
{./resources/anon_elder_sign/anon_elder_sign.png}}

%% Check Symbol
\newcommand\checksymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[width=\largesymbolsize,height=\largesymbolsize]%%
{./resources/symbol_check/symbol_check.png}%%
\hspace{\symbolhorizontalspace}}}

%% Counter Check Symbol
\newcommand\counterchecksymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[width=\largesymbolsize,height=\largesymbolsize]%%
{./resources/symbol_counter_check/symbol_counter_check.png}%%
\hspace{\symbolhorizontalspace}}}

%% Auxiliary Check Symbol
\newcommand\auxiliarychecksymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[width=\largesymbolsize,height=\largesymbolsize]%%
{./resources/symbol_auxiliary/symbol_auxiliary.png}%%
\hspace{\symbolhorizontalspace}}}

%% Antag Check Symbol
\newcommand\antagonistsymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[width=\symbolsize,height=\symbolsize]%%
{./resources/symbol_antagonist/symbol_antagonist.png}%%
\hspace{\symbolhorizontalspace}}}

%% Fate Die Symbol
\newcommand\fatediesymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[width=\symbolsize,height=\symbolsize]%%
{./resources/symbol_fate_die/symbol_fate_die.png}}}

%% No Fate Die Symbol
\newcommand\nofatediesymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[width=\symbolsize,height=\symbolsize]%%
{./resources/symbol_no_fate_die/symbol_no_fate_die.png}}}

%% Skill Die Symbol
\newcommand\skilldiesymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[width=\symbolsize,height=\symbolsize]%%
{./resources/symbol_skill_die/symbol_skill_die.png}}}




%%
%% Monsters Block Formatting.
%%
\newcommand\mbsep{\hrule\hfill\break}

\newenvironment{mbattr}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbtitle}%%
%% {\sherwood\color{monstertitlecolor}\begin{large}}%%
{\dogma\color{monstertitlecolor}\begin{large}}%%
{\end{large}\vspace{0.0cm}\hfill}

\newenvironment{mbtags}%%
{\color{monstertagscolor}\begin{normalsize}}%%
{\end{normalsize}\\[-0.42cm]}

\newenvironment{mbdefence}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbmove}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbhp}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbmettle}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbluck}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbinitiative}
{\color{monstertitlecolor}\normalsize}{}

\newenvironment{mbmagic}
{\color{monstertitlecolor}\normalsize}{}

\newenvironment{npcname}
{\color{monstertitlecolor}\normalsize}{}

\newenvironment{npchp}
{\color{monstertitlecolor}\normalsize}{}

\newcommand\mbattrtitleformat[1]{\normalsize\textbf{#1}}


%%
%% Index
%%

%% for glossary like definitions in the index.
\renewcommand*{\alsoname}{}
\def\igobble#1 {}

%% Make the hangindent for multiline index
%% entries (glossary type entries) smaller.
\makeatletter
\def\@idxitem{\par\hangindent 1em}
\makeatother

%% Tell xelatex to create the index
\makeindex


%%
%% Start the document!
%%
\begin{document}

%% Relax Latex formatting rules
\sloppy

%% Print some page info
\typeout{ --- Page Info ---}
\typeout{    Line Width: \linewidth}
\typeout{    Text Height: \textheight}
\typeout{}

"""    

def sanitize_index_text(txt):
    """
    Indicies have a few special characters that need to be escaped.

    """
    if txt is None:
        return None

    # Remove leading and trailing whitespace and any other duplicate
    # inter-string spaces.
    txt = txt.strip()
    txt = " ".join(txt.split())
    
    # ! is used to separate entries from subentries in indexentries.
    # double quote is the escape char for indicies :|
    txt = txt.replace("!", "\"!")
    return txt


class TableState:
    """
    There's only ever zero or one table at a time when formatting.
    We do have to remember its state while we're formatting it however.

    """
    def __init__(self):
        # This is a label for makeindex.
        self.label = None

        # list of (index entry / sub entry)
        self.index_entries = []

        # number of columns in the table.
        self.number_of_columns = 0
        self.current_column = 0
        self.current_row = 0

        # Some flags that determine table layout.
        self.figure = False
        self.fullwidth = False
        self.sideways = False

        # array that maps from column number to percent of text width.
        self.column_percent_widths = []

    def get_columns_percent_width(self, n_columns):
        """
        Get the widths of some number of columns including the col seps
        between them.  This is really shit (can't use X cols) but I'm
        not sure how to improve it.

        """
        from_column = self.current_column
        to_column = min(self.number_of_columns, self.current_column+n_columns)
        return sum(self.column_percent_widths[from_column:to_column])

    def parse_category(self, table):
        """
        Parse the optional first element of the table, one of
        <standardtable/>, <figuretable/>,  <fullwidthtable/>,
        <sidewaystable/>.

        """
        if get_child(table, "fullwidthtable") is not None:
            self.figure = True
            self.fullwidth = True
        elif get_child(table, "figuretable") is not None:
            self.figure = True
        elif get_child(table, "sidewaystable") is not None:
            self.figure = True
            self.fullwidth =  True
            self.sideways = True
        elif get_child(table, "standardtable") is not None:            
            pass # the default
        else:
            # fallback to default.  We don't need to specify this!
            pass
        return


class IndexEntry:
    """
    Information

    """

    def __init__(self):
        #self.text = None
        self.entry = None
        self.subentries = []
        self.sees = []
        self.definitions = []
    

    def __str__(self):
        str_rep = "Index Entry\n"
        str_rep += f"entry: %s\n" % self.entry
        str_rep += "subentries\n"
        for sub in self.subentries:
            str_rep += f"  %s\n" % sub
        str_rep += "sees\n"
        for see in self.sees:
            str_rep += f"  %s\n" % see
        str_rep += "definitions\n"
        for defn in self.definitions:
            str_rep += f"  %s\n" % defn
        return str_rep
        
           
class DocFormatter:
    """
    Logic common to all doc formatters.

    """

    def no_op(self, obj):
        """
        We've got a lot of handlers that don't need to do anything..
        do nothing once.
        """
        pass
        
    def start_measurement(self, distance):
        if config.use_imperial:
            distance_text = get_text_for_child(distance, "imperial")
            if distance_text is None:
                raise Exception("Imperial distance not specified!")

        else:
            distance_text = get_text_for_child(distance, "metric")
            if distance_text is None:
                raise Exception("Metric distance not specified!")

        self.buffer.write(normalize_ws(distance_text).strip())
        return
    end_measurement = no_op
    

    
class LatexFormatter(DocFormatter):
    """
    The class that takes a doc and writes a .tex file.

    """
    
    def __init__(
            self,
            latex_file: typing.TextIO,
            db: typing.Type[DB],
            xml_fname: str):
        super().__init__()

        # Stack of file pointers.
        #
        # The problem we're solving here is that latex requires a
        # sometimes-strange ordering of elements that we don't want to have to
        # replicate in the xml structure (because it will make formatting html
        # and other formats difficult).  So the formatter writes to the stream
        # on the top of the following stack.  If we want to parse the xml in a
        # latex order we can push a StringIO buffer onto this stack and then
        # grab the string from that buffer and insert it in a less latexy
        # position later on.
        #
        # E.g. this is useful for moveable arguments.. section headers etc.
        #
        self.files= [latex_file, ]

        # the xml source document we're building
        self.xml_fname = xml_fname
        
        # for equations (indent second and subsequent lines)
        self._equation_first_line = True

        # Should description terms start on a newline?
        self.terms_on_new_line = False  # FIXME: IGNORED?

        # current index entry state.
        self.index_entry = None

        # keep track of state for npc blocks
        self._in_npc_group = False

        # game db
        self.db = db

        # current table state
        self.table = None        
        return

    # Shorthand
    no_op = DocFormatter.no_op

    def write(self, *args, **kwargs):
        self.buffer.write(*args, **kwargs)
        return
        
    def writeln(self, *args, **kwargs):
        self.buffer.write(*args, **kwargs)
        self.buffer.write("\n")
        return

    def debug_dump_buffers(self):
        str_rep = "Debug Dump Buffers\n"
        indent = ""
        for i, b in enumerate(self.buffers):
            str_rep += f"{indent}{i:5} {b[:20]} \n"
            str_rep += f"{indent}      {b[-20:]} \n"
        return str_rep
            
    def push_buffer(self):
        self.files.append(io.StringIO())

    def get_buffer_str(self, strip=False, peek=False):
        str_rep = self.files[-1].getvalue()
        if strip:
            str_rep = str_rep.strip()
        if not peek:
            self.files[-1].close()
            self.files.pop()
        return str_rep
    
    @property
    def buffer(self):
        return self.files[-1]    

    def verify(self):
        verifyObject(IFormatter, self)
        return

    def _get_img_filename(self, img):
        """
        We use this in two places so whack it here to avoid
        duplicating code.

        """
        # Either it's an image we build or it's one from the resource db
        if "buildfname" in img.attrib:
            build_fname = img.get("buildfname")
            filename = join(build_dir, build_fname)

        elif "id" in img.attrib:
            resource_id = img.get("id")
            try:
                resource = self.db.resources.use(
                    resource_id, self.xml_fname)
            except KeyError:
                raise Exception(f"Image {resource_id} does not exist!")
            filename = resource.get_fname()
            # self.buffer.write("\\addcontentsline{loa}{section}{%s}"
            #                       % resource.get_contents_desc())
        else:
            raise Exception("Image missing source or id!")

        if not exists(filename):
            raise Exception("Image does not exist: %s" % filename)        
        return filename

    def start_book(self, book):        
        # must be a valid latex paper size
        if config.paper_size == "a4":
            paper_size = "a4paper"
        elif config.paper_size == "letter":
            paper_size = "letterpaper"
        else:
            raise Exception("Unknown paper size.  "
                            "Pick one of [a4, letter] in config.py")
        orientation = ""
        landscape = attrib_is_true(book, "landscape")
        formatting = paper_size + orientation
        self.buffer.write(latex_frontmatter % formatting)

        if config.display_page_background:
            self.buffer.write(
                "\n"
                "% use a background image\n"
                "\\CenterWallPaper{1.0}"
                "{./resources/paper_" + paper_size + ".jpg}"
                "\n\n")
        return

    def end_book(self, book):
        self.buffer.write("\\end{document}\n")        
        return

    def start_appendix(self, appendix):
        self.buffer.write("\\appendix\n"
                          "\\addcontentsline{toc}{chapter}{APPENDICES}\n")
        return
    end_appendix = no_op

    def handle_keyword(self, keyword):
        self.buffer.write("{\\color{keywordcolor} \\textbf{%s}}" % keyword)
        return

    def start_daggersymbol(self, symbol):
        self.buffer.write("\\textsuperscript{\\dag}")
        return
    end_daggersymbol = no_op    

    def start_doubledaggersymbol(self, symbol):
        self.buffer.write("\\textsuperscript{\\ddag}")
        return
    end_doubledaggersymbol = no_op    

    def start_downarrowfrombar(self, symbol):
        self.buffer.write("\\downarrowfrombar ")
        return
    end_downarrowfrombar = no_op    

    def start_uparrowfrombar(self, symbol):
        self.buffer.write("\\uparrowfrombar ")
        return
    end_uparrowfrombar = no_op    

    def start_abilitybullet(self, symbol):
        self.buffer.write(r"\abilitybullet ")
    end_abilitybullet = no_op    

    def start_checksymbol(self, symbol):
        self.buffer.write(r"\checksymbol ")
    end_checksymbol = no_op    

    def start_counterchecksymbol(self, symbol):
        self.buffer.write(r"\counterchecksymbol ")
    end_counterchecksymbol = no_op    

    def start_auxiliarysymbol(self, symbol):
        self.buffer.write(r"\auxiliarychecksymbol ")
        return
    end_auxiliarysymbol = no_op    

    def start_antagonistsymbol(self, symbol):
        self.buffer.write(r"\antagonistsymbol ")
        return
    end_antagonistsymbol = no_op    

    def start_fatediesymbol(self, symbol):
        self.buffer.write(r"\fatediesymbol ")
        return
    end_fatediesymbol = no_op    

    def start_nofatediesymbol(self, symbol):
        self.buffer.write(r"\nofatediesymbol ")
        return
    end_nofatediesymbol = no_op    

    def start_skilldiesymbol(self, symbol):
        self.buffer.write(r"\skilldiesymbol ")
        return
    end_skilldiesymbol = no_op    

    #
    # Corollaries
    #
    def start_corollary(self, symbol):
        self.buffer.write(r"\begin{corollary}")
        return
    
    def end_corollary(self, symbol):
        self.buffer.write(r"\end{corollary}")
        return

    def start_corollary(self, symbol):
        self.buffer.write(r"\begin{corollary}")
        return

    def start_corollarytitle(self, symbol):
        self.buffer.write("[")
        return
    
    def end_corollarytitle(self, symbol):
        self.buffer.write("]")
        return
    
    start_corollarybody = no_op
    end_corollarybody = no_op
    
    def end_corollary(self, symbol):
        self.buffer.write(r"\end{corollary}")
        return

    #
    # Principles
    #
    start_principlebody = no_op
    end_principlebody = no_op

    def start_principle(self, symbol):
        self.buffer.write(r"\begin{principle}")
        return
    
    def end_principle(self, symbol):
        self.buffer.write(r"\end{principle}")
        return    

    def start_principletitle(self, symbol):
        self.buffer.write("[")
        return
    
    def end_principletitle(self, symbol):
        self.buffer.write("]")
        return
        
    def start_arrowleft(self, symbol):
        self.buffer.write("\\arrowleft{}")
        return
    end_arrowleft = no_op    

    start_ability_title = no_op
    end_ability_title = no_op

    def start_ability_id(self, ability_id):        
        self.buffer.write("ID: %s\\\n" % ability_id) 
        return
    end_ability_id = no_op

    start_ability_group = no_op
    def end_ability_group(self, ability_group):
        self.buffer.write("%s\n" % normalize_ws(ability_group.text))
        return

    start_ability_class = no_op
    def end_ability_class(self, ability_class):
        self.buffer.write("%s\n" % normalize_ws(ability_class.text))
        return

    start_action_points = no_op
    def end_action_points(self, action_points):
        self.buffer.write("%s\n" % normalize_ws(action_points.text))
        return

    def start_hlink(self, hlink):
        url = hlink.get("url")
        text = utils.contents_to_string(hlink)
        self.buffer.write(r"\href{%s}{%s}" % (url, text))
        return
    end_hlink = no_op
    
    
    def start_ampersand(self, and_element):
        self.buffer.write("\\&")
        return
    end_ampersand = no_op

    def start_copyright(self, _):
        self.buffer.write(r"\copyright{}")
        return
    end_copyright = no_op

    def start_ccby(self, _):
        self.buffer.write(r"\ccby{}")
        return
    end_ccby = no_op

    def start_lore(self, element):
        self.buffer.write("\\lore{}")
        return    
    end_lore = no_op

    def start_martial(self, element):
        self.buffer.write("\\martial{}")
        return    
    end_martial = no_op

    def start_percent(self, element):
        self.buffer.write("\\%")
        return    
    end_percent = no_op

    def start_general(self, element):
        self.buffer.write("\\general{}")
        return    
    end_general = no_op

    def start_magical(self, element):
        self.buffer.write("\\magical{}")
        return    
    end_magical = no_op

    def start_geqqsymbol(self, geqq_element):
        self.buffer.write(r"$\stackrel{\scriptscriptstyle ?}{\geq}{}$")
        return
    end_geqqsymbol = no_op

    def start_leqqsymbol(self, geqq_element):
        self.buffer.write(r"$\stackrel{\scriptscriptstyle ?}{\leq}{}$")
        return
    end_leqqsymbol = no_op

    def start_leqsymbol(self, leq_element):
        self.buffer.write(r"$\leq$")
        return
    end_leqsymbol = no_op

    def start_ltsymbol(self, leq_element):
        self.buffer.write("$<$")
        return
    end_ltsymbol = no_op

    def start_gtsymbol(self, leq_element):
        self.buffer.write("$>$")
        return
    end_gtsymbol = no_op

    def start_geqsymbol(self, geq_element):
        self.buffer.write(r"$\geq$")
        return
    end_geqsymbol = no_op

    def start_br(self, br):
        length = br.attrib.get("length")
        self.buffer.write(r"\ifvmode\else\newline\fi{}")
        # if length:
        #     assert float(length)
        #     #     self.buffer.write(r" \\ ")
        #     self.buffer.write(r"\ifvmode\else\\[%s\baselineskip]\fi{}" % length)
        # else:
        #     self.buffer.write(r"\ifvmode\else\\\fi{}")
        #     #     self.buffer.write(r" \\[%s\\baselineskip] " % length)
        return
    end_br = no_op

    def start_newpage(self, newpage):
        self.buffer.write(r"\ifvmode\else\newpage\fi{}")
        return
    end_newpage = no_op

    start_pageref = no_op
    def end_pageref(self, pageref):
        self.buffer.write("~\\pageref{%s}" % normalize_ws(pageref.text))
        return

    start_ref = no_op
    def end_ref(self, ref):
        self.buffer.write("~\\ref{%s}" % normalize_ws(ref.text))
        return
    
    def start_index(self, index):
        """Put the index in the document where the <index/> element occurs."""
        self.buffer.write("\\clearpage\n")               
        self.buffer.write("\\addcontentsline{toc}{chapter}{Index}\n")
        self.buffer.write("\\printindex\n")
        return
    end_index = no_op

    #
    # Section Definitions
    #
    start_section = no_op
    end_section = no_op

    def start_sectiontitle(self, section_title):
        self.push_buffer()
        self.buffer.write("\\section{")
        return

    def end_sectiontitle(self, section_title):
        stripped_term = self.get_buffer_str(strip=True)
        self.buffer.write(stripped_term)
        self.buffer.write("}\n")
        return
    

    start_subsection = no_op
    end_subsection = no_op
    def start_subsectiontitle(self, section_title):
        self.buffer.write("\\subsection{")
        return
    def end_subsectiontitle(self, section_title):
        self.buffer.write("}")
        return

    start_subsubsection = no_op
    end_subsubsection = no_op

    def start_subsubsectiontitle(self, section_title):
        self.buffer.write("\\subsubsection*{")
        return
    def end_subsubsectiontitle(self, section_title):
        self.buffer.write("}")
        return    

    start_subsubsubsection = no_op
    end_subsubsubsection = no_op

    def start_subsubsubsectiontitle(self, section_title):
        self.buffer.write("\\paragraph{")
        return
    def end_subsubsubsectiontitle(self, section_title):
        self.buffer.write("}")
        return    

    #
    #
    #

    start_archetypelevel = no_op
    end_archetypelevel = no_op
    
    def start_leveltitle(self, archetype_level_title):
        levelnumber = archetype_level_title.get("levelnumber", -1)        
        self.buffer.write("\\subsection{Level {%s}}" % levelnumber)
        return
    def end_leveltitle(self, archetype_level_title):
        return
    

    def start_playexample(self, playexample):
        self.buffer.write("\\begin{playexample}\n")
        return

    def end_playexample(self, playexample):
        self.buffer.write(playexample.text)                
        self.buffer.write("\\end{playexample}\n")        
        return

    start_level = no_op
    end_level = no_op

    def start_leveltitle(self, level_title):
        self.buffer.write("\\subsection*{")
        return
    def end_leveltitle(self, level_title):
        self.buffer.write("}")
        return

    def start_titlepage(self, chapter):
        self.buffer.write("\\begin{titlepage}\n"
                              "\\begin{center}\n")
        return

    def end_titlepage(self, chapter):
        self.buffer.write("\\end{center}\n"
                              "\\end{titlepage}\n")
        return

    def start_emph(self, emph):
        self.buffer.write(r"\begin{mdemph}")
        return

    def end_emph(self, emph):
        # latex environments eat trailing space. The trailing {} fixes this.
        self.buffer.write(r"\end{mdemph}{}")
        return


    # def start_dropcap(self, dropcap):
    #     if dropcap.text:
    #         words = dropcap.text.split()
    #         if len(words) > 0:
    #             first_word = words[0]
    #             if len(first_word) > 0:
    #                 first_letter = first_word[0]
    #                 other_letters = first_word[1:]
    #                 dropcap_word = (
    #                     r"\dropcap{%s}{%s} " % (first_letter, other_letters))
    #             words = [dropcap_word, ] + words[1:]
    #         self.buffer.write(" ".join(words))
    #     return

    # def end_dropcap(self, emph):
    #     # latex environments eat trailing space. The trailing {} fixes this.
    #     #self.buffer.write(r"\end{mdemph}{}")
    #     return

    def start_dropcap(self, dropcap):
        #self.buffer.write(r"\begin{mddropcapbody}")
        if dropcap.text:
            words = dropcap.text.split()
            if len(words) > 0:
                first_word = words[0]
                if len(first_word) > 0:
                    first_letter = first_word[0]
                    other_letters = first_word[1:]
                    dropcap_word = (
                        r"\mddropcap{%s}{%s} " % (first_letter, other_letters))
                words = [dropcap_word, ] + words[1:]
            self.buffer.write(" ".join(words))
        return

    def end_dropcap(self, emph):
        #self.buffer.write(r"\end{mddropcapbody}")
        #self.buffer.write(r"}")
        # latex environments eat trailing space. The trailing {} fixes this.
        #self.buffer.write(r"\end{mdemph}{}")
        return


    def start_equation(self, equation):
        self._equation_first_line = True
        self.buffer.write(
            "\\begin{tabbing}\n "
            "\\hspace*{0.5cm}\\= \\kill \\nopagebreak \n")
        return

    def end_equation(self, equation):
        self.buffer.write("\\end{tabbing}\\vspace{-0.5cm}\n ")
        return


    def start_line(self, line):
        """
        Start equation line.
        
        """
        if not self._equation_first_line:
            self.buffer.write("\\> ") 
        self._equation_first_line = False
        if line.text:
            self.buffer.write(" %s " % normalize_ws(line.text))
        return

    def end_line(self, line):
        self.buffer.write("\\\\\n ")
        return


    def start_bold(self, bold):
        self.buffer.write(r"\begin{mdbold}")
        return
    def end_bold(self, smaller):
        self.buffer.write(r"\end{mdbold}")
        return

    def start_smaller(self, smaller):
        # smaller text
        self.buffer.write(r"\begin{smaller}")
        # smaller vertical space in lists etc.
        self.buffer.write(r"\setlist{nosep}")        
        return
    
    def end_smaller(self, smaller):
        self.buffer.write(r"\end{smaller}")
        return

    def handle_text(self, text):
        if text is not None:
            self.buffer.write(text)
        return


    def start_indent(self, indent):
        self.buffer.write(r"\begin{mdindent}")        
    def end_indent(self, indent):
        self.buffer.write(r"\end{mdindent}")

    # def start_indent(self, indent):
    #     self.buffer.write(r"\begin{adjustwidth}{0.3cm}{}")        
    # def end_indent(self, indent):
    #     self.buffer.write(r"\end{adjustwidth}")

    #
    # A quote
    #
    def start_quote(self, quote):
        self.buffer.write(r"\begin{mdquote}")
        
    def end_quote(self, quote_entry):
        self.buffer.write(r"\end{mdquote}")

    #
    # Am epigraph
    #
    def start_epigraph(self, quote):
        self.buffer.write(r"\begin{mdepigraph}")
        
    def end_epigraph(self, quote_entry):
        self.buffer.write(r"\end{mdepigraph}")

    #
    # Index Entries
    #
    def start_indexentry(self, _):
        self.index_entry = IndexEntry()
        self.push_buffer()
        return
    
    def end_indexentry(self, _):
        self.index_entry.text = self.get_buffer_str(strip=True)
        assert self.index_entry.entry
        #print(self.index_entry.entry)

        
        if self.table:
            # If it's an index in a table then save the index info and
            # defer writing the index entry till the end of the table.
            #index_entry = copy.deepcopy(self.index_entry)
            #self.table.index_entries.append(index_entry)
            pass

            # FIXME
        else:
            self.write_index_entry(self.index_entry)

        # if self.index_entry.entry.startswith("Asanguinous"):
        #     print(index_entry)
        #     raise Exception()
            
        self.index_entry = None                                            
        return

    # index entry
    def start_entry(self, entry):
        self.push_buffer()
        
    def end_entry(self, entry):
        self.index_entry.entry = self.get_buffer_str(strip=True)

    # index subentry
    def start_subentry(self, index_subentry):
        self.push_buffer()
        
    def end_subentry(self, index_subentry):
        subentry = self.get_buffer_str(strip=True)
        self.index_entry.subentries.append(subentry)
        return    
        
    # index see
    def start_see (self, index_see):
        self.push_buffer()
        
    def end_see(self, index_see):
        see = self.get_buffer_str(strip=True)
        self.index_entry.sees.append(see)

    # index definition
    def start_indexdefn (self, index_defn):
        self.push_buffer()
        
    def end_indexdefn(self, index_defn):
        self.index_entry.definitions.append(self.get_buffer_str(strip=True))

    def write_index_entry(self, entry: IndexEntry):
        """
        Writes an index entry.  All the arguments are the string
        contents of the various index elements.

        """
        entry_str = sanitize_index_text(entry.entry)
        self.buffer.write(r"\index{%s}" % entry_str)

        for subentry in entry.subentries:        
            sanitized_subentry = sanitize_index_text(subentry)            
            subentry_str = (
                r"\index{%s!%s}"
                % (entry_str, sanitized_subentry))
            self.buffer.write(subentry_str)

        for see in entry.sees:                    
            sanitized_see = sanitize_index_text(see)
            see_str = r"\index{%s|see {%s}}" % (entry_str, sanitized_see)
            self.buffer.write(see_str)

        for defn in entry.definitions:                    
            sanitized_defn = sanitize_index_text(defn)
            defn_str = (
                r"\index{%s" 
                r"!aaaaaaaa@\empty \igobble |seealso {%s}}"
                #r"!aaaaaaaa@\empty \igobble |seealso{\hspace{-2ex}%s}}"
                % (entry_str, sanitized_defn))
            self.buffer.write(defn_str)

        return

    #
    #
    #
    
    # word definitions
    def start_defn(self, defn):
        self.buffer.write(r"\begin{defn}")
        return
    def end_defn(self, defn):
        self.buffer.write(r"\end{defn}")
        return

    # def start_measurement(self, distance):
    #     # FIXME this logic should move up into doc.py
    #     if config.use_imperial:
    #         distance_text = get_text_for_child(distance, "imperial")
    #         if distance_text is None:
    #             raise Exception("Imperial distance not specified!")

    #     else:
    #         distance_text = get_text_for_child(distance, "metric")
    #         if distance_text is None:
    #             raise Exception("Metric distance not specified!")

    #     self.buffer.write("{" + normalize_ws(distance_text).strip() + "}")
    #     return
    # end_measurement = no_op

    start_metric = no_op
    end_metric = no_op
    start_imperial = no_op
    end_imperial = no_op    
    
    def start_chapter(self, chapter):
        return

    def end_chapter(self, chapter):
        return

    def start_p(self, paragraph):
        """
        Start paragraph.

        """
        self.buffer.write("\n\n")

        # turn of paragraph indentation?
        no_indent = attrib_is_true(paragraph, "noindent")
        if no_indent:
            self.buffer.write("\\noindent ")                
        return

    def end_p(self, paragraph):
        self.buffer.write("\n\n")
        return

    def start_design(self, design):
        if config.print_design_notes:
            self.buffer.write("\n\n")
            self.buffer.write(design.text)        
        return

    def end_design(self, design):
        self.buffer.write("\n\n")
        return

    def start_provenance(self, provenance):
        self.buffer.write("\n\n")
        if config.print_provenence_notes:
            self.buffer.write("\\begin{center}")
            self.buffer.write(r"\\begin{minipage}[c]{0.9\linewidth}")
            self.buffer.write(r"\\rpgprovenancesymbol\\hspace{0.2em}") 
            self.buffer.write(provenance.text)        
        return

    def end_provenance(self, provenance):
        if config.print_provenence_notes:
            self.buffer.write("\\end{minipage}")        
            self.buffer.write("\\end{center}")
            self.buffer.write("\n\n")
        return

    def start_author(self, author):
        self.buffer.write("{\\LARGE \\rpgtitleauthorfont %s}\\\\" % author.text)        
        return

    def end_author(self, author):
        return

    def start_version(self, version):
        self.buffer.write("{\\LARGE \\versionfont %s}\\\\" % version.text)
        return
    
    def end_version(self, npchps):
        return
            
    def start_title(self, title):
        self.buffer.write(
            "{\\color{rpgtitlefontcolor}\\Huge\\rpgtitlefont %s }\\\\\n"
            % title.text)
        return

    def end_title(self, title):
        return

    def start_caption(self, caption):
        self.buffer.write("\\caption{%s}" % caption.text)
        return

    def end_caption(self, caption):
        return

    def start_subtitle(self, subtitle):        
        self.buffer.write("{\\large\\rpgtitlesubtitlefont  %s}\\\\\n"
                          % subtitle.text)
        return

    def end_subtitle(self, title):
        return

    def start_chaptertitle(self, section_title):
        self.buffer.write("\\begin{chaptertitle}")
        return

    def end_chaptertitle(self, section_title):
        self.buffer.write("\\end{chaptertitle}")
        # self.writeln(r"\updateavailabletextheight{}")
        # self.writeln(r"THE AVAILABLE TEXT HEIGHT POST CHAPTER TITLE \the\availabletextheight{}")
        return
    
    def start_img(self, img):        
        self.buffer.write("\t\\begin{center}\n")
        # optionally draw a box around the image
        # (for debugging)
        #if config.draw_imgs:
        #if config.debug_outline_images:                
        #self.buffer.write("\\fbox{")

        #scale = img.get("scale")
        textwidth_length = img.get("textwidth")
        linewidth_length = img.get("linewidth")
        
        # if scale:
        #     #return f"scale={scale}"
        #     raise Exception("X")
        #     #width = ""
        
        if linewidth_length:
            width = f"max width ={linewidth_length}\\linewidth"

        elif textwidth_length:
            width = f"max width ={textwidth_length}\\textwidth"

        else: 
            width = (
                r"min width={\linewidth}, "
                r"max totalsize ={\linewidth}{\pagegoal}"
            )
        
        self.writeln(
            r"\begin{adjustbox}{%s, keepaspectratio, center}"
            % width
        )
        
        
        filename = self._get_img_filename(img)
        self.buffer.write("\t\\includegraphics{%s}\n" % (filename))
        return

    def end_img(self, img):
        self.buffer.write("\\end{adjustbox}\n")
            
        if img.text is not None:
            self.buffer.write("\t%s\n" % img.text)

        # title
        if "title" in img.attrib:
            title = img.get("title")
            self.buffer.write("\\emph{%s}" % title)
            
        self.buffer.write("\t\\end{center}\n")
        return


    def start_handout(self, handout):
        """
        Handout is a figure+image hybrid on its own page and with a blank
        following page.

        """                
        self.buffer.write("\\newpage\n")
        self.buffer.write("\\pagestyle{empty}\n")
        self.buffer.write("\\begin{figure*}[h!t]\n")
        self.buffer.write("\\begin{center}\n")

        if config.draw_imgs:
            if config.debug_outline_images:
                self.buffer.write("\\fbox{")
        # 
        if "src" in handout.attrib:
            filename = handout.get("src")

        elif "id" in handout.attrib:
            resource_id = handout.get("id")
            try:
                resource = self.db.resources.use(resource_id)
            except KeyError:
                raise Exception(f"Handout image {resource_id} does not exist!")
            filename = resource.get_fname()
            self.buffer.write("\\addcontentsline{loa}{section}{%s}"
                                  % resource.get_contents_desc())
        else:
            raise Exception("Handout missing image src or id!")

        if not exists(filename):
            raise Exception("Handout image does not exist: %s" % filename)

        # handout image without a box
        self.buffer.write("\t\\includegraphics[scale=%s]{%s}\n"
                              % (handout.get("scale", default="1.0"), filename))
        return

    def end_handout(self, handout):
        if handout.text is not None:
            self.buffer.write("\t%s\n" % handout.text)
        if config.debug_outline_images:
            self.buffer.write("}")
        self.buffer.write("\\end{center}\n")
        self.buffer.write("\\end{figure*}\n")
        self.buffer.write("\\cleardoublepage\n")
        self.buffer.write("\\newpage\n")
        self.buffer.write("\\cleardoublepage\n")
        self.buffer.write("\\newpage\n")
        self.buffer.write("\\pagestyle{headings}\n")
        return
    
    def start_figure(self, figure):
        position = "ht"
        
        # sanity check for attributes
        figure_attributes = {"position", "fullwidth", "sideways"}
        attribs = set(figure.attrib.keys())
        unknown_attribs = attribs - figure_attributes
        if unknown_attribs:            
            raise Exception(f"Unknown attributes for figure! {unknown_attribs}")
        
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

        self.buffer.write("\\begin{%s}[%s]\n" % (figure_name, position))
        return

    def end_figure(self, figure):
        caption = figure.get("caption")
        if caption is not None:
            self.buffer.write("\\caption{%s}\n" % caption)        

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

        self.buffer.write("\\end{%s}\n" % figure_name)            
        return

    # An image which the text wraps around
    def start_wrapimg(self, wrapimg):
        position = wrapimg.get("position", "l")
        width = wrapimg.get("scale", default="1.0") + "\\textwidth"
        
        self.buffer.write(
            "\\begin{wrapfigure}{%s}{%s}\n"
            % (position, width))

        if config.draw_imgs:
            if config.debug_outline_images:
                self.buffer.write("\\fbox{")

        self.buffer.write("\\centering\n")

        filename = self._get_img_filename(wrapimg)

        # image without a box
        self.buffer.write(
            "\t\\includegraphics[width=%s]{%s}\n"
            % (width, filename))        
        return

    
    def end_wrapimg(self, wrapimg):
        if config.debug_outline_images:
            self.buffer.write("}")

        caption = wrapimg.get("caption")
        if caption is not None:
            self.buffer.write("\\caption{%s}\n" % caption)
        self.buffer.write("\\end{wrapfigure}\n")
        return

    
    def start_olist(self, enumeration):
        """
        Start enumeration, ordered list of things.

        """
        # the [i] gets us roman numerals in the enumeration
        self.buffer.write("\\begin{enumerate}[label = (\\roman*)]\n")
        return

    def end_olist(self, enumeration):
        self.buffer.write("\\end{enumerate}\n")
        return

    # a list of definitions
    def start_descriptions(self, description_list):
        self.buffer.write("\\begin{description}[topsep=5pt,itemsep=5pt]\n")
        self.terms_on_new_line = description_list.get("termonnewline", False)
        return

    def end_descriptions(self, description_list):
        # note seeing weird artifacts in embedded latex lists without the extra newline
        self.buffer.write("\\end{description}\n\n")
        return

    
    def start_term(self, term):
        """
        List items for a descriptions list

        """
        self.buffer.write(r"\item[")
        self.push_buffer()
        return
    
    def end_term(self, term):
        # strip the term string to try and avoid
        # "! Paragraph ended before \@item was complete." errors.
        stripped_term = self.get_buffer_str(strip=True)
        self.buffer.write(stripped_term)
        self.buffer.write("]")

    def start_description(self, description):
        return

    def end_description(self, description):
        return

    def start_list(self, list_element):
        self.buffer.write("\\begin{itemize}\n")
        return

    def end_list(self, list_element):
        self.buffer.write("\\end{itemize}\n")
        return

    def start_li(self, list_item):
        """
        Start list item.

        """
        self.buffer.write(r"\item ")
        return
    end_li = no_op

    def start_comment(self, comment):
        return

    def end_comment(self, comment):
        return

    def start_branch(self, branch_node):
        return

    def start_branchtitle(self, branchtitle_node):
        self.buffer.write("\\subsubsection*{")
        return

    def end_branchtitle(self, branchtitle_node):
        
        self.buffer.write("}")
        return

    def start_branchdescription(self, branchdescription_node):
        return

    def end_branchdescription(self, branchtitle_node):
        self.buffer.write("\\begin{description}\n")
        return

    def end_branch(self, branch_node):
        self.buffer.write("\\end{description}\n")
        return

    
    def start_path(self, path_node):
        # pathtitle is optional
        has_pathtitle = False
        for child in path_node:
            if child.tag == "pathtitle":
                has_pathtitle = True
        if not has_pathtitle:
            self.buffer.write(f"\\item[\\em❧] ")
        return

    def end_path(self, path_node):
        return

    def start_pathtitle(self, pathtitle_node):
        self.buffer.write(f"\\item[\\em❧ ")
        return

    def end_pathtitle(self, pathtitle_node):
        self.buffer.write("]")
        return

    def start_choice(self, choice_node):
        return

    def end_choice(self, choice_node):
        return
    
    #
    # Table
    #
    # Easiest to parse these out of order.
    start_tablespec = no_op
    end_tablespec = no_op
    start_figuretable = no_op
    end_figuretable = no_op
    start_fullwidthtable = no_op
    end_fullwidthtable = no_op
    start_sidewaystable = no_op
    end_sidewaystable = no_op
    start_standardtable = no_op
    end_standardtable = no_op
    
    def start_table(self, table):
        assert self.table is None
        self.table = TableState()
        self.table.parse_category(table)
            
        # turn this on to draw vertical lines between columns
        DEBUG_COLUMN_WIDTH = False

        # we need to work out in advance the table layout (e.g. |c|c|c|
        # or whatever).
        table_spec = table.find("tablespec")
        table_spec_str = ""
        for child in table_spec.iterchildren():
            if DEBUG_COLUMN_WIDTH:
                table_spec_str += "|"
            
            if child.tag == "fixed": 
                # set the column (content) width
                column_width = float(child.text)
                self.table.column_percent_widths.append(column_width)
                table_spec_str += "p{%s\\hsize}" % column_width                    
                self.table.number_of_columns += 1
                
            elif is_comment(child):
                # ignore comments!
                pass

            else:
                raise Exception("Unknown table spec: %s" % child.tag)         

        if DEBUG_COLUMN_WIDTH:
            table_spec_str += "|"

        # vertical space
        self.buffer.write("\n\\vspace{-0.3cm}")

        # don't have paragraph indents buggering up our table layouts
        self.buffer.write("\\noindent{}")            
        
        # wrap single page tables in a table environment
        # (we use xtabular for multi-page tables and the table environment
        # confuses it about page size).        
        if self.table.figure:
            if self.table.sideways:
                self.buffer.write(r"\begin{sidewaystable*}[htp]")
            elif self.table.fullwidth:
                self.buffer.write(r"\begin{table*}[ht]")
            else:
                self.buffer.write(r"\begin{table}[ht]")
        else:
             self.buffer.write(r"\begin{table}[H]")             
            
        self.buffer.write(" \\begin{center}")


        # Change the separation between table columns??
        tabcolsep = table.get("colsep")
        if tabcolsep is not None:
            self.buffer.write(
                r"\setlength{\tabcolsep}{%s\tabcolsep}" % tabcolsep)

        # Tabular
        if self.table.fullwidth:
            table_width = r"\textwidth"
        else:
            table_width = r"\linewidth"
        self.buffer.write(
            r"\begin{tabularx}{%s}{%s}" 
            % (table_width, table_spec_str))

        # horizontal line
        if self.table.figure:
            self.buffer.write(r" \toprule ")
        else:
            self.buffer.write(r" \hline ")
        assert self.table is not None
        return

    def end_table(self, table):
        assert self.table is not None

        if self.table.figure:
            self.buffer.write(r"\bottomrule ")
        else:
            self.buffer.write(r" \hline ")

        # normal table environment
        self.buffer.write(r"\end{tabularx}")
        
        # Add labels for references
        if self.table.label:
            label = self.buffer.write("\\label{%s}" % self.table.label)

        self.buffer.write(r" \end{center}")

        # Change the separation between table columns??
        tabcolsep = table.get("colsep")
        if tabcolsep is not None:
            self.buffer.write(
                r"\setlength{\tabcolsep}{\originaltabcolsep}")

        # handle any table indexes now!
        for index_entry  in self.table.index_entries:
            self.write_index_entry(index_entry)

        # The table caption from the <tabletitle> element, if we have one.
        if self.table.title:
            self.buffer.write(self.table.title)
            
        if self.table.figure:
            if self.table.sideways:
                self.buffer.write(r"\end{sidewaystable*}")        
            elif self.table.fullwidth:
                self.buffer.write(r"\end{table*}")        
            else:
                self.buffer.write(r"\end{table}")
                # vertical space
                self.buffer.write("\n\\\\\n")
        else:
            self.buffer.write(r"\end{table}")            
        self.buffer.write("\n\n")

        self.table = None
        assert self.table is None
        return

    # tablespec and it's children are parsed by the table element (it's special)
    start_tablecategory = no_op
    end_tablecategory = no_op
    start_tablespec = no_op
    end_tablespec = no_op
    start_fixed = no_op
    end_fixed = no_op
    start_elastic = no_op
    end_elastic = no_op

    # 
    def start_tabletitle(self, table_title):
        self.push_buffer()
        table_title = table_title.text
        table_title = table_title.strip()
        if table_title:        
            self.buffer.write("\\captionof{table}{")

    def end_tabletitle(self, table_title):
        self.buffer.write("}")
        self.table.title = self.get_buffer_str()

    # Tablelabel is also parsed by the table
    def start_tablelabel(self, label):
        self.table.label = label.text.strip()
    end_tablelabel = no_op

    def start_tablesection(self, tablesection):
        self.buffer.write("\\rpgtablesection{%s}" % tablesection.text.strip())
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
            self.table.current_row += 1

        # Do we want to color the row?
        color = None
        if table_row.tag == "tableheaderrow":
            self.buffer.write(
                r"\rowcolor{tableheadercolor}")        
        elif self.table.current_row % 2 == 1:
            self.buffer.write(
                r"\rowcolor{tableoddrowcolor}")
        return

    def end_tablerow(self, table_row):
        self.buffer.write(r"\tabularnewline ")
        return

    start_tableheaderrow = start_tablerow
    end_tableheaderrow = end_tablerow

    def start_td(self, table_data, header=False):
        """
        Start table data.

        """
        # get the number of columns wide this cell should be.
        width = int(table_data.get("width", 1))
        
        # get the number of rows high this cell should be.
        height = int(table_data.get("height", 1))
        height_hint = float(table_data.get("heighthint", 0.0))
        
        # make cells wider than one column?
        if width > 1:
            percent_width = self.table.get_columns_percent_width(width)
            cell_align = ("p{%s\\hsize+%s\\tabcolsep}"
                          % (percent_width, 2*(width-1)))
            self.buffer.write("\\multicolumn{%s}{%s}{"
                                  % (width, cell_align))

        # make cells taller than one row?
        if height > 1:
            self.buffer.write("\\multirow{%s}{=}[-%.2f\\baselineskip]{"
                                  % (height, height_hint))

        # get the text alignment within the cell (default left).
        align = table_data.get("align", "l")
        if align == "l":
            alignment = None
        elif align == "c":
            alignment = "\\centering "
        elif align == "r":
            alignment = "\\raggedleft "
        else:
            raise Exception(f'Unknown table cell alignments "{align}"')
        if alignment: 
            self.buffer.write(alignment)

        # cell color?
        if header:
            cell_color = "\\cellcolor{tableheadercolor}"
        else:
            cell_color = None
        if cell_color:
            self.buffer.write(cell_color)
           
        self.table.current_column = (
            (self.table.current_column + width) % self.table.number_of_columns)

        if header:
            self.buffer.write("\\begin{mdbold}")
        return

    def end_td(self, table_data, header=False):
        if header:
            self.buffer.write("\\end{mdbold}")
        
        # get the number of columns wide or rows high this cell should be.
        width = int(table_data.get("width", 1))
        height = int(table_data.get("height", 1))
        
        # get the text alignment within the cell.
        align = table_data.get("align", "l")

        # borders
        borders = int(table_data.get("borders", 0))
                
        if width > 1:
            # multicolumn table data
            self.buffer.write("}")

        if height > 1:
            # multicolumn table data
            self.buffer.write("}")

        if self.table.current_column != 0:
            self.buffer.write(" & ")
        return    

    # table headers are a type of table data
    start_th = start_td
    def start_th(self, th):
        return self.start_td(th, header=True)
    
    def end_th(self, th):
        return self.end_td(th, header=True)        

    def start_tableofcontents(self, table_of_contents):
        self.buffer.write("\\tableofcontents\n")
        return
    end_tableofcontents = no_op

    def start_listoffigures(self, list_of_figures):
        self.buffer.write(r"\listoffigures{}")
        return
    end_listoffigures = no_op

    def start_listofart(self, list_of_art):
        return
    end_listofart = no_op

    def start_list_of_tables(self, list_of_tables):
        self.buffer.write("\\listoftables\n")
        return

    def end_list_of_tables(self, list_of_tables):
        return

    def start_label(self, label):
        self.buffer.write(r"\label{")
        return
    def end_label(self, label):
        self.buffer.write("}")
        return

    def start_fourcolumns(self, threecolumns):
        self.buffer.write("\\onecolumn\\begin{multicols}{4}\n")
        return

    def end_fourcolumns(self, ability_group):
        self.buffer.write("\\end{multicols}\\twocolumn\n")
        return
    
    def start_attempt(self, success):
        self.buffer.write("\\rpgattempt{}")
        return
    end_attempt = no_op

    def start_success(self, success):
        self.buffer.write("\\rpgsuccess{}")
        return
    end_success = no_op

    def start_fail(self, fail):
        self.buffer.write("\\rpgfail{}")
        return
    end_fail = no_op

    def start_eg(self, fail):
        self.buffer.write(r"e.g.\@{}")
        return
    end_eg = no_op

    def start_ie(self, fail):
        self.buffer.write(r"i.e.\@{}")
        return
    end_ie = no_op

    def start_aka(self, fail):
        self.buffer.write(r"a.k.a.\@{}")
        return
    end_aka = no_op

    def start_etc(self, fail):
        self.buffer.write(r"etc.\protect\@{}")
        return
    end_etc = no_op

    def start_nb(self, fail):
        self.buffer.write(r"n.b.\@{}")
        return
    end_nb = no_op

    def start_notapplicable(self, fail):
        self.buffer.write("n/a")
        return
    end_notapplicable = no_op

    def start_dpool(self, fail):
        self.buffer.write("\\dpool{}")
        return
    end_dpool = no_op

    def start_vspace(self, vspace):
        if vspace.text is None:
            drop = 1.0
        else:
            drop = convert_str_to_float(vspace.text)
        self.buffer.write("\\vspace{%s\\drop}\n" % drop)
        return
    end_vspace = no_op


    # def start_hspace(self, vspace):
    #     if hspace.text is None:
    #         drop = 1.0
    #     else:
    #         drop = convert_str_to_float(vspace.text)
    #     self.buffer.write("\\vspace{%s\\drop}\n" % drop)
    #     return
    # end_vspace = no_op
    
    
    #
    # Monster blocks.
    #

    def start_monsterblock(self, monsterblock):
        self.buffer.write(r"\begin{minipage}{\linewidth}")
        return

    def end_monsterblock(self, monsterblock):
        self.buffer.write(r"\end{minipage}")
        return

    def start_mbtitle(self, mbtitle):
        self.buffer.write(r"\mbsep{}\begin{mbtitle}")
        return

    def end_mbtitle(self, mbtitle):
        self.buffer.write(r"\end{mbtitle}\noindent{}")
        return
    
    def start_mbtags(self, mbtags):
        self.buffer.write(r"\begin{mbtags}")
        return

    def end_mbtags(self, mbtags):
        self.buffer.write(r"\end{mbtags}\noindent")
        return

    def start_mbdefence(self, mbac):
        self.buffer.write(r"\textbf{Defence: }\begin{mbdefence}")
        return

    def end_mbdefence(self, mbac):
        self.buffer.write(r"\end{mbdefence}\enspace{}")
        return

    def start_mbhp(self, mbhp):
        self.buffer.write(r"\textbf{HP: }\begin{mbhp}")
        return
    
    def end_mbhp(self, mbhp):
        self.buffer.write("\\end{mbhp}")
        return

    def start_mbmove(self, mbmove):
        self.buffer.write(r"\textbf{Mv: }\begin{mbmove}")
        return

    def end_mbmove(self, mbmove):
        self.buffer.write("\\end{mbmove}")
        return

    def start_mbinitiative(self, mbinitiative):
        self.buffer.write(r"\textbf{Init: }\begin{mbinitiative}")
        return
    def end_mbinitiative(self, mbinitiati):
        self.buffer.write("\\end{mbinitiative}")
        return
    
    def start_mbmagic(self, mbmagic):
        self.buffer.write(r"\textbf{Magic: }\begin{mbmagic}")
        return
    def end_mbmagic(self, mbmagic):
        self.buffer.write("\\end{mbmagic}")
        return
    
    def start_mbmettle(self, mbmettle):
        self.buffer.write(r"\textbf{Mettle: }\begin{mbmettle}")
        return
    def end_mbmettle(self, mbmettle):
        self.buffer.write("\\end{mbmettle}")
        return
    
    def start_mbluck(self, mbluck):
        self.buffer.write(r"\textbf{Luck: }\begin{mbluck}")
        return
    def end_mbluck(self, mbluck):
        self.buffer.write("\\end{mbluck}")
        return
    

    def start_mbstr(self, mbstr):
        self.buffer.write(r"\\\textbf{Str: }\begin{mbattr}")
        return
    def end_mbstr(self, mbmagic):
        self.buffer.write("\\end{mbattr}")
        return
    def start_mbend(self, mbend):
        self.buffer.write(r"\textbf{End: }\begin{mbattr}")
        return
    def end_mbend(self, mbend):
        self.buffer.write("\\end{mbattr}")
        return

    def start_mbag(self, mbag):
        self.buffer.write(r"\textbf{Ag: }\begin{mbattr}")
        return
    def end_mbag(self, mbag):
        self.buffer.write("\\end{mbattr}")
        return
    
    def start_mbspd(self, mbspd):
        self.buffer.write(r"\textbf{Spd: }\begin{mbattr}")
        return
    def end_mbspd(self, mbspd):
        self.buffer.write("\\end{mbattr}")
        return
    
    def start_mbper(self, mbper):
        self.buffer.write(r"\textbf{Per: }\begin{mbattr}")
        return
    def end_mbper(self, mbper):
        self.buffer.write("\\end{mbattr}")
        return
    
    def start_mbwil(self, mbwil):
        self.buffer.write(r"\textbf{Will: }\begin{mbattr}")
        return
    def end_mbwil(self, mbwil):
        self.buffer.write("\\end{mbattr}")
        return

    
    def start_mbarmour(self, mbarmour):
        #self.buffer.write("\\begin{small}")
        return        
    def end_mbarmour(self, mbarmour):
        #self.buffer.write("\\end{small} & %\n")
        #self.buffer.write("\n")
        return

    def start_mbabilities(self, mbabilities):
        #self.buffer.write(r"\textbf{Abilities}: ")
        return
    def end_mbabilities(self, mbabilities):
        #self.buffer.write("\n")
        return

    def start_mbaspects(self, mbaspects):
        self.buffer.write(r"\textbf{Aspects:} ")
        return
    def end_mbaspects(self, mbaspects):
        self.buffer.write("\\\\\n")
        return
    
    def start_mbdescription(self, mbdescription):
        self.buffer.write(r"\vspace{1.0mm}"
                              r"\textbf{Description:}"
                              r"\hfill"
                              r"\break"
                              r"\vspace{-0.3cm}")
        return
    def end_mbdescription(self, mbdescription):
        self.buffer.write("\n")
        return
    
    def start_mbnpc(self, mbnpc):
        return

    def end_mbnpc(self, mbnpc):
        self.buffer.write("\\newline{}")
        return

    def start_npcname(self, npcname):
        self.buffer.write(r"\textbf{Name: }\begin{npcname}")
        return
    def end_npcname(self, npcname):
        self.buffer.write("\\end{npcname} ")
        return
    
    def start_npchps(self, npchps):
        self.buffer.write(r"\textbf{HPs: }\begin{npchp}")
        return
    def end_npchps(self, npchps):
        self.buffer.write("\\end{npchp}")
        return

    def start_inspiration(self, inspiration):
        img = inspiration.getparent()
        if "id" in img.attrib:
            resource_id = img.get("id")
            resource = self.db.resources.use(resource_id)
            sig = resource.get_sig()
            
            self.buffer.write(r"{\attributionfont %s}" % sig)
        else:
            raise Exception("Image inspiration missing id!")        
        return
    end_inspiration = no_op

    def start_attribution(self, attribution):
        img = attribution.getparent()
        if "id" in img.attrib:
            resource_id = img.get("id")
            resource = self.db.resources.use(resource_id)
            sig = resource.get_sig()
            
            self.buffer.write(r"{\attributionfont %s}" % sig)
        else:
            raise Exception("Image attribution missing id!")
        return
    end_attribution = no_op

    def start_ellipsis(self, ellipsis):
        self.buffer.write(r"\ldots")
    end_ellipsis = no_op

    def start_hline(self, _):
        if self.table is None:
            self.buffer.write(r"\noindent\rule{\columnwidth}{0.8pt}\nopagebreak\vspace{-0.8em}")
        else:
            self.buffer.write(r"\hline")
        return
    end_hline = no_op

    def start_abilityref(self, ability_ref_node):
        ability_ref = abilities.AbilityRef()
        ability_ref.parse(ability_ref_node)
        ability = self.db.get_ability(ability_ref)
        if ability is None:
            line_number = ability_ref_node.sourceline
            context = get_error_context(self.xml_fname, line_number)
            raise Exception(
                f"Can't find ability that abilityref is refering to! :"
                f"({ability_ref.get_id()}) in "
                f"{self.xml_fname}:{line_number}\n")
            
        name = ability.get_name()            
        rank_num = ability_ref.get_rank()
        specializations = ability_ref.get_specializations_str()

        if rank_num is None:
            if specializations:
                self.buffer.write(f"{name}[{specializations}]")
            else:
                self.buffer.write(f"{name}")
        else:
            if specializations:
                self.buffer.write(f"{name}[{specializations}] {rank_num}")
            else:
                self.buffer.write(f"{name} {rank_num}")

        #except KeyError:
        #    # bad ability ref...
        #    raise Exception("Bad abilityref!!  Missing ability id.")        
        return    
    def end_abilityref(self, _):
        return    


    def start_sidebar(self, sidebar):
        """
        """

        if "title" in sidebar.attrib:        
            title = sidebar.attrib.get("title")
            title_str = (
                r"fonttitle=\sidebartitlefont\huge, "
                r"title={%s}, " % title)
        else:
            title_str = ""
        
        self.buffer.write(
            r"\begin{figure}[t]"
            r"\sidebarfont"
            r"\begin{tcolorbox}["
            r"enhanced, "
            "colback=sidebarcolor, "
            "colframe=sidebarboxcolor, "
            f"{title_str}"
            "arc=0mm, " # no rounded corners
            "drop fuzzy shadow]" # has a drop shadow
            r"\begin{minipage}{1.0\linewidth}")
        return

    def end_sidebar(self, _):
        self.buffer.write(
            r"\end{minipage}"
            r"\end{tcolorbox}"
            r"\end{figure}")
        return

    # FIXME: what is this for?
    def start_details(self, _):        
        # self.buffer.write("\\paragraph*{Detials}")
        return        
    end_details = no_op

    def start_hfill(self, hfill):        
        self.buffer.write(r"\hfill")
        return
    end_hfill = no_op
            
    def start_divider(self, divider):        
        char_code = 89 # standard
        if divider.attrib == "fancy":
            char_code = 80
        #self.buffer.write(r"\pgfornament[scale=0.2,color=red]{%s}" % char_code)
        self.buffer.write(r"\centerline{\pgfornament[scale=0.14]{%s}}"
                          % char_code)
        #self.buffer.write(r"{\centering\pgfornament[scale=0.14]{%s}}"
        #                  % char_code)
            # r"\begin{centering}"
            # r"\pgfornament[scale=0.14]{%s}"
            # r"\end{centering}") % char_code)
        return
    end_divider = no_op
            

    def _start_short_measurement(self, sm):
        """
        Converts a measurement constant, e.g. <m3> to metric or imperial
        depending on a setting in the configuration file.

        """
        if config.use_imperial:
            distance_text = sm.get("imperial")
            if distance_text is None:
                raise Exception("Imperial distance not specified!")

        else:
            distance_text = sm.get("metric")
            if distance_text is None:
                raise Exception("Metric distance not specified!")

        self.buffer.write(normalize_ws(distance_text).strip())
        return

    # Measurement Constants.
    start_m05, end_m05 = _start_short_measurement, no_op
    start_m2, end_m2 = _start_short_measurement, no_op
    start_m3, end_m3 = _start_short_measurement, no_op
    start_m6, end_m6 = _start_short_measurement, no_op    
    start_m9, end_m9 = _start_short_measurement, no_op    
    start_m10, end_m10 = _start_short_measurement, no_op    
    start_m12, end_m12 = _start_short_measurement, no_op    
    start_m20, end_m20 = _start_short_measurement, no_op    
    start_m30, end_m30 = _start_short_measurement, no_op    
    start_m90, end_m90 = _start_short_measurement, no_op    
    start_m180, end_m180 = _start_short_measurement, no_op    
    start_km3, end_km3 = _start_short_measurement, no_op
    
    def _start_sv(self, sv_element):
        """
        Shared formatting for all the skill values, e.g. <sv13/>
        
        """
        tag = sv_element.tag
        match_obj = _sv_regex.search(tag)
        if match_obj is not None:
            skill_value = match_obj[0]
            #self.buffer.write(fr"\nofatediesymbol/{dc}")
            self.buffer.write(fr"SSV: {skill_value}")
        else:
            raise Exception(
                f"Unknown skill value check! {node_to_string(sv_element)}")

    start_sv3, end_sv3 = _start_sv, no_op
    start_sv5, end_sv5 = _start_sv, no_op
    start_sv7, end_sv7 = _start_sv, no_op
    start_sv9, end_sv9 = _start_sv, no_op
    start_sv11, end_sv11 = _start_sv, no_op
    start_sv13, end_sv13 = _start_sv, no_op
    start_sv15, end_sv15 = _start_sv, no_op
    start_sv17, end_sv17 = _start_sv, no_op
    start_sv19, end_sv19 = _start_sv, no_op
    start_sv21, end_sv21 = _start_sv, no_op
    start_sv23, end_sv23 = _start_sv, no_op
    start_sv25, end_sv25 = _start_sv, no_op
    start_sv27, end_sv27 = _start_sv, no_op

    def start_d20plusrank(self, tag):
        #self.buffer.write(r"\fatediesymbol/\skilldiesymbol+Rank")
        self.buffer.write(r"\fatediesymbol/\skilldiesymbol+Rank")
        return
    end_d20plusrank = no_op

    
