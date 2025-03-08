"""


"""
import functools
from os.path import join, splitext, basename # , dirname, exists, abspath
import codecs

from jinja2 import Environment, FileSystemLoader

# local
from doc import Doc
from utils import root_dir, build_dir
import config


# Jinja2 doesn't like absolute paths.
# We must supply a relative path!
ARCHETYPE_TEMPLATE_FNAME = join("docs", "archetype_template.xml")
PATRON_TEMPLATE_FNAME = join("docs", "patron_template.xml")


def jinja_no_nones(x):
    """Custom jinja filter for formatting nones"""
    return "-" if (x is None or (type(x) == str and x.strip() == "")) else x


def jinja_log_to_console(text):
    """Custom jinja filter for printing log messages to console."""
    print(text, flush=True)
    return ''


def jinja_exit(text):
    """Custom jinja filter to exit the program (for debugging only)."""
    print(text, flush=True)
    sys.exit(1)

    
def jinja_recursive_render(template, jinja_env, **values):
    """
    Recurse into expanded template variables .. so our templates can
    include templates which can include templates... etc and all the
    templates will be evaluated.

    """
    MAX_DEPTH=5
    depth = 0
    prev = template.render(**values)
    while True:
        new_template = jinja_env.from_string(prev)
        curr = new_template.render(**values)
        if curr != prev:
            prev = curr
        else:
            return curr

        depth += 1
        if depth >= MAX_DEPTH:
            break


@functools.cache
def get_jinja_env(db):
    
    # get a jinja environment
    jinja_env = Environment(
        loader = FileSystemLoader([root_dir, ]),
        keep_trailing_newline = True,
        trim_blocks = False,
        lstrip_blocks = False,
    )
    
    # Use these in jinja templates like this:  {{ "foobar" | log }}
    #jinja_env.filters['convert_to_roman_numerals'] = utils.convert_to_roman_numerals
    jinja_env.filters['ab'] = db.filter_abilities
    jinja_env.filters['abilities'] = db.filter_abilities
    #jinja_env.filters['no_nones'] = jinja_no_nones
    jinja_env.filters['log']=jinja_log_to_console
    jinja_env.filters['exit']=jinja_exit
    
    return jinja_env


def apply_template_to_xml(jinja_env,
                          db,
                          xml_fname_in,
                          verbosity,
                          template_fname=None,
                          archetype=None,
                          patron=None):
    """
    Run the xml through a templating system.

    """
    xml_base_fname, _ = splitext(basename(xml_fname_in))
    xml_fname_out = join(build_dir, "%s.xml" % xml_base_fname)

    # the very first thing we do is run the xml through a template engine 
    # (Doing it like this allows us to include files relative to the doc 
    # dir using Jinjas include directive). 
    if template_fname is None:
        template_fname = xml_fname_in
    template = jinja_env.get_template(template_fname)
    if template is None:
        print(f"Problem reading template file {template_fname}.")
        exit(0)
        
    xml = jinja_recursive_render(
        template=template,
        jinja_env=jinja_env,
        db=db,
        monster_groups=db.monster_groups,                          
        ability_groups=db.ability_groups,
        npc_gangs=db.npc_gangs,
        archetype=archetype,
        patron=patron,
        config=config,
        encounters=db.encounters,
        add_index_to_core=config.add_index_to_core,
        doc_name=xml_fname_in)

    # process abilities
    try:
        xml = db.filter_abilities(xml, verbose=verbosity>0)
    except Exception as err:
        print(f"Problem filtering abilities in {xml_fname_in}")
        raise err

    # write the post-processed xml to the build dir 
    # (has all the included files in it).
    with codecs.open(xml_fname_out, "w", "utf-8") as f:
        f.write(xml)

    # parse an xml document
    doc = Doc(xml_fname_out)
    if not doc.parse():
        print(f"Problem parsing the xml.")
        exit(0)

    if not doc.validate():
        print("Fatal: xml errors are fatal!")
        print("Run with the -s cmd line option to ignore xml errors.")
        exit(0)        
        
    return doc
