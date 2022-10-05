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
#debug_outline_images = True

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
doc_files_to_build = (
    ("phb.xml", True, "PHB"),
    #("equipment.xml", True, "Eq"),
    #("magic.xml", True, "Mg"),
    #("monster_manual.xml", True, "MM"),
    ("archetypes.xml", True, "AR"),
    #("magic_items.xml", True, "MI"),
    #("abilities.xml", True, "Ab"),
    #("ability_dcs.xml", False, "X"),
    #("tables.xml", True, "[TBL]"),
    #("gms_screen.xml", False, "GMS"),
    #("gmg.xml", True, "[GMG]"),
    #("rationale.xml", True, "[R]"),
    #("archetypes.xml", True, "[A]"),
)


# List of background files to build (fname, build_index?, index_name)
background_files_to_build = (
    #("mithras/mithras.xml", True, "MTH"),
    #("noble_houses_of_westreich/noble_houses_of_westreich.xml", True, "NHW"),
    # ("ascheburg/ascheburg.xml", True, "ASB"),
    #("names/names.xml", True, "NMS"),
)

patrons_to_build = (
    #("klazyabolus", True, "[KL]"),
)

archetypes_to_build = (
    #("black_coat", True, "[BC]"),
    #("chevalier", True, "[Ch]"),
    # ("champion_of_mithras", True, "[CoM]"),
    #("confessor_militant", True, "[FC]"), 
    #("elven_scion", True, "[ESc]"),
    #("fyrdzwerg", True, "[FZW]"),
    #("halfling_rover", True, "[HR]"),
#    ("hedge_wizard", True, "[HW]"),
    #("outrider", True, "[OR]"),
    # ("penitent_brother", True, "[PB]"),
    #("red_mage", True, "[RM]"),
#    ("second_son", True, "[SS]"),
    #("skald", True, "[SKL]"),
    #("summoner", True, "[SM]"),
    #("witch_hunter", True, "[WH]"),
)

encounters_to_build = (
    #("dwarven_mines", False, "[dm]"),
    #("the_trial", False, "[tt]"),
    #("von_bauer_chateau", False, "[vbc]"),
    #("the_tower_of_laibstadt", False, "[tol]"),
)

modules_to_build = (
    #("calibration", False, "[calib]"),
    #("dwarven_mines", False, "[dm]"),
    #("the_trial", False, "[tt]"),
    #("von_bauer_chateau", False, "[vbc]"),
    #("the_tower_of_laibstadt", False, "[tol]"),
    # ("candlemass", False, "[cdm]"),
    # ("reichs_pferdemeister", False, "[rfm]"),
    # ("ottmar_fulcade", False, "[of]"),
    
    #("temple_of_the_white_prince", False, "[totwp]"),
    #("lonely_road", False, "[lonr]"),
    #("half_cask", False, "[hcask]"),
    ("cold_keep", False, "[ck]"),
    # ("brummbär_money_lender", False, "[bml]"),    
)


# These get added to a zip and dropped into the releases dir
# with the current release number when ./publish -r is run.
release_files = (
    "phb.pdf",
    "archetypes.pdf",
    "rationale.pdf",

    "black_coat.pdf",
    "chevalier.pdf",
    "champion_of_mithras.pdf",
    "confessor_militant.pdf",
    "elven_scion.pdf", 
    "fyrdzwerg.pdf", 
    "halfling_rover.pdf",
    "hedge_wizard.pdf", 
    "outrider.pdf", 
    "penitent_brother.pdf", 
    "red_mage.pdf", 
    "second_son.pdf", 
    "skald.pdf", 
    "summoner.pdf", 
    "witch_hunter.pdf",
)

    

    
