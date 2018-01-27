#!/usr/bin/env python2


from os.path import abspath, join, splitext, dirname, exists, basename
import cairo
import math
import sys

from abilities import AbilityGroups

src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))


WIDTH = 760
HEIGHT = 560
ABILITY_MARGIN_TOP = 2
ABILITY_MARGIN_LEFT = 4
ABILITY_MARGIN_RIGHT = 4
ABILITY_MARGIN_BOTTOM = 2
CIRCLE_RADIUS = 4
ABILITY_LEVEL_SEPARATOR = CIRCLE_RADIUS + 2
CIRCLE_VERTICAL_SEPARATOR = 2
SPLINE_HORIZONTAL_LEAD = 25

# standard horizontal space between nodes and their children.
VSTEP = 1
HSTEP = 1

FONT_SIZE = 6

class Page:
    ONE = "ONE"
    TWO = "TWO"
    NONE = "NONE" # Dont include


SKILL_POSITION_LOOKUP = {
    "archery.archery": (Page.ONE, "school.military", ((30, 35),)),
    "archery.dead_eye": (Page.ONE, "archery.archery", ((40, 30),)),
    "archery.long_bow": (Page.ONE, "archery.archery", ((40, 0),)),
    "archery.rain_of_arrows": (Page.ONE, "archery.archery", ((40, 15),)),
    "axe.cleave": (Page.ONE, "axe.strike", ((25, 20),)),
    "axe.frenzy": (Page.ONE, "axe.strike", ((45, -20),)),
    "axe.hook": (Page.ONE, "axe.strike", ((40, 0),)),
    "axe.strike": (Page.ONE, "school.military", ((0, -230),)),
    "club.smash": (Page.ONE, "club.strike", ((40, -5),)),
    "club.strike": (Page.ONE, "school.military", ((40, -10),)),
    "club.wild_swing": (Page.ONE, "club.strike", ((40, 20),)),
    "craft.armour_smith": (Page.ONE, "craft.smith", ((20, -40),)),
    "craft.builder": (Page.ONE, "craft.carpentry", ((45, -10),)),
    "craft.carpentry": (Page.ONE, "school.trade", ((30, 15),)),
    "craft.cartwright": (Page.ONE, "craft.carpentry", ((25, 35),)),
    "craft.cooper": (Page.ONE, "craft.carpentry", ((30, 10),)),
    "craft.farmer": (Page.ONE, "school.trade", ((25, 55),)),
    "craft.mason": (Page.ONE, "school.trade", ((25, -20),)),
    "craft.shipwright": (Page.ONE, "craft.carpentry", ((10, 55),)),
    "craft.smith": (Page.ONE, "school.trade", ((20, -65),)),
    "craft.weapon_smith": (Page.ONE, "craft.smith", ((30, -15),)),
    "crossbow.crossbow": (Page.ONE, "school.military", ((20, -100),)),
    "crossbow.fast_loader": (Page.ONE, "crossbow.crossbow", ((40, -10),)),
    "crossbow.heavy": (Page.ONE, "crossbow.crossbow", ((40, 20),)),
    "dagger.riposte": (Page.ONE, "dagger.strike", ((40, 15),)),
    "dagger.strike": (Page.ONE, "school.military", ((10, -160),)),
    "dagger.throw": (Page.ONE, "dagger.strike", ((40, -10),)),
    "fine_arts.art": (Page.ONE, "school.fine_arts", ((30, 30),)),
    "fine_arts.dance": (Page.ONE, "fine_arts.music", ((30, 60),)),
    "fine_arts.jester": (Page.ONE, "school.fine_arts", ((30, -20),)),
    "fine_arts.keyed": (Page.ONE, "fine_arts.music", ((30, 15),)),
    "fine_arts.music": (Page.ONE, "school.fine_arts", ((30, -55),)),
    "fine_arts.oratory": (Page.ONE, "school.fine_arts", ((30, 10),)),
    "fine_arts.percussion": (Page.ONE, "fine_arts.music", ((30, 0),)),
    "fine_arts.singing": (Page.ONE, "fine_arts.music", ((35, 40),)),
    "fine_arts.strings": (Page.ONE, "fine_arts.music", ((25, 95),)),
    "fine_arts.wind": (Page.ONE, "fine_arts.music", ((20, -20),)),
    "gun.maintenance": (Page.ONE, "gun.shoot", ((20, 0),)),
    "gun.shoot": (Page.ONE, "school.military", ((30, -50),)),
    "gun.sharp_shooter": (Page.ONE, "gun.shoot", ((60, -50),)),
    "hammer.smash": (Page.ONE, "hammer.strike", ((40, -5),)),
    "hammer.strike": (Page.ONE, "school.military", ((-10, -270),)),
    "language.aquillonian": (Page.TWO, "school.scholar", ((0, 180),)),
    "language.brythinian": (Page.TWO, "school.scholar", ((-15, -200),)),
    "language.dwarven": (Page.TWO, "school.scholar", ((25, -85),)),
    "language.fey": (Page.TWO, "school.scholar", ((30, 80),)),
    "language.hibernian": (Page.TWO, "school.scholar", ((45, -5),)),
    "language.inochian": (Page.TWO, "school.scholar", ((60, 45),)),
    "language.sylvan": (Page.TWO, "school.scholar", ((40, -60),)),
    "lore.alchemy": (Page.TWO, "lore.natural_history", ((50, 60),)),
    "lore.antiquarian": (Page.TWO, "school.scholar", ((10, 160),)),
    "lore.book_keeping": (Page.TWO, "lore.maths", ((25, 0),)),
    "lore.earth_science": (Page.TWO, "lore.maths", ((10, 50),)),
    "lore.history": (Page.TWO, "school.scholar", ((5, -135),)),
    "lore.law": (Page.TWO, "school.scholar", ((-20, 200),)),
    "lore.maths": (Page.TWO, "school.scholar", ((-30, 230),)),
    #"lore.natural_history": (Page.TWO, "lore.alchemy", ((20, 0),)),
    "lore.natural_history": (Page.TWO, "school.scholar", ((20, 140),)),
    "lore.physics": (Page.TWO, "lore.maths", ((25, 20),)),
    "lore.politics": (Page.TWO, "school.scholar", ((35, 15),)),
    "lore.theology": (Page.TWO, "school.scholar", ((-5, -180),)),
    "luck.lucky": (Page.ONE, None, ((540, 345),)),
    "luck.misfortune": (Page.ONE, "luck.lucky", ((20, 55),)),
    "luck.nabail": (Page.ONE, "luck.lucky", ((40, 15),)),
    "luck.nick_of_time": (Page.ONE, "luck.lucky", ((40, 35),)),
    "luck.reroll": (Page.ONE, "luck.lucky", ((110, 0),)),
    "magic.alarum": (Page.TWO, "magic_school.arcana", ((40, 30),)),
    "magic.augury": (Page.TWO, "magic_school.theurgic", ((40, 30),)),
    "magic.auri_fames": (Page.TWO, "magic_school.enchantment", ((20, 20),)),
    "magic.banish": (Page.TWO, "magic_school.abjuration", ((25, 40),)),
    "magic.bind": (Page.TWO, "magic_school.conjuration", ((30, -70),)),
    "magic.blood_soucriant": (Page.TWO, "magic_school.necromancy", ((30, -70),)),
    "magic.circle_of_protection": (Page.TWO, "magic_school.abjuration", ((30, 20),)),
    "magic.cloak_of_shadows": (Page.TWO, "magic_school.arcana", ((20, -10),)),
    "magic.commune": (Page.TWO, "magic_school.conjuration", ((35, -5),)),
    "magic.contego": (Page.TWO, "magic_school.abjuration", ((30, -5),)),
    "magic.eldritch_push": (Page.TWO, "magic_school.evocation", ((40, 5),)),
    "magic.eldritch_grasp": (Page.TWO, "magic.eldritch_push", ((40, -20),)),
    "magic.eldritch_shield": (Page.TWO, "magic_school.abjuration", ((20, 65),)),
    "magic.flesh_ward": (Page.TWO, "magic_school.abjuration", ((35, -30),)),
    "magic.glamour": (Page.TWO, "magic_school.enchantment", ((10, 40),)),
    "magic.graft_flesh": (Page.TWO, "magic_school.necromancy", ((40, 20),)),
    "magic.greater_portal": (Page.TWO, "magic.portal", ((20, 10),)),
    "magic.heal": (Page.TWO, "magic_school.theurgic", ((40, -15),)),
    "magic.hex": (Page.TWO, "magic_school.enchantment", ((-10, -60),)),
    "magic.hyperosmia": (Page.TWO, "magic_school.wild_magic", ((20, -10),)),
    "magic.incendo": (Page.TWO, "magic_school.evocation", ((40, -40),)),
    "magic.kiss_of_the_deep": (Page.TWO, "magic_school.elemental", ((40, -25),)),
    "magic.mind_worm": (Page.TWO, "magic_school.enchantment", ((25, -5),)),
    "magic.mist": (Page.TWO, "magic_school.elemental", ((25, 30),)),
    "magic.phantasmal_leech": (Page.TWO, "magic_school.conjuration", ((30, -30),)),
    "magic.phantasmal_vulture": (Page.TWO, "magic.phantasmal_leech", ((20, 10),)),
    "magic.portal": (Page.TWO, "magic_school.conjuration", ((50, 20),)),
    # "magic.potions": (Page.TWO, "magic_school.ritual", ((20, 0),)),
    # "magic.scrolls": (Page.TWO, "magic_school.ritual", ((20, 20),)),
    "magic.potions": (Page.TWO, "lore.alchemy", ((40, 20),)),
    "magic.scrolls": (Page.TWO, "magic_school.arcana", ((20, 20),)),
    "magic.scry": (Page.TWO, "magic_school.evocation", ((50, 25),)),
    "magic.scry_greater": (Page.TWO, "magic.scry", ((40, -10),)),
    "magic.shatter": (Page.TWO, "magic_school.elemental", ((10, 50),)),
    "magic.sign_of_idreshein": (Page.TWO, "magic_school.runes", ((40, -10),)),
    "magic.smoke_weasel": (Page.TWO, "magic_school.elemental", ((30, -5),)),
    "magic.speak_with_amphibians": (Page.TWO, "magic_school.zoolingualism", ((0, -55),)),
    "magic.speak_with_birds": (Page.TWO, "magic_school.zoolingualism", ((20, 40),)),
    "magic.speak_with_cats": (Page.TWO, "magic_school.zoolingualism", ((30, 15),)),
    "magic.speak_with_horses": (Page.TWO, "magic_school.zoolingualism", ((30, -10),)),
    "magic.speak_with_rodents": (Page.TWO, "magic_school.zoolingualism", ((10, 70),)),
    "magic.speak_with_wolves": (Page.TWO, "magic_school.zoolingualism", ((20, -30),)),
    "magic.spider_climb": (Page.TWO, "magic_school.wild_magic", ((20, 20),)),
    "magic.stay_death": (Page.TWO, "magic_school.necromancy", ((40, 55),)),
    "magic.stone_skin": (Page.TWO, "magic_school.elemental", ((30, 15),)),
    "magic.summon": (Page.TWO, "magic_school.conjuration", ((25, 35),)),
    "magic.true_sight": (Page.TWO, "magic_school.arcana", ((25, 0),)),
    "magic.turn_undead": (Page.TWO, "magic_school.theurgic", ((40, 10),)),
    "magic.wither": (Page.TWO, "magic_school.evocation", ((40, -20),)),
    "magic.wyld_portal": (Page.TWO, "magic.greater_portal", ((20, 10),)),
    "magic.vermin_swarm": (Page.TWO, "magic_school.wild_magic", ((20, 10),)),
    "magic_school.abjuration": (Page.TWO, "language.inochian", ((70, -70),
                                                                (80, 0),
                                                                #(80, 10)
    )),
    "magic_school.arcana": (Page.TWO, "language.inochian", ((50, -180),)),    
    "magic_school.wild_magic": (Page.TWO, "school.scholar", ((-30, -240),
                                                             (10, 0))),
    
    "magic_school.conjuration": (Page.TWO, "language.inochian", ((40, 20),
                                                                 #(0, 0),
                                                                 #(50, 0)
    )),
    "magic_school.elemental": (Page.TWO, "language.inochian", ((50, -110),
                                                               (240, 0),
                                                               (40, 50)
    )),
    "magic_school.enchantment": (Page.TWO, "language.fey", (#(40, 40),
                                                            (80, 100),
                                                            (250, 0),)),
    "magic_school.evocation": (Page.TWO, "language.inochian", ((60, 90), )),
    "magic_school.necromancy": (Page.TWO, "language.inochian", ((50, -120),
                                                                (180, 0),
                                                                (40, -80))),
    #"magic_school.ritual": (Page.TWO, "language.inochian", ((50, -115),)),
    "magic_school.runes": (Page.TWO, "language.inochian", ((30, -285),)),
    "magic_school.theurgic": (Page.TWO, "language.inochian", ((50, -240),)),

    
    "magic_school.zoolingualism": (Page.TWO, "magic_school.enchantment", ((20, -30),)),
    "monster.claw": (Page.NONE, None, ((100, 100),)),
    "monster.demon_instability": (Page.NONE, None, ((100, 100),)),
    "monster.fly": (Page.NONE, None, ((100, 100),)),
    "monster.countless_bites": (Page.NONE, None, ((100, 100),)),
    "monster.poison_bite": (Page.NONE, None, ((100, 100),)),
    "monster.prehensile_tongue": (Page.NONE, None, ((100, 100),)),
    "monster.summon_demon": (Page.NONE, None, ((100, 100),)),
    "monster.swarm": (Page.NONE, None, ((100, 100),)),
    "monster.web": (Page.NONE, None, ((100, 100),)),
    "necromancy.commune": (Page.TWO, "magic_school.necromancy", ((40, -5),)),
    "physical.charge": (Page.ONE, "school.physical", ((75, -75),)),
    "physical.climb": (Page.ONE, "school.physical", ((70, 20),)),
    "physical.dodge": (Page.ONE, "school.physical", ((35, 135),)),
    "physical.flee": (Page.ONE, "school.physical", ((70, -50),)),
    "physical.grapple": (Page.ONE, "school.physical", ((80, 80),)),
    "physical.head_butt": (Page.ONE, "school.physical", ((20, 180),)),
    "physical.jump": (Page.ONE, "school.physical", ((90, 0),)),
    "physical.kick": (Page.ONE, "school.physical", ((70, 100),)),
    "physical.listen": (Page.ONE, "school.physical", ((50, 120),)),
    "physical.notice": (Page.ONE, "school.physical", ((25, 155),)),
    "physical.punch": (Page.ONE, "school.physical", ((10, 200),)),
    "physical.rest": (Page.ONE, "school.physical", ((0, 225),)),
    "physical.run": (Page.ONE, "school.physical", ((60, -30),)),
    "physical.sleep": (Page.ONE, "school.physical", ((-20, 250),)),
    "physical.swim": (Page.ONE, "school.physical", ((55, 40),)),
    "physical.throw": (Page.ONE, "school.physical", ((0, -70),)),
    "school.fine_arts": (Page.ONE, None, ((525, 500),)),
    "school.military": (Page.ONE, None, ((0, 295),)),
    "school.physical": (Page.ONE, None, ((240, 100),)),
    "school.racial": (Page.NONE, None, ((150, 20),)),
    "school.scholar": (Page.TWO, None, ((0, 260),)),
    "school.skullduggery": (Page.ONE, None, ((370, 400),)),
    "school.social": (Page.ONE, None, ((585, 140),)),
    "school.trade": (Page.ONE, None, ((415, 180),)),
    "school.wilderness": (Page.ONE, None, ((200, 480),)),
    "shield.block": (Page.ONE, "school.military", ((5, 140),)),
    "shield.push": (Page.ONE, "shield.block", ((45, -5),)),
    "shield.support": (Page.ONE, "shield.block", ((40, 15),)),
    "skullduggery.cloak_fighting": (Page.ONE, "school.skullduggery", ((30, -70),)),
    "skullduggery.concealment": (Page.ONE, "school.skullduggery", ((20, 90),)),
    "skullduggery.cryptography": (Page.TWO, "school.scholar", ((15, -110),)),
    "skullduggery.disguise": (Page.ONE, "school.skullduggery", ((10, -105),)),
    "skullduggery.escapist": (Page.ONE, "school.skullduggery", ((40, 15),)),
    "skullduggery.pick_locks": (Page.ONE, "school.skullduggery", ((40, 35),)),
    "skullduggery.ropecraft": (Page.ONE, "school.skullduggery", ((-20, 130),)),
    "skullduggery.search": (Page.ONE, "school.skullduggery", ((5, 110),)),
    "skullduggery.sleight_of_hand": (Page.ONE, "school.skullduggery", ((35, -45),)),
    "skullduggery.sneak": (Page.ONE, "school.skullduggery", ((35, -20),)),
    "skullduggery.trap_work": (Page.ONE, "school.skullduggery", ((25, 55),)),
    "social.contacts": (Page.ONE, "school.social", ((70, 40),)),
    "social.deceive": (Page.ONE, "school.social", ((20, -125),)),
    "social.etiquette": (Page.ONE, "school.social", ((50, -20),)),
    "social.high_contacts": (Page.ONE, "school.social", ((65, 20),)),
    "social.high_etiquette": (Page.ONE, "school.social", ((50, -40),)),
    "social.interrogate": (Page.ONE, "school.social", ((10, 180),)),
    "social.intimidate": (Page.ONE, "school.social", ((20, 155),)),
    "social.leadership": (Page.ONE, "school.social", ((40, 80),)),
    "social.low_contacts": (Page.ONE, "school.social", ((45, 60),)),
    "social.low_etiquette": (Page.ONE, "school.social", ((50, 0),)),
    "social.negotiate": (Page.ONE, "school.social", ((40, -75),)),
    "social.perceive": (Page.ONE, "school.social", ((30, -100),)),
    "social.rally": (Page.ONE, "school.social", ((40, 100),)),
    "social.yield": (Page.ONE, "school.social", ((25, 120),)),
    "spear.brace": (Page.ONE, "spear.strike", ((25, 5),)),
    "spear.circle_of_death": (Page.ONE, "spear.strike", ((20, -20),)),
    "spear.hook": (Page.ONE, "spear.strike", ((20, 45),)),
    "spear.parry": (Page.ONE, "spear.strike", ((30, 25),)),
    "spear.strike": (Page.ONE, "school.military", ((-10, 200),)),
    "special.fey_resilience": (Page.NONE, None, ((100, 100),)),
    "special.natural_sprinter": (Page.NONE, None, ((100, 100),)),
    "special.sixth_sense": (Page.NONE, None, ((100, 100),)),
    # "staff.brace": (Page.ONE, "staff.strike", ((25, 5),)),
    # "staff.circle_of_death": (Page.ONE, "staff.strike", ((20, -20),)),
    # "staff.hook": (Page.ONE, "staff.strike", ((20, 45),)),
    # "staff.parry": (Page.ONE, "staff.strike", ((30, 25),)),
    # "staff.strike": (Page.ONE, "school.military", ((-10, 200),)),
    "staff.brace": (Page.ONE, "staff.strike", ((25, 5),)),
    "staff.circle_of_death": (Page.ONE, "staff.strike", ((20, -20),)),
    "staff.parry": (Page.ONE, "staff.strike", ((30, 25),)),
    "staff.strike": (Page.ONE, "school.military", ((-10, 200),)),
    "sword.disarm": (Page.ONE, "sword.strike", ((55, 20),)),
    "sword.feint": (Page.ONE, "sword.strike", ((50, 35),)),
    "sword.parry": (Page.ONE, "sword.strike", ((75, 5),)),
    "sword.strike": (Page.ONE, "school.military", ((20, 85),)),
    "transport.animal_handling": (Page.ONE, "school.trade", ((-20, -140),)),
    "transport.drive_cart": (Page.ONE, "school.trade", ((0, -100),)),
    "transport.horse_riding": (Page.ONE, "transport.animal_handling", ((20, -20),)),
    "transport.master": (Page.ONE, "transport.sailor", ((25, 20),)),
    "transport.sailor": (Page.ONE, "school.trade", ((20, 80),)),
    "wilderness.dungeoneering": (Page.ONE, "school.wilderness", ((30, 30),)),
    "wilderness.hunting": (Page.ONE, "wilderness.tracking", ((20, 0),)),
    "wilderness.scout": (Page.ONE, "school.wilderness", ((25, 50),)),
    "wilderness.stealth": (Page.ONE, "school.wilderness", ((30, -5),)),
    "wilderness.survivalism": (Page.ONE, "wilderness.wayfinding", ((25, 0),)),
    "wilderness.tracking": (Page.ONE, "school.wilderness", ((5, -60),)),
    "wilderness.wayfinding": (Page.ONE, "school.wilderness", ((30, -25),)),    
}


# for k, v in SKILL_POSITION_LOOKUP.items():
#     page, parent, points = v

#     if parent is not None:
#         parent = '"%s"' % parent

#     #new_points = tuple([(p[0] * 5, p[1] * 5) for p in points])

#     print '    "%s": (Page.%s, %s, %s),' % (k, page, parent, new_points)
# sys.exit()


class AbilityNode:
    """
    Graphic representation of an ability.

    """

    def __init__(self, ability):
        self.ability = ability

        # x, y is the point in the middle left of the node.
        self.x = None
        self.y = None

        # FIXME: do I need this any more?
        # map of ability_level_id -> arrow connection position relative to
        # the position of this node.
        self.connector_posns = {}

        # map of ability_level_id -> arrow connection offsets relative to
        # the position of this node.
        self.connector_offsets = {}

        # width of the node (used for relative layout)
        self.width = None
        return

    
    def calc_size(self, context):
        """
        Calculates the width of the ability node.  We need to know
        all the node widths before we can layout anything.

        """
        # get the text size
        title = self.ability.get_title()
        (xt, yt, width, height, dx, dy) = context.text_extents(title)

        # width of the whole ability node.
        self.width = (width + ABILITY_MARGIN_RIGHT + ABILITY_MARGIN_LEFT +
                      ABILITY_LEVEL_SEPARATOR + CIRCLE_RADIUS)
        return

    
    def layout(self, context, ability_nodes):
        """
        Work out where all the nodes go relative to one another.

        """
        # calculate position of the ability node
        self.x, self.y = ability_nodes.get_relative_pos(self.ability.get_id())        
                
        title = self.ability.get_title()
        (xt, yt, width, height, dx, dy) = context.text_extents(title)
        half_width = width / 2
        half_height = height / 2

        x0, y0 = (self.x, self.y - half_height - ABILITY_MARGIN_TOP)
        x1, y1 = (self.x + width + ABILITY_MARGIN_RIGHT + ABILITY_MARGIN_LEFT,
                  self.y + half_height + ABILITY_MARGIN_BOTTOM)

        # save the incoming pos (where dependents connect) for 0th level
        self.incoming_pos = (x0, self.y)
        
        # save the outgoing positions
        level_x = self.x + self.width
        level_y = self.y - half_height - ABILITY_MARGIN_TOP + CIRCLE_RADIUS
        for level in self.ability.get_levels():
            number = str(level.get_level_number())
            xt, yt, width, height, dx, dy = context.text_extents(number)
            self.connector_posns[level.get_level_number()] = (level_x, level_y)            
            level_y += 2 * CIRCLE_RADIUS + CIRCLE_VERTICAL_SEPARATOR

        # save the outgoing offsets
        # (this is complicated)
        level_x = 0
        level_y = half_height - ABILITY_MARGIN_TOP # + CIRCLE_RADIUS
        for level in self.ability.get_levels():
            number = str(level.get_level_number())
            xt, yt, width, height, dx, dy = context.text_extents(number)
            #level_y += height / 2
            self.connector_offsets[level.get_level_number()] = (level_x, level_y)
            level_y += 2 * CIRCLE_RADIUS + CIRCLE_VERTICAL_SEPARATOR
        return
        

    def get_width(self):
        return self.width
    
    
    def draw_ability(self, context):

        # get the text size
        title = self.ability.get_title()
        (xt, yt, width, height, dx, dy) = context.text_extents(title)
        half_width = width / 2
        half_height = height / 2

        x0, y0 = (self.x, self.y - half_height - ABILITY_MARGIN_TOP)
        x1, y1 = (self.x + width + ABILITY_MARGIN_RIGHT + ABILITY_MARGIN_LEFT,
                  self.y + half_height + ABILITY_MARGIN_BOTTOM)
        # draw box
        context.move_to(x0, y0)
        context.line_to(x1, y0)
        context.line_to(x1, y1)
        context.line_to(x0, y1)
        context.line_to(x0, y0)
        context.stroke_preserve()        
        context.set_source_rgb(1, 1, 1)
        context.fill()
        context.set_source_rgb(0, 0, 0)

        # draw little ball on the left.
        context.arc(self.x, self.y, 2, 0, 2.0*math.pi)
        context.fill()

        # draw ability label
        context.move_to(self.x + ABILITY_MARGIN_LEFT, self.y + half_height)
        context.show_text(title)

        # draw the ability levels.
        level_x = x1 + ABILITY_LEVEL_SEPARATOR
        level_y = self.y - half_height - ABILITY_MARGIN_TOP + CIRCLE_RADIUS
        for level in self.ability.get_levels():
            number = str(level.get_level_number())
            
            (xt, yt, width, height, dx, dy) = context.text_extents(number)
            context.move_to(level_x - dx/2, level_y + height/2)

            context.arc(level_x, level_y, CIRCLE_RADIUS, 0, 2.0*math.pi)
            context.stroke_preserve()        
            context.set_source_rgb(1, 1, 1)
            context.fill()
            context.set_source_rgb(0, 0, 0)
            
            context.move_to(level_x - dx/2, level_y + height/2)
            context.show_text(number)
            context.stroke()            
            
            level_y += 2 * CIRCLE_RADIUS + CIRCLE_VERTICAL_SEPARATOR
        return

    def get_incoming_pos(self):
        return self.incoming_pos

    def get_outgoing_pos(self, level_number):
        return self.connector_posns[level_number]

    def get_outgoing_offset(self, level_number):
        posn = self.connector_posns[level_number]
        # print "x %s" % self.x
        # print "y %s" % self.y
        # print "px %s" % posn[0]
        # print "py %s" % posn[1]
        return (posn[0] - self.x, posn[1] - self.y)
    
    # def get_outgoing_offset(self, level_number):
    #     return self.connector_offsets[level_number]
    
    def get_pos(self):
        return (self.x, self.y)
        

class AbilityNodes(dict):
    
    def __init__(self, values={}):
        super(AbilityNodes, self).__init__(values)
        return


    def get_relative_pos(self, ability_id, seen_ability_ids=None):

        if seen_ability_ids is None:
            seen_ability_ids = []

        _, relative_ability_id, points =  SKILL_POSITION_LOOKUP[ability_id]

        x = 0
        y = 0
        for dx, dy in points:
            x += dx
            y += dy

        # position is on a grid
        x *= HSTEP
        y *= VSTEP

        #print "--- " + ability_id

        if relative_ability_id is not None:
            has_cyclic_dependency = relative_ability_id in seen_ability_ids

            seen_ability_ids.append(relative_ability_id)

            # check for a cyclic depdendency (they're not allowed).
            if has_cyclic_dependency:
                raise Exception("Cyclic depenedency in ability prerequsitess: %s."
                                % ",".join(seen_ability_ids))

            x2, y2 = self.get_relative_pos(relative_ability_id,
                                           seen_ability_ids=seen_ability_ids)

            try:
                relative_ability_node = self[relative_ability_id]
            except KeyError:                
                raise Exception("Problem finding parent %s for ability %s" %
                                (relative_ability_id, ability_id))
            
            x += x2 + relative_ability_node.get_width()
            y += y2

        return x, y


def included_skill(ability, current_page):
    ability_id = ability.get_id()
    page, _, _ =  SKILL_POSITION_LOOKUP[ability_id]    
    if page == current_page:
        return True
    return False

    
class SkillTreeBuilder:
    """
    Object that lays out the skill tree.

    """
    def __init__(self, page):
        # Which page to draw
        self.page = page

        # the graphical representation of the abilities
        # (an ability_id -> ability_node dict)
        self.ability_nodes = AbilityNodes()
        return


    def build(self, ability_groups, fname):
        _, ext = splitext(fname)
        if ext == ".eps":
            surface = cairo.PSSurface(fname, WIDTH, HEIGHT)
            surface.set_eps(True)
        elif ext == ".svg":
            surface = cairo.SVGSurface(fname, WIDTH, HEIGHT)
        elif ext == ".pdf":
            surface = cairo.PDFSurface(fname, WIDTH, HEIGHT)
        else:
            raise Exception("Unknown ability tree image type: %s" % ext)

        context = cairo.Context(surface)
        context.set_source_rgba(0, 0, 0, 1.0)
        context.set_line_width(1)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)

        # paint background
        context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        context.rectangle(0, 0, WIDTH, HEIGHT)
        context.fill()    

        # setup font
        context.select_font_face("Verdana",
                                 cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(FONT_SIZE)
        context.set_source_rgb(0, 0, 0)

        # abilities.
        ability_keys = set([ability.get_id() for ability in ability_groups.get_abilities()])

        # calculate the widths..
        for ability in ability_groups.get_abilities():
            ability_node = AbilityNode(ability=ability)
            ability_node.calc_size(context)
            self.ability_nodes[ability.get_id()] = ability_node

        # sanity check 
        for ability_id, value in SKILL_POSITION_LOOKUP.items():        
            if ability_id not in ability_keys:
                raise Exception("SKILL_POSITION_LOOKUP has key for an ability that "
                                "no longer exists: %s" % ability_id)

            _, parent_id, _ = value        
            if parent_id is not None and parent_id not in SKILL_POSITION_LOOKUP:
                raise Exception("SKILL_POSITION_LOOKUP missing key for an ability : %s"
                                % parent_id)

        # sanity check 
        for key in ability_keys:
            if key not in SKILL_POSITION_LOOKUP:
                raise Exception("SKILL_POSITION_LOOKUP missing key for an ability : %s"
                                % key)

        # layout
        for ability_node in self.ability_nodes.values():

            if not included_skill(ability_node.ability, current_page=self.page):
                continue        
            ability_node.layout(context=context,
                                ability_nodes=self.ability_nodes)
        # draw the edges
        self.draw_edges(context, ability_groups)

        # draw the nodes
        for ability_node in self.ability_nodes.values():
            if not included_skill(ability_node.ability, current_page=self.page):
                continue
            ability_node.draw_ability(context=context)

        surface.finish()
        return


    def draw_spline(self, context, from_point, to_point, dashed=False):

        # turn on dashed lines for prereqs that aren't our direct parent
        if dashed:
            context.set_dash([3.0, ])

        # draw arrow
        x0, y0 = from_point
        x3, y3 = to_point
        x1, y1 = x0 + SPLINE_HORIZONTAL_LEAD, y0
        x2, y2 = x3 - SPLINE_HORIZONTAL_LEAD, y3
        context.move_to(x0, y0)
        context.curve_to(x1, y1, x2, y2, x3, y3)
        context.stroke()

        # turn off dashed lines for prereqs that aren't our direct parent
        if dashed:
            context.set_dash([])
        return

    
    def draw_line(self, context, p1, p2, colour):
        context.set_source_rgb(*colour)
        context.move_to(p1[0], p1[1])
        context.line_to(p2[0], p2[1]) 
        context.stroke()
        context.set_source_rgb(0.0, 0.0, 0.0)
        return


    def draw_edges(self, context, ability_groups):
        for ability in ability_groups.get_abilities():

            if not included_skill(ability, current_page=self.page):
                continue

            to_node = self.ability_nodes[ability.get_id()]

            for ability_level in ability.get_levels():
                for prereq in ability_level.get_ability_level_prereqs():

                    from_id = prereq.get_ability().get_id()
                    try:
                        from_node = self.ability_nodes[from_id]

                    except KeyError:
                        raise Exception("Can't find prereq %s for %s" %
                                        (prereq, ability_level.get_id()))

                    ability_level_number = prereq.get_ability_level().get_level_number()

                    # get the relative parent for the node
                    _, relative_parent_id, points = SKILL_POSITION_LOOKUP[ability.get_id()]

                    dashed = from_id != relative_parent_id
                    from_point = from_node.get_outgoing_pos(ability_level_number)
                    to_point = to_node.get_incoming_pos()

                    if dashed:
                        # FIXME: enforce one parent per ability.
                        raise Exception("Ability parent mismatch: %s has a parent %s "
                                        "but the ability graph thinks its parent is %s"
                                        % (ability_level.get_id(),
                                           from_id, relative_parent_id))

                    # the relative positions are relative to the center of the node
                    # so we have to offset the relative positions based on the distance
                    # from the center of the start node to its outgoing point
                    offset = from_node.get_outgoing_offset(ability_level_number)
                    #print "Offset %s" % str(offset)
                    
                    abs_points = []
                    abs_points.append(from_point)
                    for i in range(len(points)):
                        last_point = abs_points[-1]
                        dpos = points[i]

                        if i == 0:
                            point = (last_point[0], last_point[1] - offset[1])
                        else:
                            point = last_point

                        # calc spline ponit relative to the to_node.
                        point = (point[0] + dpos[0], point[1] + dpos[1])

                        abs_points.append(point)

                    # draw a single (multi-spline) connection
                    for i in range(len(abs_points)-1):
                        p1 = abs_points[i]
                        p2 = abs_points[i+1]
                        self.draw_spline(context=context,
                                         from_point=p1,
                                         to_point=p2,
                                         dashed=dashed)
        return


if __name__ == "__main__":
    # load the abilities
    abilities_dir = join(root_dir, "abilities")
    ability_groups = AbilityGroups()
    ability_groups.load(abilities_dir, fail_fast=True)

    fname = "build/ability_tree1.pdf"
    skill_tree_builder = SkillTreeBuilder(page=Page.ONE)
    skill_tree_builder.build(ability_groups, fname=fname)

    fname = "build/ability_tree2.pdf"
    skill_tree_builder = SkillTreeBuilder(page=Page.TWO)
    skill_tree_builder.build(ability_groups, fname=fname)
