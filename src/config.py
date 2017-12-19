"""

 Specifies what files to build!


"""

# should we draw an image in the page background
display_page_background = False

# paper size is one of "a4" or "letter"
paper_size = "a4"

# print debug info for skills
print_skill_debug_info = True

# draw skill trees?
draw_skill_trees = True

# outline images
# (useful for debugging alignment and sizing of images)
debug_outline_images = False

# display design notes..
# These are musings on why things have been done a certain way.
# They're not necessary to play the game.  Include them if you
# don't mind printing some extra stuff and you're curious about
# the design motivations.
print_design_notes = False

# display provenance notes
# These are notes on where the ideas for the game came from.
print_provenance_notes = True

# should we render images?
draw_imgs = True

# resources dir
from os.path import dirname, abspath, join
resources_dir = abspath(join(dirname(__file__), "..", "resources"))


# measurement system (metric or imperial)
#use_imperial = True
use_imperial = False

# Should we append the index to the core doc?
add_index_to_core = True

# List of files to build (fname, build_index?, index_name)
files_to_build = (
    ("phb.xml", True, "PHB"),
    # ("character_creation.xml", True, "CC"),
    # ("equipment.xml", True, "Eq"),
    # ("magic.xml", True, "Mg"),
    ("monster_manual.xml", True, "MM"),
    #("magic_items.xml", True, "MI"),
    #("abilities.xml", True, "Ab"),
    #("ability_dcs.xml", False, "X"),
    # ("tables.xml", True, "[T]"),

    #("character_abilities.xml", False, None),
    #("gms_screen.xml", False, "GMS"),
    ("gmg.xml", True, "[GMG]"),
    #("archetypes.xml", True, "[A]"),
)

patrons_to_build = (
    ("klazyabolus", True, "[KL]"),
)

archetypes_to_build = (
    #("bard", True, "[BRD]"),
    # ("dwarven_shield_warrior", True, "[DSW]"),
    # ("red_mage", True, "[RM]"),
    # ("halfling_rover", True, "[HR]"),
    # ("elven_scion", True, "[ES]"),
    ("outrider", True, "[OR]"),
    ("black_coat", True, "[BC]"),
    ("summoner", True, "[SM]"),
    ("hedge_wizard", True, "[HW]"),
    ("witch_hunter", True, "[WH]"),
    ("rake", True, "[RK]"),
)

encounters_to_build = (
    ("dwarven_mines", False, "[dm]"),
    ("the_trial", False, "[tt]"),
)


