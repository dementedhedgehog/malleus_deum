"""

  Jinja Templating

  We run the xml through a template engine to enable us to fill things in from
  the database.  Input docs are in dirs like docs/, abilities/ etc and the
  outputs go into build/foo.xml

"""
import functools
from os.path import join, splitext, basename
import codecs

from jinja2 import Environment, FileSystemLoader

# local
from doc import Doc
from utils import root_dir, build_dir
import config


def _jinja_log_to_console(text):
    """Custom jinja filter for printing log messages to console."""
    print(text, flush=True)
    return ''


def _jinja_exit(text):
    """Custom jinja filter to exit the program (for debugging only)."""
    print(text, flush=True)
    sys.exit(1)

    
def _jinja_recursive_render(template, jinja_env, **values):
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
    
    # Use these in jinja template code like this:  {{ "foobar" | log }}
    # jinja_env.filters['ab'] = db.filter_abilities
    # jinja_env.filters['abilities'] = db.filter_abilities
    jinja_env.filters['log']=_jinja_log_to_console
    jinja_env.filters['exit']=_jinja_exit    
    return jinja_env


def render_xml(
        jinja_env,
        db,
        xml_fname_in,
        verbosity=0,
        template_fname=None,
        archetype=None,
        patron=None):
    """
    Run the xml through a templating system, and write the processed
    xml to the build dir

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
        raise Exception(f"Problem reading template file {template_fname}.")
    
    xml = _jinja_recursive_render(
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
    # try:
    #     xml = db.filter_abilities(xml, verbose=verbosity>0)
    # except Exception as err:
    #     err.add_note(f"Problem filtering abilities in {xml_fname_in}")
    #     raise err

    # write the post-processed xml to the build dir 
    # (has all the included files in it).
    with codecs.open(xml_fname_out, "w", "utf-8") as f:
        f.write(xml)

    return xml_fname_out
