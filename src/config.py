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
use_imperial = True
#use_imperial = False

# List of files to build (fname, build_index?, index_name)
files_to_build = (
    #("abilities.xml", True, "C"),
    ("core.xml", True, "C"),
    ("character_creation.xml", True, "CC"),
    ("equipment.xml", True, "Eq"),
    ("magic.xml", True, "Mg"),
    #("monster_manual.xml", True, "MM"),
    ("magic_items.xml", True, "MI"),
    #("dmg.xml",
    #("archetypes.xml", True, "[A]"),
    ("abilities.xml", True, "Ab"),
    ("tables.xml", True, "[T]"),
)

archetypes_to_build = (
    ("dwarven_shield_warrior", True, "[ADSW]"),
    ("red_mage", True, "[ARM]"),
    ("halfling_rover", True, "[HR]"),
    ("elven_scion", True, "[ES]"),
    ("praedicant", True, "[PR]"),
    ("summoner", True, "[SM]"),
    ("hedge_wizard", True, "[HW]"),
    ("witch_hunter", True, "[WH]"),
    ("rake", True, "[RK]"),
    #("dwarven_rune_maester", True, "[DRM]"),
)
