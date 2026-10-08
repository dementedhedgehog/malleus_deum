# -*- coding: utf-8 -*-
from os.path import join, splitext, exists
import sys
import copy
import io
import re
import typing

import config
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
from db import DB
from doc_walkers import BaseDocFormatter, no_op, DocTreePreprocessor as pp


# Regex to find the boundary between non-digits and digits at the end
# of <sv13/> type elements.
_sv_regex = re.compile(r'(\d+)$')

#
# Be careful adding newlines.  Latex changes its behaviour when it sees empty
# lines.  
NEWLINE = "\n"
COMMENTLINE = "%\n"

latex_frontmatter = r"""
%% -*- mode: LaTeX; eval: (auto-revert-mode 1); buffer-read-only: t; -*-

%%
%%  *** MALLEUS DEUM ***
%%
%%

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
\usepackage{epigraph}              %% after title epigraphs
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
\usepackage{pdfpages}              %% for includepdf
\usepackage{pgfornament}           %% for the page dividers
\usepackage{quoting}               %% more configurable quoting environment.
\usepackage{rotating}              %% for sidewaystable
\usepackage{tabularx}              %% for tables
\usepackage{tcolorbox}             %% color boxes
\tcbuselibrary{skins}              %% more color box stuff
\usepackage[raggedright]{titlesec} %% avoid hyphenating titles
\usepackage{unicode-math}
\usepackage{varwidth}              %% for centering cells in tables.
\usepackage{wrapfig}               %% figures with text wrapping.
\usepackage{xtab}                  %% for multipage tables

\usepackage{transparent}           %% for transparent backgrounds
\usepackage[unicode]{hyperref}     %% for hyperlinks in pdf
\usepackage{bookmark}              %% fixes a hyperref warning.

%% TESTING
\usepackage{changepage}


%% more floats (side-step a build error)
\usepackage[maxfloats=256]{morefloats}
\maxdeadcycles=1000


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
\definecolor{champagne}{RGB}{247,231,206}
\definecolor{palechampagne}{RGB}{249,240,223}

%%
%% Colour Aliases
%%
\colorlet{rpgtitlefontcolor}{black}
\colorlet{chapterfontcolor}{black}
\colorlet{mdsectionfontcolor}{rosewood}
\colorlet{mdsubsectionfontcolor}{rosewood}
\colorlet{mdsubsubsectionfontcolor}{black}
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
%% Principle and Corollary environments
%%
%% For the Rationale doc.. don't use these in player facing docs. Redefine the
%% corollary/principle style to not put parentheses around the title.
%%
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
%% Fonts
%%
%% Used for chapter/section titles
\newfontfamily{\cloisterblack}[Path=fonts/]{CloisterBlack}
%% Used on the title page
\newfontfamily{\dogma}[Path=fonts/]{Dogma}
%% Quote font
\newfontfamily{\isabella}[Path=fonts/, Scale=1.1]{Isabella}
\newfontfamily{\germania}[Path=fonts/]{GermaniaVersalien}
%% Used for Drop Caps
\newfontfamily{\carrickc}[Path=fonts/]{CarrickCaps}
%% Used for the body of the text
\newfontfamily{\libertine}{Linux Libertine O}
\newfontfamily{\caudex}[Path=fonts/, Scale=1.1]{Caudex-Regular}

\newenvironment{smaller}{\begin{footnotesize}}{\end{footnotesize}}

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
\newcommand{\rpgtitlefont}{\fontsize{90}{102}\dogma}
\newcommand{\rpgtitlesubtitlefont}{\fontsize{62}{68}\cloisterblack}
\newcommand{\rpgtitlesubsubtitlefont}{\cloisterblack}
\newcommand{\rpgtitleauthorfont}{\dogma}
\newcommand{\rpgsmalltitlefont}{\libertine}
\newcommand{\versionfont}{\dogma}
\newcommand{\mdsectionfont}{\cloisterblack}
\newcommand{\mdsubsectionfont}{\cloisterblack}
\newcommand{\mdsubsubsectionfont}{\cloisterblack}
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
%%\setmathfont{TeX Gyre Pagella Math}
%%\newcommand{\downarrowfrombar}{\ensuremath{\mapsdown}} 
%%\newcommand{\uparrowfrombar}{\ensuremath{\mapsup}}


%% Custom indent environment
%% Inserts no vertical space and is nestable.
\newenvironment{mdindent}{%%
\vspace{-1\parskip}%%
\begin{adjustwidth}{0.3cm}{\rightskip}%%
}{%%
\end{adjustwidth}%%
\ifvmode\else\vspace{-1\parskip}\fi{}%%
}


%% Custom linebreak mode
\newcommand{\mdbr}{\ifvmode\else\newline\fi}


%% Custon Bold Environment
\newenvironment{mdbold}{\bfseries{}}{}


%% Custon Quotemark Environment
\newenvironment{mdquotemarks}{``}{''}


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


%%
%% Title Page
%%
\newenvironment{mdtitlepage}{%%
\begin{titlepage}%%
\begin{center}%%
}{%%
\end{center}%%
\end{titlepage}}

\newenvironment{mdtitle}{%%
\color{rpgtitlefontcolor}\rpgtitlefont}{}

\newenvironment{mdsubtitle}{%%
\color{rpgtitlefontcolor}\rpgtitlesubtitlefont}{}

\newenvironment{mdsubsubtitle}{%%
\color{rpgtitlefontcolor}\rpgtitlesubsubtitlefont}{}

\newenvironment{mdauthor}{%%
\color{rpgtitlefontcolor}\large\rpgtitleauthorfont}{}

\newenvironment{mdversion}{%%
\color{rpgtitlefontcolor}\rpgtitleauthorfont}{}


%%
%% Spacing
%%
%% drop is a vspace 1/100th the page text height.
%%
\newlength\drop
\drop = 0.01\textheight

%% Caption Spacing (spacing around table/figure captions)
\setlength{\abovecaptionskip}{2ex}

%% Use a page style that shows chapter headings at the top of the page.
\pagestyle{headings}

\titleformat{name=\chapter}[hang]
{\raggedright\Huge\bfseries\chapterfont\color{chapterfontcolor}}
{}{1em}{}


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
\colorlet{tableheadercolor}{tan}
%% Every second row color (champagne)
\colorlet{tableoddrowcolor}{palechampagne}

%% Table header - centered and bold.
%% \newcommand{\mdtblheader}[1]{{\centering\arraybackslash \bfseries #1\par}}
%%\newcommand{\mdtblheader}[1]{\begin{varwidth}{\linewidth}\setlength{\parskip}{0pt}\centering\bfseries #1\end{varwidth}}

%% Center a <td> or <th> element
%%\newcommand{\mdtblcenter}[1]{{\centering\arraybackslash #1\par}}

\newcommand{\mdtblcenter}[1]{{\centering\arraybackslash #1}}

%%\newcommand{\mdtblcenter}[1]{\begin{varwidth}{\linewidth}\setlength{\parskip}{0pt}\centering #1\end{varwidth}}

%%{\centering\arraybackslash}X

%%\newcommand{\mdtblcenter}[1]{%%
%%  \begin{varwidth}{\linewidth}%%
%%    \setlength{\topsep}{0pt}%%     <-- Removes top/bottom padding
%%    \setlength{\partopsep}{0pt}%%   <-- Removes extra structural padding
%%    \setlength{\parskip}{0pt}%%
%%    \centering #1%%
%%  \end{varwidth}%%
%%}

%%
%% Elastic Vertical Space
%%
%% Suggest to latex that if it wants to add vertical space for layout here is a
%% reasonably good place to do so.  (Adds vspace of 0 to 2cm and let's latex
%% decide how much).
%%
\newcommand{\mdspacer}{\vspace{0cm plus 2cm}}


%%
%% Sidebar Formatting
%%
\colorlet{sidebarcolor}{palechampagne}
\colorlet{sidebarboxcolor}{black}
\newsavebox{\sidebarbox}


%%
%% Create custom environments from commands.
%% We do this because the \begin and \end semantics of environments map nicely
%% onto xmls begin  <x> and end </x> elements than fiddling with latex commands
%% like \bold{text}; for example.
%%
%% NewEnviron eats trailing whitespace!! 
%%
\NewEnviron{mdchaptertitle}{\chapter{\BODY}}
\NewEnviron{mdsectiontitle}{\section{\BODY}}
\NewEnviron{mdsubsectiontitle}{\subsection{\BODY}}
\NewEnviron{mdsubsubsectiontitle}{\subsubsection{\BODY}}
\NewEnviron{mdemph}{\emph{\color{emphcolor}\BODY}}




%%
%% Custom Symbols
%%

%% Declares a new length variable named \mycustomlength
\newlength{\symbolsize}
\setlength{\symbolsize}{0.8em}

%% Make sure they're all the same size
\newlength{\symbolverticaloffset}
\setlength{\symbolverticaloffset}{-0.2em}
\newlength{\symbolhorizontalspace}
\setlength{\symbolhorizontalspace}{0.3ex}

%% Same offsets for all symbols.
\newlength{\actionsymbolverticaloffset}
\setlength{\actionsymbolverticaloffset}{-0.7mm}
\newlength{\actionsymbolhorizontaloffset}
\setlength{\actionsymbolhorizontaloffset}{0.2mm}

%% Symbol Free Action
\newcommand\freeactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_free_action.png}}}

%% Symbol One Action
\newcommand\oneactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_one_action.png}}}

%% Symbol Two Actions
\newcommand\twoactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_two_actions.png}}}

%% Symbol Three Actions
\newcommand\threeactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_three_actions.png}}}

%% Symbol Four Actions
\newcommand\fouractionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_four_actions.png}}}

%% Symbol Five Actions
\newcommand\fiveactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_five_actions.png}}}

%% Symbol Response
\newcommand\responsesymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_response.png}}}

%% Symbol Free Response
\newcommand\freeresponsesymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_free_response.png}}}

%% Symbol Mandatory Response
\newcommand\mandatoryresponsesymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_mandatory_response.png}}}

%% Symbol Mandatory Free Response
\newcommand\mandatoryfreeresponsesymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_mandatory_free_response.png}}}

%% Symbol Interrupt
\newcommand\interruptsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_interrupt.png}}}

%% Symbol Free Interrupt
\newcommand\freeinterruptactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_free_interrupt.png}}}

%% Symbol Mandatory Interrupt
\newcommand\mandatoryinterruptsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_mandatory_interrupt.png}}}

%% Symbol Mandatory Free Interrupt
\newcommand\mandatoryfreeinterruptactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_mandatory_free_interrupt.png}}}

%% Symbol GM Fiat Check
\newcommand\gmfiatchecksymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_gm_fiat_check.png}}}

%% Symbol GM Fiat Save
\newcommand\gmfiatsavesymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_gm_fiat_save.png}}}

%% Symbol Out of Combat Action
\newcommand\outofcombatsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_out_of_combat_action.png}}}

%% Multi Round Action
\newcommand\multiroundactionsymbol{%%
\hspace{\actionsymbolhorizontaloffset}%%
\raisebox{\actionsymbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_multi_round_action.png}}}

%% Check Arrow Symbol
\newcommand\checkarrowsymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_check_arrow.png}%%
\hspace{\symbolhorizontalspace}}}

%% VS Check Arrow Symbol
\newcommand\vscheckarrowsymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_vs_check_arrow.png}%%
\hspace{\symbolhorizontalspace}}}

%% Save Arrow Symbol
\newcommand\savearrowsymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_save_arrow.png}%%
\hspace{\symbolhorizontalspace}}}

%% Vs Save Arrow Symbol
\newcommand\vssavearrowsymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_vs_save_arrow.png}%%
\hspace{\symbolhorizontalspace}}}

%% Save Symbol
\newcommand\savesymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_save.png}%%
\hspace{\symbolhorizontalspace}}}

%% Free Save Symbol
\newcommand\freesavesymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_free_save.png}%%
\hspace{\symbolhorizontalspace}}}

%% Save or Free Save Symbol
\newcommand\saveorfreesavesymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_save_or_free_save.png}%%
\hspace{\symbolhorizontalspace}}}

%% Auxiliary Symbol
\newcommand\auxiliarysymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/check_auxiliary_symbol.png}%%
\hspace{\symbolhorizontalspace}}}


%% Antagonist Check Symbol also used for antagonistic abilities.
\newcommand\antagonistsymbol{%%
%%\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_antagonist.png}%%
\hspace{0.0\symbolhorizontalspace}}
%%}

%% Check Action Symbol
\newcommand\actionsymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/check_action_symbol.png}%%
\hspace{\symbolhorizontalspace}}}

%% Reaction Symbol
\newcommand\reactionsymbol{%%
\raisebox{\symbolverticaloffset}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/check_reaction_symbol.png}%%
%%\hspace{\symbolhorizontalspace}
}}

%% Subsubsection Symbol
\newcommand\subsubsectionsymbol{%%
\raisebox{-0.2mm}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_subsubsection.png}%%
\hspace{\symbolhorizontalspace}}}

%% Ability Subsubsection Symbol
\newcommand\abilitysubsubsectionsymbol{%%
\raisebox{-0.2mm}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_abilitysubsubsection.png}%%
\hspace{\symbolhorizontalspace}}}

%% Ability Versus Save Symbol
\newcommand\vssavesymbol{%%
\raisebox{-0.5mm}{
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_vs_save.png}%%
\hspace{\symbolhorizontalspace}}
}

%% Ability Versus Check Symbol
%%\newcommand\vschecksymbol{%%
%%\raisebox{-0.5mm}{%%
%%\includegraphics[height=\symbolsize]%%
%%{./resources/symbols/symbol_vs_check.png}%%
%%\hspace{\symbolhorizontalspace}}
%%}

%% Ability Bullet Symbol
\newcommand\abilitybulletsymbol{%%
\raisebox{-0.5mm}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_ability_bullet.png}%%
\hspace{\symbolhorizontalspace}}
}

%% Elder Sign Symbol
\newcommand\eldersign{%%
\raisebox{-0.5mm}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_elder_sign.png}%%
\hspace{\symbolhorizontalspace}}
}

%% Start of Turn Symbol
\newcommand\startofturnsymbol{%%
\raisebox{-0.5mm}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_start_of_turn.png}%%
%%\hspace{\symbolhorizontalspace}
}}

%% Any Out of Turn Action Symbol
\newcommand\anyootasymbol{%%
\raisebox{-0.5mm}{%%
\includegraphics[height=\symbolsize]%%
{./resources/symbols/symbol_any_oota.png}%%
\hspace{\symbolhorizontalspace}}
}


%%\DeclareRobustCommand{\optionalsymbol}{%%
%%\protect\includegraphics[height=\symbolsize]{./resources/symbols/symbol_optional.png}%%
%%\hspace{\symbolhorizontalspace}%%
%%}

\newcommand\versus{\raisebox{-0.2mm}{{\cloisterblack{}VS}}}

%%
%%  Pass Through Definitions
%%
\newcommand{\emdash}{\textemdash }
%%\newcommand{\daggersymbol}{\dag }
\newcommand{\optionalsymbol}{\dag }



%% Fate Die Symbol
%% \newcommand\fatediesymbol{%%
%% \raisebox{\symbolverticaloffset}{%%
%% \includegraphics[height=\symbolsize]%%
%% {./resources/symbol_fate_die/symbol_fate_die.png}}}

%% %% No Fate Die Symbol
%% \newcommand\nofatediesymbol{%%
%% \raisebox{\symbolverticaloffset}{%%
%% \includegraphics[height=\symbolsize]%%
%% {./resources/symbol_no_fate_die/symbol_no_fate_die.png}}}

%% %% Skill Die Symbol
%% \newcommand\skilldiesymbol{%%
%% \raisebox{\symbolverticaloffset}{%%
%% \includegraphics[height=\symbolsize]%%
%% {./resources/symbol_skill_die/symbol_skill_die.png}}}


%%
%% Sectioning
%%

%% include subsubsections in the table of contents
\setcounter{tocdepth}{3}

%% allow \subsubsection numbering.
%% \setcounter{secnumdepth}{3}


\titleformat{\section}
{\mdsectionfont\LARGE\color{mdsectionfontcolor}}
{\thesection}{0.5em}{}

\titleformat{\subsection}
{\mdsubsectionfont\Large\color{mdsubsectionfontcolor}}
{\thesubsection}{0.5em}{}

%%\titleformat{\subsubsection}
%%{\bfseries\mdsubsectionfont\color{mdsubsubsectionfontcolor}}
%%{\thesubsubsection}{0.5em}{\subsubsectionsymbol{}}

\newcommand\rpgtablesection[1]{
\rule{0pt}{1ex}\bfseries\scriptsize #1}


\titlespacing*{\abilitysubsubsection}%%
{0pt}%%
{3.25ex plus 1ex minus .2ex}%%
{1.5ex plus .2ex}





%%
%% Monsters Block Formatting.
%%
\newcommand\mbsep{\hrule\hfill\break}

\newenvironment{mbattr}
{\color{monstertitlecolor}\normalsize}{\hfill}

\newenvironment{mbtitle}%%
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
%% Relax spacing around figures.
%%

%% Max fraction of page/column for floats at top
\renewcommand{\topfraction}{0.85}
%% Max fraction of page/column for floats at bottom
\renewcommand{\bottomfraction}{0.7}   
%% Minimum fraction of page/column that must be text
\renewcommand{\textfraction}{0.15}    
%% Minimum fraction a float must occupy to get its own page
\renewcommand{\floatpagefraction}{0.75} 

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
\typeout{--- Page Info ---}
\typeout{ Line Width: \the\linewidth}
\typeout{ Text Height: \the\textheight}
\typeout{}

""".lstrip() # (Make the emacs mode line the first line in the file.)

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
    Save Index Entry State.
    FIXME: this is complicated.  I could just walk the tree and find this info.

    """
    def __init__(self):
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
        
    
class LatexFormatter(BaseDocFormatter):
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

    def write(self, *args, **kwargs):
        self.buffer.write(*args, **kwargs)
        return
        
    def writelines(self, *args, **kwargs):
        self.buffer.writelines(*args, **kwargs)
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
            # self.write("\\addcontentsline{loa}{section}{%s}"
            #                       % resource.get_contents_desc())
        else:
            raise Exception("Image missing source or id!")

        if not exists(filename):
            raise Exception("Image does not exist: %s" % filename)        
        return filename

    def start_book(self, book):
        # must be a valid latex paper size
        # FIXME == config.A4?  but these should be an xml enum <a4/>
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
        self.write(latex_frontmatter % formatting)

        if config.display_page_background:
            self.write(
                "\n"
                "% use a parchment background image for the pages\n"
                "\\CenterWallPaper{1.0}"
                "{./resources/paper_" + paper_size + ".jpg}"
                "\n\n")
        return

    def end_book(self, book):
        self.write(r"\end{document}" + NEWLINE)        
        return

    def handle_appendix(self, appendix):
        self.write(
            r"\appendix" + NEWLINE + 
            r"\addcontentsline{toc}{chapter}{Appendicies}" + NEWLINE)
        return

    def handle_keyword(self, keyword):
        self.write(r"{\color{keywordcolor} \textbf{%s}}" % keyword)
        return

    # def handle_daggersymbol(self, symbol):2
    #     self.write(r"\dag ")

    def handle_startofturnsymbol(self, symbol):
        self.write(r"\startofturnsymbol{}")

    def handle_freeactionsymbol(self, symbol):
        self.write(r"\freeactionsymbol{}")
    
    def handle_oneactionsymbol(self, symbol):
        self.write(r"\oneactionsymbol{}")

    def handle_twoactionsymbol(self, symbol):
        self.write(r"\twoactionsymbol{}")
        
    def handle_threeactionsymbol(self, symbol):
        self.write(r"\threeactionsymbol{}")

    def handle_fouractionsymbol(self, symbol):
        self.write(r"\fouractionsymbol{}")

    def handle_fiveactionsymbol(self, symbol):
        self.write(r"\fiveactionsymbol{}")

    def handle_interruptsymbol(self, symbol):
        self.write(r"\interruptsymbol{}")

    def handle_freeinterruptsymbol(self, symbol):
        self.write(r"\freeinterruptactionsymbol{}")

    def handle_mandatoryinterruptsymbol(self, symbol):
        self.write(r"\mandatoryinterruptsymbol{}")

    def handle_mandatoryfreeinterruptsymbol(self, symbol):
        self.write(r"\mandatoryfreeinterruptactionsymbol{}")

    def handle_responsesymbol(self, symbol):
        self.write(r"\responsesymbol{}")

    def handle_freeresponsesymbol(self, symbol):
        self.write(r"\freeresponsesymbol{}")

    def handle_mandatoryresponsesymbol(self, symbol):
        self.write(r"\mandatoryresponsesymbol{}")

    def handle_mandatoryfreeresponsesymbol(self, symbol):
        self.write(r"\mandatoryfreeresponsesymbol{}")

    def handle_gmfiatchecksymbol(self, symbol):
        self.write(r"\gmfiatchecksymbol{}")

    def handle_checkarrowsymbol(self, symbol):
        self.write(r"\checkarrowsymbol{}")

    def handle_vscheckarrowsymbol(self, symbol):
        self.write(r"\vscheckarrowsymbol{}")

    def handle_savearrowsymbol(self, symbol):
        self.write(r"\savearrowsymbol{}")

    def handle_vssavearrowsymbol(self, symbol):
        self.write(r"\vssavearrowsymbol{}")

    def handle_gmfiatsavesymbol(self, symbol):
        self.write(r"\gmfiatsavesymbol{}")

    def handle_outofcombatsymbol(self, symbol):
        self.write(r"\outofcombatsymbol{}")

    def handle_multiroundactionsymbol(self, symbol):
        self.write(r"\multiroundactionsymbol{}")
    
    def handle_actionsymbol(self, symbol):
        self.write(r"\actionsymbol{}")

    def handle_reactionsymbol(self, symbol):
        self.write(r"\reactionsymbol{}")

    # def handle_eldersign(self, symbol):
    #     self.write(r"\eldersign{}")

    def handle_abilitybulletsymbol(self, symbol):
        self.write(r"\abilitybulletsymbol{}")

    def handle_savesymbol(self, symbol):
        self.write(r"\savesymbol{}")

    def handle_freesavesymbol(self, symbol):
        self.write(r"\freesavesymbol{}")

    def handle_saveorfreesavesymbol(self, symbol):
        self.write(r"\saveorfreesavesymbol{}")

    def handle_auxiliarysymbol(self, symbol):
        self.write(r"\auxiliarysymbol{}")

    def handle_antagonistsymbol(self, symbol):
        self.write(r"\antagonistsymbol{}")

    def handle_fatediesymbol(self, symbol):
        self.write(r"\fatediesymbol{}")

    def handle_nofatediesymbol(self, symbol):
        self.write(r"\nofatediesymbol{}")

    def handle_skilldiesymbol(self, symbol):
        self.write(r"\skilldiesymbol{}")

    def handle_vschecksymbol(self, symbol):
        self.write(r"\vschecksymbol{}")

    def handle_gmfiatsymbol(self, symbol):
        self.write(r"\gmfiatsymbol{}")

    def handle_vssavesymbol(self, symbol):
        self.write(r"\vssavesymbol{}")

    def handle_actionchecksymbol(self, symbol):
        self.write(r"\actionchecksymbol{}")

    def handle_actionsavesymbol(self, symbol):
        self.write(r"\actionsavesymbol{}")

    def handle_actionauxiliarysymbol(self, symbol):
        self.write(r"\actionauxiliarysymbol{}")

    #
    # Corollaries
    #
    def start_corollary(self, symbol):
        self.write(r"\begin{corollary}")
    
    def end_corollary(self, symbol):
        self.write(r"\end{corollary}")

    def start_corollary(self, symbol):
        self.write(r"\begin{corollary}")

    def start_corollarytitle(self, symbol):
        self.write("[")
    
    def end_corollarytitle(self, symbol):
        self.write("]")
    
    handle_corollarybody = no_op
    
    def end_corollary(self, symbol):
        self.write(r"\end{corollary}")
        return

    #
    # Pass through simple tags straight to latex (e.g. handle pass through
    # elements by defining a \newcommand{\tag}{...} in the latex preamble)
    #
    def get_pass_through_elements(self):
        return ("emdash", "optionalsymbol", "daggersymbol", )

    def pass_through_handler(self, pass_through_element):
        self.write(r"\%s " % pass_through_element.tag)
        return
    
    #
    # Principles
    #
    handle_principlebody = no_op

    def start_principle(self, symbol):
        self.write(r"\begin{principle}")
    
    def end_principle(self, symbol):
        self.write(r"\end{principle}")

    def start_principletitle(self, symbol):
        self.write("[")
    
    def end_principletitle(self, symbol):
        self.write("]")
        
    def handle_arrowleft(self, symbol):
        self.write("\\arrowleft{}")

    handle_ability_title = no_op

    def handle_ability_id(self, ability_id):        
        self.write("ID: %s\\\n" % ability_id) 

    start_ability_group = no_op
    def end_ability_group(self, ability_group):
        self.write("%s\n" % normalize_ws(ability_group.text))
        return

    start_ability_class = no_op
    def end_ability_class(self, ability_class):
        self.write("%s\n" % normalize_ws(ability_class.text))
        return

    start_action_points = no_op
    def end_action_points(self, action_points):
        self.write("%s\n" % normalize_ws(action_points.text))
        return

    def handle_hlink(self, hlink):
        url = hlink.get("url")
        text = utils.contents_to_string(hlink)
        self.write(r"\href{%s}{%s}" % (url, text))
        return    
    
    def handle_ampersand(self, and_element):
        self.write("\\&")

    def handle_copyright(self, _):
        self.write(r"\copyright{}")

    def handle_ccby(self, _):
        self.write(r"\ccby{}")

    def handle_includepdf(self, includepdf):
        fname = includepdf.get("fname")        
        self.write(r"\includepdf[pages=-]{%s}" % fname + NEWLINE)
        #self.write(r"\ccby{}")

    def handle_endash(self, _):
        # We can't replace this with a passthrough because we'd have to call the
        # latex command \endash and latex reservers names that start with \end
        # for ending environments
        self.write(r"\textendash{}")

    def handle_versus(self, _):
        self.write(r"\versus ")

    def handle_lore(self, element):
        self.write(r"\lore ")

    def handle_martial(self, element):
        self.write(r"\martial ")

    def handle_percent(self, element):
        self.write(r"\% ")

    def handle_general(self, element):
        self.write(r"\general ")
        return    

    def handle_magical(self, element):
        self.write(r"\magical ")
        return    

    def handle_geqqsymbol(self, geqq_element):
        self.write(r"$\stackrel{\scriptscriptstyle ?}{\geq}{}$")
        return

    def handle_leqqsymbol(self, geqq_element):
        self.write(r"$\stackrel{\scriptscriptstyle ?}{\leq}{}$")
        return

    def handle_leqsymbol(self, leq_element):
        self.write(r"$\leq$")
        return

    def handle_ltsymbol(self, leq_element):
        self.write("$<$")
        return

    def handle_gtsymbol(self, leq_element):
        self.write("$>$")
        return

    def handle_geqsymbol(self, geq_element):
        self.write(r"$\geq$")
        return

    def handle_br(self, br): 
        length = br.attrib.get("length")
        # self.write(r"\ifvmode\else\newline\fi{}")
        self.write(r"\mdbr ")
        # if length:
        #     assert float(length)
        #     #     self.write(r" \\ ")
        #     self.write(r"\ifvmode\else\\[%s\baselineskip]\fi{}" % length)
        # else:
        #     self.write(r"\ifvmode\else\\\fi{}")
        #     #     self.write(r" \\[%s\\baselineskip] " % length)
        return

    def handle_newpage(self, newpage):
        self.write(r"\ifvmode\else\newpage\fi{}")
        return

    #
    # References
    #
    def __handle_ref(self, ref):
        tag = ref.tag

        if tag == "chapterref":
            ref_name = "Chapter"
        elif tag == "sectionref":
            ref_name = "Section"
        elif tag == "tableref":
            ref_name = "Table"
        elif tag == "figureref":
            ref_name = "Figure"
        else:
            raise Exception(f"Unknown ref type?! {ref.tag}")

        label = ref.get("label")
        on_page = attrib_is_true(ref, "on-page")
        if label and on_page:
            page_ref = r" on page~\pageref{%s}" % label
        else:
            page_ref = ""
        
        self.write(ref_name + r"~\ref{%s}" % label + page_ref)        
        return
    handle_chapterref = __handle_ref
    handle_sectionref = __handle_ref
    handle_tableref = __handle_ref
    handle_figureref = __handle_ref

    def handle_pageref(self, pageref):
        """Page refs are a bit different from other refs."""
        label = pageref.get("label")        
        self.write(r"page~\pageref{%s}" % normalize_ws(label))
        return
    
    def handle_index(self, index):
        """Put the index in the document where the <index/> element occurs."""
        self.write(r"\clearpage" + NEWLINE)               
        self.write(r"\addcontentsline{toc}{chapter}{Index}" + NEWLINE)
        self.write(r"\printindex" + NEWLINE)
        return

    #
    #
    #
    handle_archetypelevel = no_op
    
    def handle_leveltitle(self, archetype_level_title):
        levelnumber = archetype_level_title.get("levelnumber", -1)        
        self.write(r"\subsection{Level {%s}}" % levelnumber)

    def start_playexample(self, playexample):
        self.write("\\begin{playexample}\n")
        return

    def end_playexample(self, playexample):
        self.write(playexample.text)                
        self.write("\\end{playexample}\n")
        return

    handle_level = no_op
    def start_leveltitle(self, level_title):
        self.write(r"\subsection*{")
        return
    def end_leveltitle(self, level_title):
        self.write("}")
        return


    #
    # Text with emphasis
    #
    def start_emph(self, emph):
        self.write(r"\begin{mdemph}")
        return

    def end_emph(self, emph):
        # latex environments eat trailing space. The trailing {} fixes this.
        self.write(r"\end{mdemph}{}")
        return


    #
    # Text with emphasis but less emphasis than emph.
    #
    def start_italic(self, _):
        self.write(r"\begin{itshape}")
        
    def end_italic(self, _):
        self.write(r"\end{itshape}")


    #
    # "Quotes" latex style.
    #
    def start_quotemarks(self, quote):
        self.write(r"\begin{mdquotemarks}")
        
    def end_quotemarks(self, quote):
        self.write(r"\end{mdquotemarks}")
        
    
    def start_dropcap(self, dropcap):
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
            self.write(" ".join(words))
        return

    def end_dropcap(self, emph):
        #self.write(r"\end{mddropcapbody}")
        #self.write(r"}")
        # latex environments eat trailing space. The trailing {} fixes this.
        #self.write(r"\end{mdemph}{}")
        return


    def start_equation(self, equation):
        self._equation_first_line = True
        self.write(
            "\\begin{tabbing}\n "
            "\\hspace*{0.5cm}\\= \\kill \\nopagebreak \n")
        return

    def end_equation(self, equation):
        self.write("\\end{tabbing}\\vspace{-0.5cm}\n ")
        return


    def start_line(self, line):
        """
        Start equation line.
        
        """
        if not self._equation_first_line:
            self.write("\\> ") 
        self._equation_first_line = False
        if line.text:
            self.write(" %s " % normalize_ws(line.text))
        return

    def end_line(self, line):
        self.write("\\\\\n ")
        return


    def start_bold(self, _):
        self.write(r"\begin{mdbold}")
        return
    def end_bold(self, _):
        self.write(r"\end{mdbold}")
        return

    def start_smaller(self, smaller):
        # smaller text
        self.write(r"\begin{smaller}")
        # smaller vertical space in lists etc.
        self.write(r"\setlist{nosep}")        
        return
    
    def end_smaller(self, smaller):
        self.write(r"\end{smaller}")
        return

    def process_plain_text(self, text):
        """
        Handles blocks of plain text with no embedded elements in it.

        """
        if text is not None:
            # Makes some effort to make the resulting .tex semi-readable.
            # Also it's a little careful about whitespace because tex is
            # brittle around certain whitespace.
            lines = utils.wrap_text(text)
            self.writelines(lines)

    def start_indent(self, indent):
        self.write(r"\begin{mdindent}")        
    def end_indent(self, indent):
        self.write(r"\end{mdindent}")

    #
    # A quote
    #
    def start_quote(self, quote):
        self.write(r"\begin{mdquote}")
        
    def end_quote(self, quote_entry):
        self.write(r"\end{mdquote}")

    #
    # Am epigraph
    #

    #
    # FIXME DROP EPIGRAPH IN XML FOR SLUG.
    #
    # def start_epigraph(self, quote):
    #     self.write(r"\begin{mdepigraph}")
        
    # def end_epigraph(self, quote_entry):
    #     self.write(r"\end{mdepigraph}")

    def start_slug(self, slug):
        if slug.attrib.get("slugAfterChapterTitle"):
            self.write(r"\epigraph{")
        else:
            self.write(r"\begin{mdepigraph}")
        return
        
    def end_slug(self, slug):
        if slug.attrib.get("slugAfterChapterTitle"):
            self.write(r"}")
        else:
            self.write(r"\end{mdepigraph}")
        return

    #
    # Index Entries
    #
    def start_indexentry(self, _):
        # We need to be able to defer index entries in tables.
        self.index_entry = IndexEntry()
        self.push_buffer()
        return
    
    def end_indexentry(self, _):
        self.index_entry.text = self.get_buffer_str(strip=True)
        assert self.index_entry.entry
        if self.table:
            # If it's an index in a table then save the index info and
            # defer writing the index entry till the end of the table.
            pass
        else:
            self.write_index_entry(self.index_entry)
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
        self.write(r"\index{%s}" % entry_str)

        for subentry in entry.subentries:        
            sanitized_subentry = sanitize_index_text(subentry)            
            subentry_str = (
                r"\index{%s!%s}"
                % (entry_str, sanitized_subentry))
            self.write(subentry_str)

        for see in entry.sees:                    
            sanitized_see = sanitize_index_text(see)
            see_str = r"\index{%s|see {%s}}" % (entry_str, sanitized_see)
            self.write(see_str)

        for defn in entry.definitions:                    
            sanitized_defn = sanitize_index_text(defn)
            defn_str = (
                r"\index{%s" 
                r"!aaaaaaaa@\empty \igobble |seealso {%s}}"
                % (entry_str, sanitized_defn))
            self.write(defn_str)
        return

    #
    #
    #
    
    # word definitions
    def start_defn(self, defn):
        self.write(r"\begin{defn}")
        return
    def end_defn(self, defn):
        self.write(r"\end{defn}")
        return

    handle_metric = no_op
    handle_imperial = no_op

    def start_p(self, paragraph):
        """
        Start paragraph.

        """
        self.write("\n\n")

        # turn of paragraph indentation?
        no_indent = attrib_is_true(paragraph, "noindent")
        if no_indent:
            self.write("\\noindent ")            
        return

    def end_p(self, paragraph):
        self.write("\n\n")
        return

    def start_design(self, design):
        if config.print_design_notes:
            self.write("\n\n")
            self.write(design.text)        
        return

    def end_design(self, design):
        self.write("\n\n")
        return

    def start_provenance(self, provenance):
        self.write("\n\n")
        if config.print_provenence_notes:
            self.write("\\begin{center}")
            self.write(r"\\begin{minipage}[c]{0.9\linewidth}")
            self.write(r"\\rpgprovenancesymbol\\hspace{0.2em}") 
            self.write(provenance.text)        
        return

    def end_provenance(self, provenance):
        if config.print_provenence_notes:
            self.write("\\end{minipage}")        
            self.write("\\end{center}")
            self.write("\n\n")
        return

    #
    # Title Page
    #
    def start_titlepage(self, chapter):
        self.write(r"\begin{mdtitlepage}")
        return

    def end_titlepage(self, chapter):
        self.write(r"\end{mdtitlepage}")
        return    
    
    def start_title(self, title):
        """Title page title."""
        self.write(r"\begin{mdtitle}")
        return

    def end_title(self, section_title):
        self.write(r"\end{mdtitle}")
        return

    def start_subtitle(self, title):
        """Title page subtitle."""
        self.write(r"\begin{mdsubtitle}")
        return

    def end_subtitle(self, section_title):
        self.write(r"\end{mdsubtitle}")
        return

    def start_subsubtitle(self, title):
        self.write(r"\begin{mdsubsubtitle}")
        return

    def end_subsubtitle(self, section_title):
        self.write(r"\end{mdsubsubtitle}")
        return

    def start_author(self, author):
        self.write(r"\begin{mdauthor}")
        return

    def end_author(self, author):
        self.write(r"\end{mdauthor}")
        return

    def start_version(self, version):
        self.write(r"\begin{mdversion}Version: ") 
        return
    
    def end_version(self, npchps): 
        self.write(r"\end{mdversion}")
        return
    
    #
    #
    #
    def start_caption(self, caption): 
        self.write(r"\caption{%s}" % caption.text)
        return

    def end_caption(self, caption):
        return    

    #
    # Chapters, Sections, etc..
    #

    # Chapters
    handle_chapter = no_op
    def start_chaptertitle(self, chapter_title):
        self.write(r"\begin{mdchaptertitle}")
        return

    def end_chaptertitle(self, chapter_title):
        # If we have a label it has to go after the chapter title!
        # (otherwise the label isn't set correctly,.. because of NewEnviron).
        label = chapter_title.attrib.get("label")
        if label:
            self.write(r"\label{%s}" % label + NEWLINE)
        self.write(r"\end{mdchaptertitle}" + NEWLINE)
        self.write(NEWLINE)
        return

    # Sections
    handle_section = no_op
    def start_sectiontitle(self, section_title):
        #self.push_buffer()
        self.write(r"\begin{mdsectiontitle}")
        return

    def end_sectiontitle(self, section_title):
        #stripped_term = self.get_buffer_str(strip=True)
        #self.write(stripped_term)
        label = section_title.attrib.get("label")
        if label:
            self.write(r"\label{%s}" % label)
        self.write(r"\end{mdsectiontitle}" + NEWLINE)
        return

    # Subsections
    handle_subsection = no_op
    def start_subsectiontitle(self, section_title):
        self.write(r"\subsection{")
        return
    def end_subsectiontitle(self, section_title):
        self.write("}")
        return

    # Subsubsections
    handle_subsubsection = no_op
    def start_subsubsectiontitle(self, title):
        title_category = title.attrib.get("titlecategory")  
        if (title_category == "antagonist-ability" or
            title_category == "ability"):       
            symbol = r"\abilitysubsubsectionsymbol "
        else:
            symbol = r"\subsubsectionsymbol "
        self.write(r"\subsubsection*{" + symbol)
        return
    def end_subsubsectiontitle(self, title):
        self.write("}")
        return    
 
    # Small Title (not really a division.. just a little header thing)
    def start_smalltitle(self, title):
        """
        A little header title (smaller than a subsubsection).

        """
        # suggest to latex that if we have to insert a page break
        # we'd much rather that was done before the little header
        # than after it.
        self.write(
            r"\pagebreak[2]"
            r"\begin{mdbold}\eldersign\rpgsmalltitlefont\small{}"
            r"\nopagebreak[2]")
        return
    
    def end_smalltitle(self, title):
        self.write(r"\end{mdbold}")
        return    

    
    
    #
    #
    #
    def start_img(self, img):        
        #self.write("\t\\begin{center}\n")
        
        # optionally draw a box around the image
        # (for debugging)
        #if config.draw_imgs:
        #if config.debug_outline_images:                
        #self.write("\\fbox{")

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
        self.write(r"\includegraphics{%s}" % (filename) + NEWLINE)
        return

    def end_img(self, img):
        self.write("\\end{adjustbox}\n")
            
        if img.text is not None:
            self.write("\t%s\n" % img.text)

        # title
        if "title" in img.attrib:
            title = img.get("title")
            self.write("\\emph{%s}" % title)
            
        #self.write("\t\\end{center}\n")
        return


    def start_handout(self, handout):
        """
        Handout is a figure+image hybrid on its own page and with a blank
        following page.

        """                
        self.write("\\newpage\n")
        self.write("\\pagestyle{empty}\n")
        self.write("\\begin{figure*}[h!t]\n")
        self.write("\\begin{center}\n")

        if config.draw_imgs:
            if config.debug_outline_images:
                self.write("\\fbox{")
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
            self.write("\\addcontentsline{loa}{section}{%s}"
                                  % resource.get_contents_desc())
        else:
            raise Exception("Handout missing image src or id!")

        if not exists(filename):
            raise Exception("Handout image does not exist: %s" % filename)

        # handout image without a box
        self.write("\t\\includegraphics[scale=%s]{%s}\n"
                              % (handout.get("scale", default="1.0"), filename))
        return

    def end_handout(self, handout):
        if handout.text is not None:
            self.write("\t%s\n" % handout.text)
        if config.debug_outline_images:
            self.write("}")
        self.write("\\end{center}\n")
        self.write("\\end{figure*}\n")
        self.write("\\cleardoublepage\n")
        self.write("\\newpage\n")
        self.write("\\cleardoublepage\n")
        self.write("\\newpage\n")
        self.write("\\pagestyle{headings}\n")
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

        self.write("\\begin{%s}[%s]\n" % (figure_name, position))
        return

    def end_figure(self, figure):
        caption = figure.get("caption")
        if caption is not None:
            self.write(r"\caption{%s}" % caption + NEWLINE)        

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

        self.write(r"\end{%s}" % figure_name + NEWLINE*3)
        return

    # An image which the text wraps around
    def start_wrapimg(self, wrapimg):
        position = wrapimg.get("position", "l")
        width = wrapimg.get("scale", default="1.0") + "\\textwidth"
        
        self.write(
            "\\begin{wrapfigure}{%s}{%s}\n"
            % (position, width))

        if config.draw_imgs:
            if config.debug_outline_images:
                self.write("\\fbox{")

        self.write("\\centering\n")

        filename = self._get_img_filename(wrapimg)

        # image without a box
        self.write(
            "\t\\includegraphics[width=%s]{%s}\n"
            % (width, filename))        
        return

    
    def end_wrapimg(self, wrapimg):
        if config.debug_outline_images:
            self.write("}")

        caption = wrapimg.get("caption")
        if caption is not None:
            self.write("\\caption{%s}\n" % caption)
        self.write("\\end{wrapfigure}\n")
        return

    
    def start_olist(self, enumeration):
        """
        Start enumeration, ordered list of things.

        """
        # the [i] gets us roman numerals in the enumeration
        self.write("\\begin{enumerate}[label = (\\roman*)]\n")
        return

    def end_olist(self, enumeration):
        self.write("\\end{enumerate}\n")
        return

    # a list of definitions
    def start_descriptions(self, description_list):
        self.write("\\begin{description}[topsep=5pt,itemsep=5pt]\n")
        self.terms_on_new_line = description_list.get("termonnewline", False)
        return

    def end_descriptions(self, description_list):
        # note seeing weird artifacts in embedded latex lists without the extra newline
        self.write("\\end{description}\n\n")
        return

    
    def start_term(self, term):
        """
        List items for a descriptions list

        """
        self.write(r"\item[")
        self.push_buffer()
        return
    
    def end_term(self, term):
        # strip the term string to try and avoid
        # "! Paragraph ended before \@item was complete." errors.
        stripped_term = self.get_buffer_str(strip=True)
        self.write(stripped_term)
        self.write("]")

    def start_description(self, description):
        return

    def end_description(self, description):
        return

    def start_list(self, list_element):
        self.write("\\begin{itemize}\n")
        return

    def end_list(self, list_element):
        self.write("\\end{itemize}\n")
        return

    def handle_li(self, list_item):
        """
        Start list item.

        """
        self.write(r"\item ")
        return

    def start_comment(self, comment):
        return

    def end_comment(self, comment):
        return

    def start_branch(self, branch_node):
        return

    def start_branchtitle(self, branchtitle_node):
        self.write("\\subsubsection*{")
        return

    def end_branchtitle(self, branchtitle_node):
        
        self.write("}")
        return

    def start_branchdescription(self, branchdescription_node):
        return

    def end_branchdescription(self, branchtitle_node):
        self.write("\\begin{description}\n")
        return

    def end_branch(self, branch_node):
        self.write("\\end{description}\n")
        return

    
    def start_path(self, path_node):
        # pathtitle is optional
        has_pathtitle = False
        for child in path_node:
            if child.tag == "pathtitle":
                has_pathtitle = True
        if not has_pathtitle:
            self.write(f"\\item[\\em❧] ")
        return

    def end_path(self, path_node):
        return

    def start_pathtitle(self, pathtitle_node):
        self.write(f"\\item[\\em❧ ")
        return

    def end_pathtitle(self, pathtitle_node):
        self.write("]")
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
        self.write(NEWLINE + r"\vspace{-0.3cm}")

        # don't have paragraph indents buggering up our table layouts
        self.write(r"\noindent{}" + NEWLINE)
        
        # wrap single page tables in a table environment
        # (we use xtabular for multi-page tables and the table environment
        # confuses it about page size).        
        if self.table.figure:
            if self.table.sideways:
                self.write(r"\begin{sidewaystable*}[htp]" + NEWLINE)
            elif self.table.fullwidth:
                self.write(r"\begin{table*}[ht]" + NEWLINE)
            else:
                self.write(r"\begin{table}[ht]" + NEWLINE)
        else:
             self.write(r"\begin{table}[H]" + NEWLINE)             
            
        self.write(r"\begin{center}" + NEWLINE)

        # Change the separation between table columns??
        tabcolsep = table.get("colsep")
        if tabcolsep is not None:
            self.write(
                r"\setlength{\tabcolsep}{%s\tabcolsep}" % tabcolsep +
                NEWLINE)

        # Tabular
        if self.table.fullwidth:
            table_width = r"\textwidth"
        else:
            table_width = r"\linewidth"
        self.write(
            r"\begin{tabularx}{%s}{%s}" 
            % (table_width, table_spec_str) + NEWLINE)
        return

    def end_table(self, table):
        assert self.table is not None

        # normal table environment
        self.write(r"\end{tabularx}" + NEWLINE)
        
        # Add labels for references
        if self.table.label:
            label = self.write(r"\label{%s}" % self.table.label)

        self.write(r"\end{center}" + NEWLINE)

        # Change the separation between table columns??
        tabcolsep = table.get("colsep")
        if tabcolsep is not None:
            self.write(r"\setlength{\tabcolsep}{\originaltabcolsep}" + NEWLINE)

        # handle any table indexes now!
        for index_entry  in self.table.index_entries:
            self.write_index_entry(index_entry)

        # The table caption from the <tabletitle> element, if we have one.
        if self.table.title:
            self.write(self.table.title)
            
        if self.table.figure:
            if self.table.sideways:
                self.write(r"\end{sidewaystable*}" + NEWLINE)        
            elif self.table.fullwidth:
                self.write(r"\end{table*}" + NEWLINE)
            else:
                self.write(r"\end{table}" + NEWLINE)
                # vertical space
                #self.write("\n\\\\\n")
        else:
            self.write(r"\end{table}" + NEWLINE)            
        self.write("\n\n")

        self.table = None
        assert self.table is None
        return

    # tablespec and it's children are parsed by the table element (it's special)
    handle_tablecategory = no_op
    handle_tablespec = no_op
    handle_fixed = no_op
    handle_elastic = no_op

    # 
    def start_tabletitle(self, table_title):
        self.push_buffer()
        table_title = table_title.text
        table_title = table_title.strip()
        if table_title:        
            self.write(r"\captionof{table}{")

    def end_tabletitle(self, table_title):
        self.write("}")
        self.table.title = self.get_buffer_str()

    # Tablelabel is also parsed by the table
    def handle_tablelabel(self, label):
        self.table.label = label.text.strip()

    def handle_tablesection(self, tablesection):
        self.write(r"\rpgtablesection{%s}" % tablesection.text.strip())
        return

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

        # do we want to color the row?
        color = None
        if table_row.tag == "tableheaderrow":
            self.write(
                r"\rowcolor{tableheadercolor}")        
        elif self.table.current_row % 2 == 1:
            self.write(
                r"\rowcolor{tableoddrowcolor}")

        # Add a horizontal line at the top of the first row of the table
        # (this has to come after the \rowcolor command above).
        if pp.is_first_table_row(table_row):
            self.write(r"\toprule " + NEWLINE)
        return

    def end_tablerow(self, table_row):
        if pp.is_last_table_row(table_row):
            self.write(
                r"\\ \bottomrule" +
                NEWLINE)
        else:
            self.write(
                r"\\ " +
                NEWLINE)
        return

    start_tableheaderrow = start_tablerow
    end_tableheaderrow = end_tablerow

    def start_td(self, td, header=False):
        """
        Start table data.

        """
        # get the number of columns wide this cell should be.
        align = td.get("align", "l")
        width = int(td.get("width", 1))

        # make cells wider than one column?
        if width > 1:
            percent_width = self.table.get_columns_percent_width(width)
            cell_align = ("p{%s\\hsize+%s\\tabcolsep}"
                          % (percent_width, 2*(width-1)))
            self.write("\\multicolumn{%s}{%s}{"
                              % (width, cell_align))
        #else:
        if align == "l":
            alignment = None
        elif align == "c":
            #self.write(r"\multicolumn{1}{c}{")
            self.write(r"\mdtblcenter{")
        elif align == "r":
            #alignment = r"\raggedleft{}"
            #self.write(r"\multicolumn{1}{r}{")
            alignment = None
            pass
        else:
            raise Exception(f'Unknown table cell alignments "{align}"')

        # cell color?
        if header:
            cell_color = r"\cellcolor{tableheadercolor}\bfseries "
        else:
            cell_color = None
        if cell_color:
            self.write(cell_color)
           
        self.table.current_column = (
            (self.table.current_column + width) % self.table.number_of_columns)

        if header:
            self.write(r"\begin{mdbold}")
        return

    def end_td(self, td, header=False):
        if header:
            self.write(r"\end{mdbold}")

        # get the number of columns wide or rows high this cell should be.
        width = int(td.get("width", 1))        
        # get the text alignment within the cell.
        align = td.get("align", "l")

        if align == "c":
            self.write(r"}")
        
        # Close out the multicolumn?
        if width > 1:
            # multicolumn table data
            self.write("}")
            #pass
        
        if self.table.current_column != 0:
            self.write(" & ")
        return    

    # table headers are a type of table data
    def start_th(self, th):
        return self.start_td(th, header=True)
    
    def end_th(self, th):
        return self.end_td(th, header=True)        

    def handle_tableofcontents(self, table_of_contents):
        self.write(r"\tableofcontents" + NEWLINE)

    def handle_listoffigures(self, list_of_figures):
        self.write(r"\listoffigures{}")

    def handle_listofart(self, list_of_art):
        return

    def handle_list_of_tables(self, list_of_tables):
        self.write(r"\listoftables" + NEWLINE)

    def start_label(self, label):
        self.write(r"\label{")

    def end_label(self, label):
        self.write("}")

    def start_fourcolumns(self, threecolumns):
        self.write(r"\onecolumn\begin{multicols}{4}" + NEWLINE)

    def end_fourcolumns(self, ability_group):
        self.write(r"\end{multicols}\twocolumn" + NEWLINE)
    
    def handle_attempt(self, success):
        self.write(r"\rpgattempt{}")

    def handle_success(self, success):
        self.write(r"\rpgsuccess{}")

    def handle_fail(self, fail):
        self.write(r"\rpgfail{}")

    def handle_eg(self, fail):
        self.write(r"e.g.\@{}")

    def handle_ie(self, fail):
        self.write(r"i.e.\@{}")

    def handle_aka(self, fail):
        self.write(r"a.k.a.\@{}")

    def handle_etc(self, fail):
        self.write(r"etc.\protect\@{}")

    def handle_nb(self, fail):
        self.write(r"\textbf{N.B.\@} ")

    def handle_notapplicable(self, fail):
        self.write("n/a")

    #def handle_dpool(self, fail): # What's this for?
    #    self.write(r"\dpool{}")

    def handle_vspace(self, vspace):
        length_str = vspace.attrib.get("length", "1.0")
        length = convert_str_to_float(length_str)
        #self.write(r"\vspace{%s\drop}\\" % length + NEWLINE)
        self.write(r"\ifvmode\else\vspace{%s\drop}\\\fi{}" % length + NEWLINE)


    def handle_hspace(self, hspace):
        length_str = hspace.attrib.get("length", "1.0")
        length = convert_str_to_float(length_str)
        self.write(r"\hspace{%sex}" % length)
    
    
    #
    # Monster blocks.
    #

    def start_monsterblock(self, monsterblock):
        self.write(r"\begin{minipage}{\linewidth}")
        return

    def end_monsterblock(self, monsterblock):
        self.write(r"\end{minipage}")
        return

    def start_mbtitle(self, mbtitle):
        self.write(r"\mbsep{}\begin{mbtitle}")
        return

    def end_mbtitle(self, mbtitle):
        self.write(r"\end{mbtitle}\noindent{}")
        return
    
    def start_mbtags(self, mbtags):
        self.write(r"\begin{mbtags}")
        return

    def end_mbtags(self, mbtags):
        self.write(r"\end{mbtags}\noindent")
        return

    def start_mbdefence(self, mbac):
        self.write(r"\textbf{Defence: }\begin{mbdefence}")
        return

    def end_mbdefence(self, mbac):
        self.write(r"\end{mbdefence}\enspace{}")
        return

    def start_mbhp(self, mbhp):
        self.write(r"\textbf{HP: }\begin{mbhp}")
        return
    
    def end_mbhp(self, mbhp):
        self.write("\\end{mbhp}")
        return

    def start_mbmove(self, mbmove):
        self.write(r"\textbf{Mv: }\begin{mbmove}")
        return

    def end_mbmove(self, mbmove):
        self.write("\\end{mbmove}")
        return

    def start_mbinitiative(self, mbinitiative):
        self.write(r"\textbf{Init: }\begin{mbinitiative}")
        return
    def end_mbinitiative(self, mbinitiati):
        self.write(r"\end{mbinitiative}")
        return
    
    def start_mbmagic(self, mbmagic):
        self.write(r"\textbf{Magic: }\begin{mbmagic}")
        return
    def end_mbmagic(self, mbmagic):
        self.write("\\end{mbmagic}")
        return
    
    def start_mbmettle(self, mbmettle):
        self.write(r"\textbf{Mettle: }\begin{mbmettle}")
        return
    def end_mbmettle(self, mbmettle):
        self.write("\\end{mbmettle}")
        return
    
    def start_mbluck(self, mbluck):
        self.write(r"\textbf{Luck: }\begin{mbluck}")
        return
    def end_mbluck(self, mbluck):
        self.write("\\end{mbluck}")
        return
    

    def start_mbstr(self, mbstr):
        self.write(r"\\\textbf{Str: }\begin{mbattr}")
        return
    def end_mbstr(self, mbmagic):
        self.write("\\end{mbattr}")
        return
    def start_mbend(self, mbend):
        self.write(r"\textbf{End: }\begin{mbattr}")
        return
    def end_mbend(self, mbend):
        self.write("\\end{mbattr}")
        return

    def start_mbag(self, mbag):
        self.write(r"\textbf{Ag: }\begin{mbattr}")
        return
    def end_mbag(self, mbag):
        self.write("\\end{mbattr}")
        return
    
    def start_mbspd(self, mbspd):
        self.write(r"\textbf{Spd: }\begin{mbattr}")
        return
    def end_mbspd(self, mbspd):
        self.write("\\end{mbattr}")
        return
    
    def start_mbper(self, mbper):
        self.write(r"\textbf{Per: }\begin{mbattr}")
        return
    def end_mbper(self, mbper):
        self.write("\\end{mbattr}")
        return
    
    def start_mbwil(self, mbwil):
        self.write(r"\textbf{Will: }\begin{mbattr}")
        return
    def end_mbwil(self, mbwil):
        self.write("\\end{mbattr}")
        return

    
    def start_mbarmour(self, mbarmour):
        #self.write("\\begin{small}")
        return        
    def end_mbarmour(self, mbarmour):
        #self.write("\\end{small} & %\n")
        #self.write("\n")
        return

    def start_mbabilities(self, mbabilities):
        #self.write(r"\textbf{Abilities}: ")
        return
    def end_mbabilities(self, mbabilities):
        #self.write("\n")
        return

    def start_mbaspects(self, mbaspects):
        self.write(r"\textbf{Aspects:} ")
        return
    def end_mbaspects(self, mbaspects):
        self.write("\\\\\n")
        return
    
    def start_mbdescription(self, mbdescription):
        self.write(r"\vspace{1.0mm}"
                              r"\textbf{Description:}"
                              r"\hfill"
                              r"\break"
                              r"\vspace{-0.3cm}")
        return
    def end_mbdescription(self, mbdescription):
        self.write("\n")
        return
    
    def start_mbnpc(self, mbnpc):
        return

    def end_mbnpc(self, mbnpc):
        self.write("\\newline{}")
        return

    def start_npcname(self, npcname):
        self.write(r"\textbf{Name: }\begin{npcname}")
        return
    def end_npcname(self, npcname):
        self.write("\\end{npcname} ")
        return
    
    def start_npchps(self, npchps):
        self.write(r"\textbf{HPs: }\begin{npchp}")
        return
    def end_npchps(self, npchps):
        self.write("\\end{npchp}")
        return

    def handle_inspiration(self, inspiration):
        img = inspiration.getparent()
        if "id" in img.attrib:
            resource_id = img.get("id")
            resource = self.db.resources.use(resource_id)
            sig = resource.get_sig()
            
            self.write(r"{\attributionfont %s}" % sig)
        else:
            raise Exception("Image inspiration missing id!")        
        return

    def handle_attribution(self, attribution):
        img = attribution.getparent()
        if "id" in img.attrib:
            resource_id = img.get("id")
            resource = self.db.resources.use(resource_id)
            sig = resource.get_sig()
            
            self.write(r"{\attributionfont %s}" % sig)
        else:
            raise Exception("Image attribution missing id!")
        return

    def handle_ellipsis(self, ellipsis):
        self.write(r"\ldots")

    def handle_hline(self, _):
        if self.table is None:
            self.write(
                r"\noindent"
                r"\rule{\columnwidth}{0.8pt}"
                r"\nopagebreak\vspace{-0.8em}")
        else:
            self.write(r"\hline ")
        return

    def handle_abilityref(self, ability_ref_node):
        ability_ref = abilities.AbilityRef()
        ability_ref.parse(ability_ref_node)
        ability = self.db.get_ability_from_ref(ability_ref)
        if ability is None:
            line_number = ability_ref_node.sourceline
            context = get_error_context(self.xml_fname, line_number)
            raise Exception(
                f"Can't find ability that abilityref is refering to! :"
                f"({ability_ref.get_id()}) in "
                f"{self.xml_fname}:{line_number}\n")
            
        name = ability.get_name()            
        rank_num_str = f" {ability_ref.get_rank()}"
        phrase = ability_ref.get_phrase() or ""
        if phrase:
            phrase_str = f"{phrase} "
        else:
            phrase_str = ""
        
        if ability_ref.is_permanent():
            is_permanent_str = " permanent"
        else:
            is_permanent_str = ""
        
        specializations = ability_ref.get_specializations_str()
        if specializations:
            specializations_str = f"{name}[{specializations}]"
        else:
            specializations_str = ""

        if ability_ref.get_id() == "aspect":
            self.write(
                r"\begin{mdbold}" + 
                phrase_str +
                " «Aspect» " +
                is_permanent_str +
                specializations_str +
                rank_num_str +
                r"\end{mdbold}")            
        else:
            self.write(
                r"\begin{mdbold}" +
                phrase_str +
                name +
                is_permanent_str +
                specializations_str +
                rank_num_str +
                r"\end{mdbold}")
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
        
        self.write(
            r"\begin{figure}[hbtp!]"
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
        self.write(
            r"\end{minipage}"
            r"\end{tcolorbox}"
            r"\end{figure}")
        return

    # FIXME: what is this for?
    def handle_details(self, _):        
        # self.write("\\paragraph*{Detials}")
        return        

    def handle_hfill(self, hfill):        
        self.write(r"\hfill")
        return

    def handle_spacer(self, spacer):        
        self.write(r"\mdspacer{}")
        return

    def handle_divider(self, divider):        
        char_code = 89 # standard
        if divider.attrib == "fancy":
            char_code = 80
        self.write(r"\centerline{\pgfornament[scale=0.14]{%s}}" % char_code)
        return    

    def _handle_short_measurement(self, sm):
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

        self.write(normalize_ws(distance_text).strip())
        return

    # Measurement Constants.
    handle_m05 = _handle_short_measurement
    handle_m2 = _handle_short_measurement  
    handle_m3 = _handle_short_measurement
    handle_m6 = _handle_short_measurement
    handle_m9 = _handle_short_measurement
    handle_m10 = _handle_short_measurement
    handle_m12 = _handle_short_measurement
    handle_m20 = _handle_short_measurement
    handle_m30 = _handle_short_measurement
    handle_m90 = _handle_short_measurement
    handle_m180 = _handle_short_measurement
    handle_km3 = _handle_short_measurement
    
    def _handle_sv(self, sv_element):
        """
        Shared formatting for all the skill values, e.g. <sv13/>
        
        """
        tag = sv_element.tag
        match_obj = _sv_regex.search(tag)
        if match_obj is not None:
            skill_value = match_obj[0]
            self.write(fr"SSV: {skill_value}")
        else:
            raise Exception(
                f"Unknown skill value check! {node_to_string(sv_element)}")

    handle_sv3 = _handle_sv 
    handle_sv5 = _handle_sv
    handle_sv7 = _handle_sv
    handle_sv9 = _handle_sv
    handle_sv11 = _handle_sv
    handle_sv13 = _handle_sv
    handle_sv15 = _handle_sv
    handle_sv17 = _handle_sv
    handle_sv19 = _handle_sv
    handle_sv21 = _handle_sv
    handle_sv23 = _handle_sv
    handle_sv25 = _handle_sv
    handle_sv27 = _handle_sv
    handle_sv29 = _handle_sv

    def handle_d20plusrank(self, tag):
        self.write(r"\fatediesymbol/\skilldiesymbol+Rank")

    
