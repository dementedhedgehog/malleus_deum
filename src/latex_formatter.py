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
    
    def __init__(self, latex_file):

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
        
        # must be a valid latex paper size
        if config.paper_size == "a4":
            paper_size = "a4paper"
        elif config.paper_size == "letter":
            paper_size = "letterpaper"
        else:
            raise Exception("Unknown paper size.  Pick one of [a4, letter] in config.py")
        
        self.latex_file.write(
            "\\documentclass[" + paper_size + ",twocolumn,oneside]{book}\n" 
            "\n"
            "\\usepackage[unicode]{hyperref} % for hyperlinks in pdf\n"
            "\\usepackage{caption}           % extra captions\n" 
            "\\usepackage{color}             % color.. what can I say\n"
            "\\usepackage{fancyhdr}          % header control\n" 
            "\\usepackage{fancybox}          % fancy boxes.. eg box outs\n" 
            "\\usepackage{graphicx}          % for including images\n" 
            "\\usepackage{fontspec}          % fine font control\n"
            "\\usepackage{titlesec}          % for fancy titles\n"
            "\\usepackage{lettrine}          % for drop capitals \n"            
            "\\usepackage{tabularx}          % for tables \n"            
            "\\usepackage[table]{xcolor}     % for tables with colour\n"
            "\\usepackage{booktabs}          % for tables\n"
            "\\usepackage{calc}              % for table width calculations\n"
            "\\usepackage{xcolor}            % for color aliases\n"            
            "\\usepackage{wallpaper}         % for the paper background\n"            
            "\\usepackage{enumerate}         % for roman numerals in enumerations\n"            
            "\\usepackage{lipsum}            % for generating debug text\n"
            "\\usepackage{wrapfig}           % sidebar thingy\n"
            "\\usepackage{makeidx}           % for building the index\n"
            "\\usepackage{amssymb}           % for special maths symbols, e.g. slanted geq\n"
            "\\usepackage{xtab}              % for multipage tables\n"
            "\\usepackage{rotating}          % for sidewaystable\n"
            "\\usepackage{parskip}           % non indented paragraphs\n"
            "\\usepackage{multicol}          % used for three column mode.\n"
            "\n"
            "% include subsubsections in the table of contents\n"
            "\\setcounter{tocdepth}{3}\n"
            "\n"
            "% fonts\n"
            #"\\newfontfamily{\\rim}[Path=fonts/, Scale=1.5]{Rat Infested Mailbox}\n"
            #"\\newfontfamily{\\dz}[Path=fonts/, Scale=2.5]{Deutsche Zierschrift}\n"
            #"\\newfontfamily{\\tkaqf}[Path=fonts/, Scale=2.5]{the King & Queen font}\n"
            "\\newfontfamily{\\cloisterblack}[Path=fonts/]{Cloister Black}\n"
            "\\newfontfamily{\\carolingia}[Path=fonts/]{Carolingia}\n"
            "\\newfontfamily{\\fontawesome}[Path=fonts/]{fontawesome-webfont.ttf}\n"
            "\\newfontfamily{\\wwdesigns}[Path=fonts/]{WWDesigns}\n"
            #"\\newfontfamily{\\symbolfont}[Path=fonts/, Scale=1.0]{rpg-icons}\n"
            "% fonts\n"
            "\\newfontfamily{\\rpgtitlefont}[Path=fonts/, Scale=10.0]{Dogma}\n"
            "\\newfontfamily{\\rpgchapterfont}[Path=fonts/, Scale=1.0]{Cloister Black}\n"
            "\\newfontfamily{\\rpgtitlesubtitlefont}[Path=fonts/]{Cloister Black}\n" 
            "\\newfontfamily{\\rpgtitleauthorfont}[Path=fonts/]{Dogma}\n"
            "\\newfontfamily{\\rpgdropcapfont}[Path=fonts/, Scale=1.2]{Cloister Black}\n"
            "\\newfontfamily{\\rpgdice}[Path=fonts/]{RPGDice}\n"
            "\n"            
            "\\newcommand{\\rpgsectionfont}{\cloisterblack}\n"
            "\\newcommand{\\rpgtableheaderfont}{\cloisterblack}\n"
            "\\newcommand{\\mbtagfont}{\cloisterblack}\n"
            "\n"            
            "% colours \n"
            "\\definecolor{maroon}{RGB}{128,0,0}\n"
            "\\definecolor{darkred}{RGB}{139,0,0}\n"
            "\\definecolor{barnred}{RGB}{124,10,2}\n"
            "\\definecolor{rosetaupe}{RGB}{144,93,93}\n"
            "\\definecolor{rosewood}{RGB}{101,0,11}\n"
            "\\definecolor{black}{RGB}{0,0,0}\n"
            "\n"
            "% colour aliases\n"
            "\\colorlet{rpgtitlefontcolor}{black}\n"
            "\\colorlet{rpgchapterfontcolor}{black}\n"
            "\\colorlet{rpgsectionfontcolor}{rosewood}\n"
            "\n"
            "% spacing \n"            
            "\\newlength\drop\n"
            "\\drop = 0.01\\textheight % drop is a vspace 1/100th the page text height.\n"
            "\n"
            "\\titleformat{name=\\chapter}[hang]\n"
            "   {\\Huge\\bfseries\\rpgchapterfont\\color{rpgchapterfontcolor}}\n"
            "   {}{1em}{}\n"
            "\n"
            "\\titleformat{\\section}\n"
            "  {\\rpgsectionfont\\LARGE\\color{rpgsectionfontcolor}}\n"
            "  {\\thesection}{0.5em}{}\n"
            "\n"
            "\\newcommand{\\rpgtableheader}{\\bfseries\\selectfont}{}\n"
            "\n"
            "\\newcommand{\\rpgtablesection}%"
            "  {\\rule{0pt}{3ex}\\rpgtableheaderfont\\bfseries}{}\n"
            "\n"
            "\\newcommand{\\reactionsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}R\\endgroup}"
            "  {reaction}}\n"
            "\n"
            "\\newcommand{\\startsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}1\\endgroup}"
            "  {start}}\n"            
            "\n"
            "\\newcommand{\\talksymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}t\\endgroup}"
            "  {talk}}\n"
            "\n"
            "\\newcommand{\\fastsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}2\\endgroup}"
            "  {fast}}\n"
            "\n"
            "\\newcommand{\\mediumsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}3\\endgroup}"
            "  {medium}}\n"
            "\n"
            "\\newcommand{\\slowsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}4\\endgroup}"
            "  {slow}}\n"
            "\n"
            "\\newcommand{\\startandreactionsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}1+R\\endgroup}"
            "  {startandreactionsymbol}}\n"
            "\n"
            "\\newcommand{\\mediumorslowsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}3/4\\endgroup}"
            "  {mediumorslowsymbol}}\n"
            "\n"
            "\\newcommand{\\resolutionsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}5\\endgroup}"
            "  {resolution}}\n"
            "\n"
            "\\newcommand{\\surprisesymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}s\\endgroup}"
            "  {surprise}}\n"
            "\n"
            "\\newcommand{\\ambushsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}a\\endgroup}"
            "  {ambush}}\n"
            "\n"
            "\\newcommand{\\initiativesymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}i\\endgroup}"
            "  {initiative}}\n"
            "\n"
            "\\newcommand{\\fightreachsymbol}\n"
            "  {\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}3:4\\endgroup}"
            "  {fight-reach}}\n"
            "\n"
            "\\newcommand{\\noncombatsymbol}"
            "{\\texorpdfstring{\\begingroup\\rpgdice\\selectfont{}n\\endgroup}"
            "{non-combat}}\n"
            "\n"
            "\n"
            "% the font for the body of the text\n"
            "\\setmainfont[Scale=0.95]{Linux Libertine O}\n"
            "\\setromanfont[\n"
            "  Mapping=tex-text, \n"
            "  Mapping=tex-text, \n"
            "  Ligatures={Common,Rare,Discretionary}\n"
            "  ]{Linux Libertine O}\n"
            "\n"
            "% special bullet symbols\n"
            "\\newcommand{\\rpgbullet}\n"
            "{\n"
            "   \\begingroup\n"
            "   \\wwdesigns\n"
            "   \\large\n"
            "   \\selectfont\n"
            "   \\char\"0043"
            "   \\endgroup\n"
            "}\n" 	
            ""
            "\\newcommand{\\facircle}\n"
            "  {\\begingroup\\fontawesome\\scriptsize\\selectfont\\char\"F111\\endgroup}\n"
            "\\newcommand{\\fatick}\n"  
            " {\\begingroup\\rpgdice\\selectfont{}y\\endgroup}\n"
            "\\newcommand{\\faquestion}\n"  
            " {\\begingroup\\fontawesome\\scriptsize\\selectfont\\symbol{\"F29C}\\endgroup}\n"
            "\\newcommand{\\facross}\n"  
            " {\\begingroup\\rpgdice\\selectfont{}x\\endgroup}\n"
            "\\newcommand{\\fastaro}\n"   
            " {\\begingroup\\fontawesome\\scriptsize\\selectfont\\symbol{\"F006}\\endgroup}\n"
            #"\\newcommand{\\faexclamation}\n"
            #" {\\begingroup\\fontawesome\\scriptsize\\selectfont\\symbol{\"F12A}\\endgroup}\n"
            "\n"
            "\\newcommand{\\dfour}\n" 
            " {\\begingroup\\rpgdice\\selectfont{}A\\endgroup}\n"
            "\\newcommand{\\dsix}\n"
            " {\\begingroup\\rpgdice\\selectfont{}B\\endgroup}\n"
            "\\newcommand{\\deight}\n"
            " {\\begingroup\\rpgdice\\selectfont{}C\\endgroup}\n"
            "\\newcommand{\\dten}\n"
            " {\\begingroup\\rpgdice\\selectfont{}D\\endgroup}\n"
            "\\newcommand{\\dtwelve}\n"
            " {\\begingroup\\rpgdice\\selectfont{}E\\endgroup}\n"
            "\\newcommand{\\dtwenty}\n"
            " {\\begingroup\\rpgdice\\selectfont{}F\\endgroup}\n"
            "\\newcommand{\\dany}\n"
            " {\\begingroup\\rpgdice\\selectfont{}G\\endgroup}\n"
            "\\newcommand{\\dpool}\n"
            " {\\begingroup\\rpgdice\\selectfont{}H\\endgroup}\n"
            "\\newcommand{\\firststage}\n"  
            " {\\begingroup\\rpgdice\\selectfont{}1\\endgroup}\n"
            "\\newcommand{\\secondstage}\n"
            " {\\begingroup\\rpgdice\\selectfont{}2\\endgroup}\n"
            "\\newcommand{\\thirdstage}\n"
            " {\\begingroup\\rpgdice\\selectfont{}3\\endgroup}\n"
            "\\newcommand{\\fourthstage}\n"
            " {\\begingroup\\rpgdice\\selectfont{}4\\endgroup}\n"
            "\\newcommand{\\fifthstage}\n"
            " {\\begingroup\\rpgdice\\selectfont{}5\\endgroup}\n"
            "\n"
            #"% marki \n"
            #"\\newcommand{\\marko}{\\facircleo\\,\\facircleo\\,\\facircleo}\n"
            #"\\newcommand{\\marki}{\\facircle\\,\\facircleo\\,\\facircleo}\n"
            #"\\newcommand{\\markii}{\\facircle\\,\\facircle\\,\\facircleo}\n"
            #"\\newcommand{\\markiii}{\\facircle\\,\\facircle\\,\\facircle}\n"
            "\n"
            "\\newcommand{\\rpginnateabilitysymbol}{\\fastaro}\n"
            "\\newcommand{\\rpginnatearchetypeabilitysymbol}{\\fastar}\n"
            "\\newcommand{\\rpgrecommendedabilitylevelsymbol}{\\faexclamation}\n"
            "\n"
            "\n"
            "\n"
            "% half symbol \n"
            u"\\newcommand{\\half}{½}\n"
            "% third symbol \n"
            u"\\newcommand{\\third}{⅓}\n"
            "% quarter symbol \n"
            u"\\newcommand{\\quarter}{¼}\n"

            "\n"
            "\\newcommand{\\lore}{%\n"
            "\\begingroup\\rpgdice\\selectfont{}l\\endgroup}\n"
            "\\newcommand{\\martial}{%\n"
            "\\begingroup\\rpgdice\\selectfont{}m\\endgroup}\n"            
            "\\newcommand{\\general}{%\n"
            "\\begingroup\\rpgdice\\selectfont{}g\\endgroup}\n"
            "\\newcommand{\\magical}{%\n"
            "\\begingroup\\rpgdice\\selectfont{}z\endgroup}\n"
            "\n"
            "\\renewcommand{\\labelitemi}{\\rpgbullet}\n"
            "\n"
            "\n"
            "% special provenance symbol\n"
            "\\newcommand{\\rpgprovenancesymbol}\n"
            "{\n"
            "   \\begingroup\n"
            "   \\fontspec{WWDesigns}\n"
            "   \\Large\n"
            "   \\selectfont\n"
            "   \\char\"0041"
            "   \\endgroup\n"
            "}\n"
            "\n"
            "\n"
            "\\newcommand{\\flourish}{\n"
            "}\n"
            "\n"
            "% combat symbol - a sword\n"
            "\\newcommand{\\rpgcombatsymbol}{$\\dagger$}\n"
            "\n"
            "% training symbol\n"
            "\\newcommand{\\rpgtrainingsymbol}{$\\otimes$}\n"
            "\n"
            "% learning symbols\n"
            "\\newcommand{\\rpglearningsymbol}{$\Psi$}\n"            
            "\n"
            "% success/fail/attempt symbols\n"
            "\\newcommand{\\rpgsuccess}{\\fatick}\n"
            "\\newcommand{\\rpgfail}{\\facross}\n"            
            "\\newcommand{\\rpgattempt}{\\faquestion}\n"
            "\n"
            "\n"
            "\n"
            "% the index \n"
            "\\makeindex\n"            
            "\n"
            # start other evironments in newenvironments like this 
            # put it after a section, not just before
            "\n"
            "\\newenvironment{playexample}{\n" 
            "\\vspace{0.4em}\n"
            "  \\flourish\n"
            "  \\begin{quote}\n"
            "  \\small\n"
            "  \\carolingia\n"
            "  \\setlength{\parindent}{0pt}\n"
            "  \\raggedright\n"
            "}\n"
            "{\n"
            "  \\end{quote}\n"
            "  \\flourish\n"
            "\\vspace{0.4em}\n"
            "}\n"
            "\n"
            "% don't break paragraphs\n"            
            "\\widowpenalties 1 10000\n"
            "\\raggedbottom\n"
            "\n"
            "\hypersetup{%\n"
            "colorlinks=false,% hyperlinks will be black\n"
            "linkbordercolor=blue,% hyperlink borders will be red\n"
            "pdfborderstyle={/S/U/W 1}% border style will be underline of width 1pt\n"
            "}\n"
            "\n"
            "\n" # monster block formatting
            "\\newcommand\\mbsep{\\raisebox{1.2ex}{"
            "\\includegraphics[width=\\columnwidth,height=0.1cm]{./resources/hrule.png}"
            "}}\n"
            "\n"
            #"\\newcommand\\mbtitleformat[1]{"
            #"  \fontspec[Path = /home/blaize/proj/dnd/laibstadt/style/fonts/]{sherwood.ttf}%
            #\large\color{monstertextcolor}#1}
            
            #"\\newcommand\\mbtagformat[1]{\\begingroup\\mbtagfont\\normalsize#1\\endgroup}"
            "\\newcommand\\mbtagformat[1]{\\begingroup\\mbtagfont\\normalsize#1\\endgroup}\n"
            #"\\begingroup\\mbtagfont\\LARGE\\color{rpgsectionfontcolor}#1\\endgroup}"
            #"\\begingroup\\fontawesome\\small\\selectfont{}#1\\endgroup}"
            #"\\begingroup\\fontawesome\\small\\selectfont{}\normalsize{#1}\\endgroup}"
            # \fontspec[Path = /home/blaize/proj/dnd/laibstadt/style/fonts/]{calibri-italic.ttf}{\normalsize{#1}}}            "\n"
            
            "% \\monster command\n"
            "\\makeatletter\n"
            "\\newcommand\\monster[1]{%\n"
            #"    \\noindent#1%\n"
            "\\noindent\\@startsection{subsection}{3}%\n"
            "{\\z@ }% indent 0pt\n"
            "{-1.5ex\\@plus -1ex \\@minus -.2ex}% vertical rubber space before the title\n"
            "{1sp \\@minus 0ex\\nointerlineskip\\vspace{3\\lineskip}}% vertical rubber space after the title\n"
            "{\\Large #1 }*% heading style modifiers\n"
            "}\n"

            # \\\\\\mbsep
#{\Large \color{monstertextcolor}%
#\fontspec[Path = /home/blaize/proj/dnd/laibstadt/style/fonts/]{LinLibertine_aS.ttf}\scshape}*% h

            # \\monster{\\noindent\\@startsection{subsection}{3}{}{}{}\n"
            #"{X}"
            #"{\\z@ }% indent 0pt\n"
            #"X}"
            #"{-1.5ex\\@plus -1ex \\@minus -.2ex}% vertical rubber space before the title\n"
            #"% vertical rubber space after the title\n"
            #"{1sp \\@minus 0ex\\nointerlineskip\\vspace{3\\lineskip}}\n"
            #"{\\Large\\color{monstertextcolor}%\n"
            #\fontspec[Path = /home/blaize/proj/dnd/laibstadt/style/fonts/]{LinLibertine_aS.ttf}\scshape}*% heading style modifiers
            #"}\n"
            "\\makeatother\n"
            "\n"
            "\n"
            "\n"            
            "% the document! \n"
            "\\begin{document}\n"
            "\n")

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
    start_ambushsymbol = no_op
    end_ambushsymbol = no_op
    start_surprisesymbol = no_op
    end_surprisesymbol = no_op    
    start_initiativesymbol = no_op
    end_initiativesymbol = no_op
    start_talksymbol = no_op
    end_talksymbol = no_op
    start_fightreachsymbol = no_op
    end_fightreachsymbol = no_op
    start_startsymbol = no_op
    end_startsymbol = no_op
    start_fastsymbol = no_op
    end_fastsymbol = no_op
    start_mediumsymbol = no_op
    end_mediumsymbol = no_op
    start_slowsymbol = no_op
    end_slowsymbol = no_op
    start_mediumorslowsymbol = no_op
    end_mediumorslowsymbol = no_op
    start_startandreactionsymbol = no_op
    end_startandreactionsymbol = no_op
    start_resolutionsymbol = no_op
    end_resolutionsymbol = no_op
    start_noncombatsymbol = no_op
    end_noncombatsymbol = no_op
    start_reactionsymbol = no_op
    end_reactionsymbol = no_op

    def start_fightreach(self, symbol):
        self.latex_file.write("\\fightreachsymbol{}")
        return
    end_fightreach = no_op    

    # def start_fight(self, symbol):
    #     self.latex_file.write("\\fightsymbol{}")
    #     return
    # end_fight = no_op
    
    # def start_fightfast(self, symbol):
    #     self.latex_file.write("\\fightfastsymbol{}")
    #     return
    # end_fightfast = no_op

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
    
    # def start_run(self, symbol):
    #     self.latex_file.write("\\runsymbol{}")
    #     return
    # end_run = no_op

    def start_noncombat(self, symbol):
        self.latex_file.write("\\noncombatsymbol{}")
        return
    end_noncombat = no_op    

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
    
    def start_initiative(self, symbol):
        self.latex_file.write("\\initiativesymbol{}")
        return
    end_initiative = no_op
    
    def get_latex_symbols(self, title):
        tex = ""
        for symbol in ("ambushsymbol",
                       "surprisesymbol",
                       "initiativesymbol",
                       "talksymbol",
                       #"runsymbol",
                       #"actsymbol",
                       #"fightrangedsymbol",
                       "fightreachsymbol",
                       "startsymbol",
                       "fastsymbol",
                       "mediumsymbol",
                       "slowsymbol",
                       "mediumorslowsymbol",
                       "startandreactionsymbol",
                       #"fightfastsymbol",
                       #"fightsymbol",
                       "resolutionsymbol",
                       "reactionsymbol",
                       "noncombatsymbol"):
            symbol_node = title.find(symbol)
            if symbol_node is not None:
                tex += " \\%s{}" % symbol
            #else:
            #    raise Exception("UNKNOWN SYMBOL: %s" % symbol)
        return tex
        
        
    
    def start_subsubsection(self, subsubsection):
        tex = ""
        anonymous = subsubsection.get("anonymous")
        if anonymous is not None and anonymous.lower() == "true":
            tex = "\\subsubsection*{"
        else:
            tex = "\\subsubsection{"

        title = subsubsection.find("subsubsectiontitle")
        if title is not None:
            tex += title.text.strip()        
        tex += self.get_latex_symbols(title)
        
        self.latex_file.write(tex) 
        self.latex_file.write("}\n") 
        return
    end_subsubsection = no_op
        
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

    def start_section(self, section):
        title_element = section.find("sectiontitle")
        if title_element is None:
            title = ""
        else:
            title = title_element.text

        self.latex_file.write("\\section{%s}\n" % title)               
        return
    end_section = no_op

    def start_subsection(self, subsection):
        tex = ""
        anonymous = subsection.get("anonymous")
        if anonymous is not None and anonymous.lower() == "true":
            tex = "\\subsection{"
        else:
            tex = "\\subsection{"

        title = subsection.find("subsectiontitle")
        if title is not None:
            tex += title.text.strip()
            tex += self.get_latex_symbols(title)

        tex += "}\n"
        self.latex_file.write(tex) 
        return
    end_subsection = no_op

    start_subsectiontitle = no_op
    end_subsectiontitle = no_op

    start_subsubsectiontitle = no_op
    end_subsubsectiontitle = no_op

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
        self.latex_file.write("\\end{tabbing}\n ")
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


    def start_bold(self, emph):
        self.latex_file.write("\\textbf{%s} " % normalize_ws(emph.text))
        return
    end_bold = no_op

    def start_smaller(self, emph):
        self.latex_file.write("\\scriptsize{%s} " % normalize_ws(emph.text))
        return
    end_smaller = no_op

    def handle_text(self, text):
        if text is not None:
            self.latex_file.write(text.encode('utf8'))
        return

    start_indexentry = no_op
    def end_indexentry(self, index_entry):
        if self.index_entry_see is not None:
            self.latex_file.write("\\index{%s|see {%s}}" % (
                normalize_ws(index_entry.text), self.index_entry_see))
            self.index_entry_see = None

        elif self.index_entry_subentry is not None:
            self.latex_file.write("\\index{%s!%s}" % (
                normalize_ws(index_entry.text), self.index_entry_subentry))
            self.index_entry_subentry = None
            
        else:
            self.latex_file.write("\\index{%s}" % normalize_ws(index_entry.text))
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
        # self.latex_file.write(" \\textbf{%s}\\index{%s}" % (normalize_ws(defn.text),
        #                                                     normalize_ws(defn.text)))
        self.latex_file.write(" \\textbf{%s}" % (normalize_ws(defn.text)))
        return
    end_defn = no_op

    # def start_distance(self, distance):
    #     d = None
    #     if use_imperial:
    #         if "imperial" in paragraph.attrib:
    #             d = normalize_ws(distance.get("imperial").lower())
    #         else:
    #             raise Exception("Imperial distance not specified!")

    #     else:
    #         # assume metric
    #         if "metric" in paragraph.attrib:
    #             d = normalize_ws(distance.get("metric").lower())
    #         else:
    #             raise Exception("Metric distance not specified!")

    #     self.latex_file.write("  " % (normalize_ws(d)))
    #     return
    # end_distance = no_op

    def start_measurement(self, distance):
        #d = None
        if use_imperial:
            distance_text = get_text_for_child(distance, "imperial")
            #if "imperial" in distance.attrib:
            #    d = normalize_ws(distance.get("imperial").lower())
            #else:
            if distance_text is None:
                raise Exception("Imperial distance not specified!")

        else:
            distance_text = get_text_for_child(distance, "metric")
            # assume metric
            #if "metric" in paragraph.attrib:
            #    d = normalize_ws(distance.get("metric").lower())
            #else:
            if distance_text is None:
                raise Exception("Metric distance not specified!")

        print "[%s]" % distance_text
        print "[%s]" % normalize_ws(distance_text)

        self.latex_file.write(normalize_ws(distance_text))
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
        if "noindent" in paragraph.attrib:
            no_indent = paragraph.get("noindent").lower()
            if no_indent == "true":
                self.latex_file.write("\\noindent ")
                
        # add drop caps to the first word of every chapter
        if not self._drop_capped_first_letter_of_chapter:
            self._drop_capped_first_letter_of_chapter = True
            words = paragraph.text.split()
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

            text = " ".join(words)
        else:
            text = normalize_ws(paragraph.text)

        self.latex_file.write(text)        
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

    def start_title(self, title):
        self.latex_file.write("{ \\color{rpgtitlefontcolor} \\rpgtitlefont %s }\\\\\n"
                              % title.text)
        return

    def end_title(self, title):
        return

    def start_subtitle(self, subtitle):        
        self.latex_file.write("{\\large \\rpgtitlesubtitlefont  %s}\\\\\n" % subtitle.text)
        return

    def end_subtitle(self, title):
        return

    start_chaptertitle = no_op
    end_chaptertitle = no_op
    # def start_chaptertitle(self, chapter_title):
    #     return

    # def end_chapter_title(self, chapter_title):
    #     return


    start_sectiontitle = no_op
    end_sectiontitle = no_op
    # def start_sectiontitle(self, section_title):
    #     return

    # def end_sectiontitle(self, section_title):
    #     return

    def start_img(self, img):
        if config.draw_imgs:
            if config.debug_outline_images:
                self.latex_file.write("\\fbox{")

            self.latex_file.write("\t\\begin{center}\n")

            filename = img.get("src")
            #_, ext = splitext(filename)
            #if ext.lower() == ".svg":            
            #    self.latex_file.write("\t\\includesvg{%s}\n"
            #                          % (#img.get("scale", default="1.0", ),
            #                              filename))
            #else:
            self.latex_file.write("\t\\includegraphics[scale=%s]{%s}\n"
                                  % (img.get("scale", default="1.0"), filename))
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

        fullwidth = False
        if "fullwidth" in figure.attrib:
            fullwidth = figure.get("fullwidth")

        if fullwidth:
            self.latex_file.write("\\begin{figure*}[%s]\n" % position)
        else:
            self.latex_file.write("\\begin{figure}[%s]\n" % position)
        self.latex_file.write("\\centering\n")
        return

    def end_figure(self, figure):
        caption = figure.get("caption")
        if caption is not None:
            self.latex_file.write("\\caption{%s}\n" % caption)        

        fullwidth = False
        if "fullwidth" in figure.attrib:
            fullwidth = figure.get("fullwidth")

        if fullwidth:
            self.latex_file.write("\\end{figure*}\n")
        else:
            self.latex_file.write("\\end{figure}\n")
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


    def start_description(self, description):
        if description.text is not None:
            self.latex_file.write("%s" % description.text)
        return

    def end_description(self, list_item):
        return

    def start_term(self, term):
        """
        A description term.

        """
        if term.text is not None:
            assert not self.description_terms_on_their_own_line
            # if self.description_terms_on_their_own_line:
            #     self.latex_file.write("\\item[%s] \hfill \n" % term.text)
            # else:
            #     self.latex_file.write("\\item[%s]" % term.text)
            self.latex_file.write("\\item[%s]" % term.text)
        return
    end_term = no_op


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

        # don't have paragraph indents buggering up our table layouts
        self.latex_file.write("\n\n\\vspace{0.2cm}\\noindent")

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
        else:
            self.latex_file.write("\\captionsetup{type=figure}")

        #self.latex_file.write("\\centering")
                        
        if fullwidth:
            # normal table environment
            self.latex_file.write("\\begin{tabularx}{1.0\\textwidth}{%s} " 
                                  % table_spec_str)
        else:
            self.latex_file.write("\\begin{tabularx}{1.0\\linewidth}{%s} " 
                                  % table_spec_str)

        if figure:
            self.latex_file.write(" \\toprule ")

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
            self.latex_file.write("\\bottomrule ")    

        # normal table environment
        self.latex_file.write("\\end{tabularx}")
        

        table_title = table.find("tabletitle")
        if table_title is not None and table_title.text.strip() != "":
            if figure:
                self.latex_file.write("\\caption{%s}" % table_title.text)
            #else:            
            #    self.latex_file.write("\\captionof{table}{%s}"
            #                          % table_title.text)
            
            
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
        self.latex_file.write("\\rpgtablesection{%s}\n" % tablesection.text.strip())
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
            self.latex_file.write("\\rowcolor{blue!20} \n")
        else:
            #self.latex_file.write("\\rowcolor{yellow!50} \n")
            pass
        return

    def end_tablerow(self, table_title):
        self.latex_file.write(" \\tabularnewline ")
        #self.latex_file.write("\\caption{%s}\n" % table_title.text)
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
            text = normalize_ws(table_data.text)

            # override for table headers
            parent = table_data.getparent()
            if parent.tag == "tableheaderrow":
                text = "\\rpgtableheader{%s}" % text

            if width > 1 or align != "l":
                # multicolumn table data
                assert align is not None

                self.latex_file.write("\\multicolumn{%s}{%s}{%s" % (width, align, text))
            else:
                # normal table data
                self.latex_file.write("%s" % text)

            #     self.latex_file.write("\\multicolumn{%s}{%s}{%s" % (width, align, text))
            # else:
            #     # normal table data
            #     self.latex_file.write("%s" % text)
        return

    def end_td(self, table_data):
        width = table_data.get("width")
        align = table_data.get("align")
        if width is not None or align is not None:
            self.latex_file.write("}")                        

        if self._current_column_in_table != 0:
            self.latex_file.write(" & ")                
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
        #     self.latex_file.write("\\rpgtableheader{%s} \n" %
        #                           table_data.text)
        #else:

        
        # self.latex_file.write("\\multicolumn{%s}{c}{\\rpgtableheader{%s}}" % 
        #                        (columns, table_data.text))
        self.latex_file.write("\\multicolumn{%s}{c}{\\rpgtableheader{%s" %
                              (columns, table_data.text))

        # if self._current_column_in_table != 0:
        #     self.latex_file.write(" & ")                        
        # return
    #end_multicolumntd = no_op
    def end_multicolumntd(self, table_data):

        self.latex_file.write("}}")
        
        if self._current_column_in_table != 0:
            self.latex_file.write(" & ")
        return


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
        self.latex_file.write("\\label{%s} " % normalize_ws(label.text))
        return
    end_label = no_op


    def start_threecolumns(self, threecolumns):
        self.latex_file.write("\\onecolumn\\begin{multicols}{3}\n")
        return
    
    def end_threecolumns(self, ability_group):
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
    # Monster blocks.
    #

    start_monsterblock = no_op
    end_monsterblock = no_op
    
    def start_mbtitle(self, mbtitle):
        #self.latex_file.write("\\subsection{%s}\n\\mbsep{}" % mbtitle.text)
        #self.latex_file.write("\\mbtitleformat{%s}\n\\mbsep{}" % mbtitle.text)
        self.latex_file.write("\\monster{%s}\n"
                              #"\\\\\n"
                              "\\mbsep\n" % mbtitle.text)
        return

    def end_mbtitle(self, mbtitle):
        return
    
    def start_mbtags(self, mbtags):
        self.latex_file.write("\\mbtagformat{%s}\n" % mbtags.text)
        return
    end_mbtags = no_op
    
    def start_mbabilities(self, mbabilities):
        self.latex_file.write("Abilities: %s\n" % mbabilities.text)
        return
    end_mbabilities = no_op

    def start_mbaspects(self, mbaspects):
        self.latex_file.write("Aspects: %s\n" % mbaspects.text)
        return
    end_mbaspects = no_op

    def start_mbac(self, mbac):
        self.latex_file.write("AC: %s, " % mbac.text)
        return
    end_mbac = no_op

    def start_mbstamina(self, mbstamina):
        self.latex_file.write("Stamina: %s, " % mbstamina.text)
        return
    end_mbstamina = no_op

    def start_mbhealth(self, mbhealth):
        self.latex_file.write("Health: %s\n" % mbhealth.text)
        return
    end_mbhealth = no_op

    def start_mbstr(self, mbstr):
        self.latex_file.write("Str: %s, " % mbstr.text)
        return
    end_mbstr = no_op

    def start_mbend(self, mbend):
        self.latex_file.write("End: %s, " % mbend.text)
        return
    end_mbend = no_op
    
    def start_mbag(self, mbag):
        self.latex_file.write("Ag: %s, " % mbag.text)
        return
    end_mbag = no_op
    
    def start_mbspd(self, mbspd):
        self.latex_file.write("Spd: %s, " % mbspd.text)
        return
    end_mbspd = no_op
    
    def start_mbluck(self, mbluck):
        self.latex_file.write("Luck: %s, " % mbluck.text)
        return
    end_mbluck = no_op
    
    def start_mbwil(self, mbwil):
        self.latex_file.write("Wil: %s, " % mbwil.text)
        return
    end_mbwil = no_op
    
    def start_mbper(self, mbper):
        self.latex_file.write("Per: %s\n" % mbper.text)
        return
    end_mbper = no_op    
