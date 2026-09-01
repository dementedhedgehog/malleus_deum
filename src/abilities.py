#!/usr/bin/env python3
"""

  I was going to have ability ranks have their own settings for
  checks and damage and promotions etc .. but that's way too
  complicated.  All that's move into Ability now so this code
  is currently a mess.

"""
from os.path import join
from os import listdir

import utils
from utils import (
    parse_xml,
    get_error_context,
    is_comment,
    children_to_string,
    contents_to_string,
    contents_to_string2,
    contents_to_comma_separated_str,
    contents_to_list,
    node_to_string,
    get_child_name,
    root_dir,
    parse_xml_list,
    parse_xml_keyword_list,
    ability_groups_dir,
)

# constants
ANTAGONIST = "Aspect"



class SpecializationRef:
    """Specialization part of an AbilityRef"""

    def __init__(self):
        self.name = None
        self.rank = None

    def parse(self, specialization_rank_str):
        """
        Parse a specialization-rank str.  Format is specialization-name
        followed by an optional :rank
        """
        tokens = specialization_rank_str.split(":")
        self.specialization = tokens[0]
        if len(tokens) > 1:
            self.rank = int(tokens[1])
        return

    def __str__(self):        
        return f"{self.name}:{self.rank}"
        

class AbilityRef:
    """Reference to an ability"""
    def __init__(self):
        self._id = None
        self.rank = None
        self.ability = None
        self.specializations = []
        self.dmg = None
        return

    def parse(self, node):
        self._id = node.attrib["id"]

        rank = node.attrib.get("rank")
        self.rank = int(rank) if rank is not None else None
        dmg_str = node.attrib.get("dmg")
        if dmg_str is not None:
            self.dmg = int(dmg_str)
        specializations = node.attrib.get("specializations")
        if specializations is not None:
            for specialization_rank in specializations.split(","):
                s = SpecializationRef()
                s.parse(specialization_rank)
                self.specializations.append(s)
        assert node.attrib.get("template") is None
        return

    def get_skill_value(self):
        return self.rank + 11

    def get_specializations_str(self):
        return ", ".join([str(s) for s in self.specializations])

    @classmethod
    def from_ability(cls, ability):
        ability_ref = cls()
        ability_ref._id = ability.get_id()
        return ability_ref

    def get_id(self):
        return self._id

    def get_rank(self):
        return self.rank

    def to_str(self):
        return f'<abilityref id="{self._id}" rank="{self.rank}"/>'

    def __str__(self):
        return self.to_str()


class AbilityStage:
    """
    Stages.. like for different levels of poisoned in PF2e

    """
    def __init__(self):
        self.name = None
        self.description = None


    def parse(self, stage_element, fname):
        for child in list(stage_element):
            tag = child.tag
            if tag == "name":
                self.name = contents_to_string(child)
          
            elif tag == "description":
                self.description = contents_to_string(child)
                
            elif is_comment(child):
                # ignore comments!
                pass

            else:
                raise Exception("UNKNOWN (%s) in file %s\n" % 
                                (child.tag, fname))
        return
        
    

MIN_INITIAL_ABILITY_RANK = -6
MAX_INITIAL_ABILITY_RANK = 9

# Lookup table from ability-rank-id :--> ability-rank
#ability_rank_lookup = {}


def parse_spline(point_nodes):
    """
    We use splines in the skill tree graphs

    """
    points = []
    for point_node in point_nodes:
        x = float(point_node.attrib["x"])
        y = float(point_node.attrib["y"])
        points.append((x, y))
    return points




class Specialization:
    """An alternative ability rank"""

    def __init__(self, name, ability):
        self.name = name
        self.ability = ability

    def get_name(self):
        return self.name

    def get_rank_number(self):
        return 3  # for now

    def get_checks(self):
        return []

    def get_full_name(self):
        return (self.ability.get_id().split(".")[-1] + "." + self.name).lower()

    def get_long_name(self):
        return (self.ability.get_id() + "." + self.name).lower()


class AttrPrereq: # (Prerequisite):

    def __init__(self, attr, value):
        self.attr = attr
        self.value = value
        return

    @classmethod
    def parse_xml(cls, prereq_attr_node):
        """
        Return a list of prereq attrs.

        """
        prereqs = []
        for child in list(prereq_attr_node):
            tag = child.tag
            #if tag is COMMENT:
            if is_comment(child):#  tag is COMMENT:
                # ignore comments!
                pass
            else:
                # We know the tag is a valid attribute
                # because xsd validation requires it.
                attr = tag
                value = int(child.text)
                prereqs.append(AttrPrereq(attr, value))
        return prereqs

    def to_string(self):
        return "%s>%s" % (self.attr, self.value)

    def get_name(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()


class TagPrereq: #(Prerequisite):
    """
    Tag prerequisites.

    """
    def __init__(self, tag):
        self.tag = tag
        return

    def to_string(self):
        return "Tag: %s" % self.tag

    def get_name(self):
        return self.tag

    def __str__(self):
        return self.to_string()


class NotTagPrereq: # (Prerequisite):

    def __init__(self, tag):
        self.tag = tag
        return

    def to_string(self):
        return "Not %s" % self.tag

    def get_title(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()


class AbilityCheck:
    """
    An ability check configuration.

    """

    def __init__(self, ability):
        self.ability = ability

        # Check Type e.g. Check, CounterCheck
        self.check_class = None

        # can be None for the default
        self.name = None

        # Things like physical, magic, melee .. used for crit tables.
        self.check_type = None

        # Pool point default cost.
        self.pool_cost = None
        
        # Action point cost
        self.ap_cost = None

        # range of the attack/spell etc, in meters/yards
        self.check_range = None

        # Requirements to make the check.
        self.requires = None

        # 
        self.precondition = None
        self.effect = None
        self.dmg = None

        # Countercheck if any.
        self.counter = None
        
        # list of tags for the ability
        self.keywords = []

        # line number of the start of the ability check.
        self.line_number = None

        # Skill Outcomes
        self.any_success = None
        self.critsuccess = None
        self.righteoussuccess = None
        self.success = None
        self.any_fail = None
        self.fail = None
        self.grimfail = None
        self.critfail = None

        # Fate Outcomes
        self.blessed = None
        self.lucky = None
        self.damned = None
        self.cursed = None

    def get_name(self):
        return self.name

    def get_check_type(self):
        return self.check_type

    
    def get_ap_cost(self):
        """
        Returns the Action Point cost of the check.

        """
        return self.ap_cost

    def get_pool_cost(self):
        return self.pool_cost
    
    def get_pool_cost_str(self):

        if self.pool_cost is None:
           return None

        keywords = self.get_keywords()
        if "Magic-Pool" in keywords:
            pool = "Magic Pool"
        elif "Mettle-Pool" in keywords:
            pool =  "Mettle Pool"
        elif "Luck-Pool" in keywords:
            pool = "Luck Pool"
        else:
            raise Exception(f"Unknown pool cost!\n{self.ability}")
        
        return f"{self.pool_cost} {pool}"

    def get_keywords(self):
        return sorted(list(set(self.keywords + self.ability.get_keywords())))

    def get_keywords_str(self):
        return ", ".join(self.get_keywords()).strip()

    def get_range(self):
        return self.check_range

    def get_precondition(self):
        return self.precondition

    def get_effect(self):
        return self.effect

    def _throw_error(self, node, msg):
        context = get_error_context(self.ability.fname, node.sourceline) 
        raise Exception(
            f"{msg}: ({node.tag}) {node.text} in "
            f"{self.ability.fname}:{node.sourceline}\n"
            f"{context}\n")
    
    def _load(self, ability_check_element):

        # Get the type of check. (Check or Countercheck).
        self.check_class = ability_check_element.get("readable-type")
        if self.check_class is None:
            raise Exception(str(ability_check_element))
        #print(f"check class %s" % self.check_class)

        # handle all the children
        for child in list(ability_check_element):

            if self.line_number is None:
                self.line_number = child.sourceline

            tag = child.tag
            if tag == "name":
                self.name = contents_to_string(child)

            elif tag == "checktype":
                #self.check_type = contents_to_string(child)

                check_type = list(child)[0]
                self.check_type = contents_to_string(check_type)
                if self.name == "":
                    self.name = self.check_type

            elif tag == "poolcost":
                if self.pool_cost is not None:
                    self._throw_error(child,
                                      "Only one poolcost element per check")
                else:
                    self.pool_cost = int(child.text)

            elif tag == "apcost":
                self.ap_cost = child[0].text                
                if self.ap_cost is None:
                    # APCost is a keywordType in the xsd.  So if you get this
                    # error check you've set a fixed attribute value for the
                    # keyword.
                    self._throw_error(child, "Unknown apcost")                

            elif tag == "range":
                if len(child):
                    range_node = child[0]
                    self.check_range = range_node.text
                else:
                    self._throw_error(child, "MISSING range?")                

            elif tag == "requires":
                if self.requires is None:
                    self.requires =  ", ".join(parse_xml_keyword_list(child))
                else:
                    self._throw_error(
                        child,
                        "Only one requires element per check")

            elif tag == "precondition":
                self.precondition = contents_to_string(child).strip()

            elif tag == "effect":
                self.effect = contents_to_string(child).strip()

            elif tag == "counter":
                if len(child):
                    counter = child[0]
                    self.counter = node_to_string(counter)
                else:
                    self._throw_error(child, "MISSING counter?")                

            elif tag == "range":
                self.ability_range = contents_to_string(child).strip()

            elif tag == "keywords":
                self.keywords += parse_xml_keyword_list(child)

            # elif tag == "result":
            #     if len(child):
            #         result = child[0]
            #         if result.text:
            #             # If it has a fixed text value then use that
            #             self.result = result.text
            #         else:
            #             # Otherwise pass the whole element.  Let the formatter
            #             # sort it out.
            #             self.result = node_to_string(result)
            #     else:
            #         self._throw_error(child, "Problem with result?")

            elif tag == "dmg":
                self.dmg = contents_to_string(child).strip()

            elif tag == "critsuccess":
                self.critsuccess = contents_to_string2(child).strip()

            elif tag == "righteoussuccess":
                self.righteoussuccess = contents_to_string2(child).strip()

            elif tag == "success":
                self.success = contents_to_string2(child).strip()

            elif tag == "fail":
                self.fail = contents_to_string2(child).strip()

            elif tag == "grimfail": # FIXME REMOVE..
                self.grimfail = contents_to_string2(child).strip()

            elif tag == "critfail":
                self.critfail = contents_to_string2(child).strip()

            elif tag == "any-success":
                self.any_success = contents_to_string2(child).strip()

            elif tag == "any-fail":
                self.any_fail = contents_to_string2(child).strip()

            elif tag == "blessed":
                self.blessed = contents_to_string2(child).strip()

            elif tag == "lucky":
                self.lucky = contents_to_string2(child).strip()

            elif tag == "damned":
                self.damned = contents_to_string2(child).strip()

            elif tag == "cursed":
                self.cursed = contents_to_string2(child).strip()
    
            elif is_comment(child): # .tag is not COMMENT:
                # ignore comments!
                pass

            else:
                self._throw_error(child, f"UNKNOWN tag ({tag})")                
        return

    def __str__(self):
        return f"{self.name}"

    def get_problems(self):
        problems = []

        #
        # FIXME: move these to schematron
        #

        #
        # Check the tags are set properly.
        #
        keywords = self.get_keywords()

        # Normalize 'save' behaviour
        # Saves don't have these values, they're determined by the opposed check
        if problem := self._check_not_field_if_keyword("save", "critsuccess"):
            problems.append(problem)

        if problem := self._check_not_field_if_keyword("save", "righteoussuccess"):
            problems.append(problem)

        # All defend checks are also save checks
        if "defend" in keywords and "countercheck" not in keywords:
            problems.append(f"Ability {self.ability.title} in "
                            f"{self.ability.fname}:{self.line_number} has a "
                            f"a 'defend' keyword (one of {keywords}) but does "
                            "not have a 'save' keyword.  (All defence checks are "
                            "also save checks)!\n")
        return problems

    def is_pool_check(self):
        pool_keywords = self.get_pool_keywords()
        return len(pool_keywords) > 0

    _pool_keywords = {"magicpool", "mettlepool", "luckpool", "aspectpool"}
    def get_pool_keywords(self):
        keywords = set(self.get_keywords())
        return  keywords.intersection(self._pool_keywords)    

    def get_pool_keywords_str(self):
        return  ", ".join(self.get_pool_keywords())
    
    def _create_problem(self, msg):
        """Helper to format xml configuration errors with some useful data."""
        return (f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} "
                f"{msg}\n")    

    def _check_keyword_if_field(self, keyword, field_name):
        keywords = self.get_keywords()
        field_value = getattr(self, field_name)
        if field_value and not keyword in keywords:
            return self._create_problem(
                f"has a value for the {field_name} set. but does not "                
                f" have the '{keyword}' keyword (one of {keywords})\n")
        return None
        

    def _check_field_if_keyword(self, keyword, field_name):
        keywords = self.get_keywords()
        field_value = getattr(self, field_name)
        if keyword in keywords and not field_value:                    
            return (
                f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} has "
                f"a '{keyword}' keyword (one of {keywords}) but does not "
                f"have a value for the {field_name} set.\n")
        return None
        
    def _check_not_field_if_keyword(self, keyword, field_name):
        keywords = self.get_keywords()
        field_value = getattr(self, field_name)
        if keyword in keywords and field_value:                    
            return (
                f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} has "
                f"a '{keyword}' keyword (one of {keywords}) but "
                f"*has* a value for the {field_name} set.\n")
        return None
        
    def _check_name_if_keyword(self, keyword, check_name, contains=False):
        """
        We enforce a naming scheme on check names to try and reduce 
        complexity.

        """
        keywords = self.get_keywords()

        if keyword not in keywords:
            return None
        
        if contains:
            if check_name not in self.name:
                return (
                    f"Ability {self.ability.title} in "
                    f"{self.ability.fname}:{self.line_number} has "
                    f"a '{keyword}' keyword (one of {keywords}) but does not "
                    f"have a check name that contains '{check_name}' it has a "
                    f"check name: '{self.name}' (checks with a {keyword} "
                    f"keyword must have a name containing the word: "
                    f"{check_name}).\n")
            
        elif self.name != check_name:
            return (
                f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} has "
                f"a '{keyword}' keyword (one of {keywords}) but does not "
                f"have a check name '{check_name}' it has a check name: "
                f"'{self.name} (checks with a {keyword} "
                f"keyword must have the check name {check_name}).\n")
        return None
        
    def has_outcomes(self): 
        """
        Helper for formatting abilities in docs.

        """
        return (self.any_success or 
                self.critsuccess or
                self.righteoussuccess or 
                self.success or 
                self.any_fail or 
                self.fail or 
                self.grimfail or
                self.critfail or
                self.blessed or
                self.lucky or
                self.damned or
                self.cursed)
        
    def get_outcomes(self):
        """
        Helper for formatting abilities in docs.

        """
        outcomes = []
        if self.any_success:
            outcomes.append(("Any Success", self.any_success))

        if self.critsuccess:
            outcomes.append(("Critical Success", self.critsuccess))

        if self.righteoussuccess:
            outcomes.append(("Righteous Success", self.righteoussuccess))

        if self.success:
            outcomes.append(("Success", self.success))

        if self.any_fail:
            outcomes.append(("Any Fail", self.any_fail))

        if self.fail:
            outcomes.append(("Fail", self.fail))

        # FIXME REMOVE THIS... (failure's are annoying)
        if self.grimfail:
            outcomes.append(("Grim Fail", self.grimfail))

        if self.critfail:
            outcomes.append(("Critical Fail", self.critfail))

        if self.blessed:
            outcomes.append(("Blessed", self.blessed))

        if self.lucky:
            outcomes.append(("Lucky", self.lucky))

        if self.damned:
            outcomes.append(("Damned", self.damned))

        if self.cursed:
            outcomes.append(("Cursed", self.cursed))

        return outcomes
    
    
class Ability:
    """
    An ability.

    """
    # set of all ability ids we've seen there should be no duplicates!
    _ids = {}
    
    def __init__(self, fname, ability_group_id):
        self.fname = fname
        self.name = None
        self.ability_id = None
        self.slug = None        
        self.description = None
        self.specializations = []
        self.group_id = ability_group_id

        # Checks .. a dictionary from name->check details. An ability can have
        # multiple check configurations
        self.checks = []

        # List of template parameters for antag checks (e.g. damage, result).
        #self.param_check_default = None  FIXME USE RANK INSTEAD
        self.param_dmg_default = None
        self.param_stage_default = None # 
        self.param_rank_default = None # suggestion for antag abilities.
        
        # prereq.
        #self.ability_rank_prereq = None
        self.ability_ref_prereq = None

        # all the prerequisites including the prereq_ability_rank
        self.prerequisites = []        

        # list of tags for the ability
        self.keywords = []

        # list of available ability ranks.
        #self.ranks = []

        # list of ability refs for this ability
        self.refs = []

        # list of available ranks (ints).
        self.ability_ranks = []

        # list of specializations
        self.specializations = []

        # if this element is not none it should be a number in [-9, -6, -3, 0]
        # the rank at which untrained players make the check
        self.untrained_rank = None

        # list of spline points .. used for laying out the ability
        # in a graph in the phb.
        self.spline = []

        # Ability stages
        self.stages = []
        
        # the group this ability belongs to.
        self.ability_group = None
        return

    # def get_range(self):
    #     return self.ability_range

    def get_name(self):
        return self.name

    def has_parameters(self):
        return (# self.param_check_default or
                self.param_dmg_default or
                self.param_rank_default or
                self.param_stage_default)

    def is_antag_ability(self):
        return ANTAGONIST in self.keywords

    def get_parameters_str(self):
        params = []
        #if self.param_check_default:
        #    params.append(f"SSV: {self.param_check_default}")
        if self.param_dmg_default:
            params.append(f"Dmg: {self.param_dmg_default}")
        if self.param_stage_default:
            params.append(f"Stage: {self.param_stage_default}")
        if self.param_rank_default:
            params.append(f"Rank: {self.param_rank_default}")
        return ", ".join(params)

    def get_keywords(self):
        return sorted(self.keywords + self.ability_group.get_keywords())

    def has_keywords(self):
        return len(self.get_keywords()) > 0

    def get_keywords_str(self):
        return ",".join(self.get_keywords())
    
    def __str__(self):
        #return f"✱{self.ability_id}"
        #return self.ability_id}"
        return AbilityRef.from_ability(self).to_str()

    def set_group(self, ability_group):
        self.ability_group = ability_group
            
    def get_group_id(self):
        return self.ability_group.get_id()

    def get_specializations_str(self):
        return ", ".join([s.name for s in self.specializations])
        
    # FIXME: what has this got to do with check_sanity?
    def get_problems(self):
        """Checks for malformed abilities.. returns a list of problems."""
        problems = []                
        
        for check in self.checks:
            problems += check.get_problems()

        # rank numbers can have an optional initial untrained/negative rank,
        # after that the should be a continuous range of increasing positive
        # ints (or zero), e.g. -3, 0, 1, 2, 3 or 1, 2, 3, 4 are both valid.
        last_rank_number = None
        is_first_rank = True
        for rank_number in self.get_trained_ranks():
                
            # check the first rank is always 0 or 1 (primary abilities can be
            # lower).
            if is_first_rank:
                if ((rank_number < MIN_INITIAL_ABILITY_RANK
                     or rank_number > MAX_INITIAL_ABILITY_RANK)
                    and "primary" not in self.keywords):
                    problems.append(
                        f"First rank for ability {self.get_name()} is {rank_number} "
                        f"should be {MIN_INITIAL_ABILITY_RANK} to {MAX_INITIAL_ABILITY_RANK}")
                is_first_rank = False
            else:
                if last_rank_number + 1 != rank_number:
                    problems.append("Bad rank numbers for ability %s around rank  %s"
                                    % (self.get_name(), rank_number))
            last_rank_number = rank_number
        return problems

    def get_trained_ranks(self):
        if self.is_untrained():
            if len(self.ability_ranks) > 1:
                return self.ability_ranks[1:]
            else:
                return []
        else:
            return self.ability_ranks

    def check_sanity(self):
        problems = self.get_problems()
        if len(problems) > 0:
            raise Exception(", ".join([str(p) for p in problems]))
        return    

    def get_ability_ref_prereq(self):
        return self.ability_ref_prereq

    def is_valid_rank(self, rank):
        return int(rank) in self.ranks

    def has_ranks(self):
        return len(self.ability_ranks) > 0
    
    def get_ability_rank_range(self):
        if not self.has_ranks():
            return None
        trained_ranks = self.get_trained_ranks()
        first_ability_rank = trained_ranks[0]
        last_ability_rank = trained_ranks[-1]
        ability_ranks = f"{first_ability_rank}-{last_ability_rank}"
        return ability_ranks

    def is_core(self):  # FIXME: WHAT DOES THIS MEAN?
        return "core" in self.keywords

    def is_pool(self):
        return "pool" in self.keywords

    # def get_rank_number(self):
    #     """
    #     Make ability look like ability rank so we can
    #     treat them the same-ish in other code
    #     (duck-typing ftw).

    #     """
    #     return None

    def get_name(self):
        """Return the abilities name."""
        return self.name

    def get_ability_rank(self, rank_number):
        for ability_rank in self.ranks:
            if ability_rank.get_rank_number() == rank_number:
                return ability_rank
        return None

    def get_prerequisites_str(self):
        #if self.prerequisites:
        prereqs = ", ".join([str(p) for p in self.prerequisites])
        #else:
        #    prereqs = ""
        return prereqs

    def get_attr_modifiers(self):
        return self.attr_modifiers

    def get_description(self):
        return self.description

    def get_ranks(self):
        return self.ability_ranks

    def get_id(self):
        """Returns something like conjuration.ignis_2"""
        return self.ability_id

    # def get_short_id(self):
    #     """For conjuration.ignis_2 this will return the string ignis_2"""
    #     return self.ability_id.split(".")[-1]

    def get_checks(self):
        return self.checks

    def has_prerequisites(self):
        # has_prereqs = False
        # for rank in self.ranks:
        #     if rank.has_prerequisites():
        #         has_prereqs = True
        #         break
        # return has_prereqs
        return len(self.prerequisites) > 0

    def __iter__(self):
        return iter(self.get_ranks())

    def load(self, ability_element):
        # check it's the right sort of element
        if ability_element.tag not in ("ability", "antagability"):
            raise Exception(
                "UNKNOWN (%s) %s\n" %
                (ability_element.tag,
                 str(ability_element)))
        self._load(ability_element)
        return

    def _get_location(self, lxml_element):
        return "%s:%s" % (self.fname, lxml_element.sourceline)

    def _load(self, ability_element):
        # handle all the children
        for child in list(ability_element):
            tag = child.tag
            if tag == "abilitytitle":
                if self.name is not None:
                    raise Exception(
                        "Only one abilitytitle per ability. (%s) %s\n" %
                        (child.tag, str(child)))
                else:
                    self.name = child.text

            elif tag == "abilityid":
                if self.ability_id is not None:
                    raise Exception(
                        "Only one abilityid per ability. (%s) %s\n" %
                        (child.tag, str(child)))
                else:
                    # check for duplicates - ability ids should be unique!
                    ability_id = child.text
                    ability_location = self._get_location(child)
                    if ability_id in self._ids:
                        raise Exception(
                            "Ability id: %s appears in two places %s and %s"
                            % (ability_id,
                               ability_location,
                               self._ids[ability_id]))
                    else:
                        self._ids[ability_id] = ability_location

                    # save the id!
                    self.ability_id = ability_id

            elif tag == "slug":
                self.slug = contents_to_string(child)
 
            # elif tag == "param-check-default":
            #     #self.param_check_default = children_to_string(child).strip()
            #     self.param_check_default = ", ".join(contents_to_list(child))

            elif tag == "param-dmg":
                self.param_dmg_default = child.text.strip()

            elif tag == "param-stage":
                self.param_stage_default = child.text.strip()

            elif tag == "param-rank":
                self.param_rank_default = child.text.strip()

            elif tag in ("abilitycheck", "abilitycountercheck",
                         "abilityantagcheck",
                         "abilityopposed", 
                         "abilityauxiliary"):

                # Ability check type is an xsd fixed attribute.
                ability_check = AbilityCheck(ability=self)
                ability_check._load(child)
                self.checks.append(ability_check)

            elif tag == "abilityranks":
                # if len(self.ranks) > 0: #  is not None:
                #     raise Exception(
                #         "Only one abilityranks per ability. (%s) %s\n" %
                #         (child.tag, str(child)))
                # else:
                #     self.load_ability_ranks(child)
                if len(self.ability_ranks) > 0: #  is not None:
                    raise Exception(
                        "Only one abilityranks per ability. (%s) %s\n" %
                        (child.tag, str(child)))
                else:
                    self.load_ability_ranks(child)
                    
            elif tag == "abilitydescription":
                if self.description is not None:
                    raise Exception(
                        "Only one abilitydescription per ability. (%s) %s\n" %
                        (child.tag, str(child)))
                else:
                    self.description = children_to_string(child)

            # elif tag == "prereqabilityrank":
            #     ability_rank_id = child.text
            #     if ability_rank_id is not None:
            #         prereq = AbilityRankPrereq(ability_rank_id)
            #         self.ability_rank_prereq = prereq
            #         self.prerequisites.append(prereq)

            elif tag == "prereqabilityref":                
                ability_ref = AbilityRef()
                ability_ref.parse(child)
                self.ability_ref_prereq = ability_ref
                self.prerequisites.append(ability_ref)

            elif tag == "prereqattr":
                prereqs = AttrPrereq.parse_xml(child)
                self.prerequisites += prereqs

            elif tag == "prereqtag":
                prerequisite_tag = child.text
                if prerequisite_tag is not None:
                    prereq = TagPrereq(prerequisite_tag)
                    self.prerequisites.append(prereq)

            elif tag == "prereqnottag":
                prerequisite_tag = child.text
                if prerequisite_tag is not None:
                    prereq = NotTagPrereq(prerequisite_tag)
                    self.prerequisites.append(prereq)

            elif tag == "keywords":
                self.keywords += parse_xml_keyword_list(child)

            elif tag == "spline":
                self.spline = parse_spline(child.getchildren())

            elif tag == "specializations":
                self.parse_specializations(child.getchildren())

            elif tag == "stage":
                stage = AbilityStage()
                stage.parse(child, fname=self.fname)
                self.stages.append(stage)
    
            elif is_comment(child):
                # ignore comments!
                pass

            else:
                raise Exception("UNKNOWN (%s) in file %s\n" % 
                                (child.tag, self.fname))
        return


    def parse_specializations(self, specializations_element):
        """
        Parse a list of ability specializations from an xml
        specializations element.

        """
        for specialization_element in specializations_element:
            specialization_name = contents_to_string(specialization_element)
            specialization = Specialization(
                name=specialization_name,
                ability=self)
            self.specializations.append(specialization)
            print(specialization.get_full_name())
            print(specialization.get_long_name())
            # ability_rank_lookup[specialization.get_full_name()] = specialization
            # ability_rank_lookup[specialization.get_long_name()] = specialization
        return


    def is_untrained(self):
        return self.untrained_rank is not None

    def get_untrained_rank(self):
        if self.untrained_rank is None:
            return None
        return self.ability_ranks[0]

    # def _add_ability_rank(self, rank_number):
    #     """Add an ability rank."""
    #     rank = AbilityRank()
    #     rank.ability = self
    #     rank.rank_number = rank_number
    #     rank_id = rank.get_id()
        
    #     assert "." not in rank_id
    #     ability_rank_lookup[rank_id] = rank
    #     self.ranks.append(rank)
    #     return
    

    def _add_ability_ref(self, rank):
        """Add an ability ref."""
        ref = AbilityRef()
        ref.ability = self
        ref.rank = rank_number
        #rank_id = rank.get_id()        
        #assert "." not in rank_id
        #ability_rank_lookup[rank_id] = rank
        self.refs.append(ref)
        return

    # def load_ability_ranks(self, ability_ranks):
    #     untrained_rank = ability_ranks.attrib.get("untrained", None)
    #     if untrained_rank is not None:
    #         self.untrained_rank = int(untrained_rank)
    #         self._add_ability_rank(self.untrained_rank)

    #     from_rank = int(ability_ranks.attrib["from"])
    #     to_rank = int(ability_ranks.attrib["to"])
    #     for rank_number in range(from_rank, to_rank+1):
    #         self._add_ability_rank(rank_number)
    #     return

    def load_ability_ranks(self, ability_ranks):
        untrained_rank = ability_ranks.attrib.get("untrained", None)
        if untrained_rank is not None:
            self.untrained_rank = int(untrained_rank)
            #self._add_ability_rank(self.untrained_rank)
            self.ability_ranks.append(self.untrained_rank)

        from_rank = int(ability_ranks.attrib["from"])
        to_rank = int(ability_ranks.attrib["to"])
        for rank_number in range(from_rank, to_rank+1):
            #self._add_ability_rank(rank_number)
            self.ability_ranks.append(rank_number)
        return
    

class AbilityGroupInfo:
    """
    A group of abilities

    """
    # The set of all ability ids we've seen.
    # There should be no duplicates!
    _ids = {}

    def __init__(self, fname):
        self.fname = fname
        self.name = None
        self.ability_group_id = None
        self.description = None
        self.slug = None        
        self.family_id = None
        self.keywords = []

        # Should we draw a skill tree when documenting the ability group?
        # (Some ability groups are very flat with no relationships)
        self.draw_skill_tree = True

        # Should this ability group be included in the docs?
        self.enabled = True
        return

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def load(self, ability_group_info_element):
        # check it's the right sort of element
        if ability_group_info_element.tag != "abilitygroupinfo":
            raise Exception(
                "UNKNOWN (%s) %s\n" %
                (ability_group_info_element.tag,
                 str(ability_group_info_element)))
        self._load(ability_group_info_element)
        return

    def _load(self, ability_group_info_element):
        # handle all the children
        for child in list(ability_group_info_element):
           tag = child.tag
           if tag == "abilitygrouptitle":
               if self.name is not None:
                   raise Exception("Only one abilitygrouptitle per file.")
               else:
                   self.name = child.text.strip()

           elif tag == "dontdrawskilltree":
               self.draw_skill_tree = False

           elif tag == "abilitygroupid":
               if self.ability_group_id is not None:
                   raise Exception(
                       "Only one abilitygroupid per ability. (%s) %s\n" %
                       (child.tag, str(child)))
               else:
                   node = list(child)[0]
                   self.ability_group_id = node.tag
                   ability_group_location = f"{self.fname}:{node.sourceline}"
                   
           elif tag == "abilitygroupfamily":
               if self.family_id is not None:
                   raise Exception(
                       "Only one abilitygroupfamily per ability. (%s) %s\n" %
                       (child.tag, str(child)))
               else:
                   family_ids = parse_xml_keyword_list(child)
                   if len(family_ids) != 1:
                       raise Exception(
                           "Expecting 1 family id: got %s and %s"
                           % (len(family_ids), contents_to_string(child)))
                   # save the id!
                   self.family_id = family_ids[0]

           elif tag == "keywords":
               self.keywords = parse_xml_keyword_list(child)

           elif tag == "slug":
                self.slug = contents_to_string(child)

           elif tag == "abilitygroupdescription":
               if self.description is not None:
                   raise Exception("Only one abilitygroupdescription per file.")
               else:
                   self.description = children_to_string(child)

           #elif tag is COMMENT:
           elif is_comment(child):
               pass # ignore comments!

           elif tag == "enabled":
               self.enabled = True

           elif tag == "disabled":
               self.enabled = False

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return

    def get_id(self):
        return self.ability_group_id


class AbilityGroup:
    xsd_schema = None

    def __init__(self, fname):
        self.fname = fname
        self.doc = parse_xml(fname)
        self.info = None
        self.abilities = []
        return

    def get_ability(self, ability_id):
        if "wyrd" in self.get_id():
            print(f"Get ability {[a.get_id() for a in self.abilities]}")
        for ability in self.abilities:
            if ability.ability_id == ability_id:
                assert isinstance(ability, Ability)
                return ability            
        return None

    def get_keywords(self):
        all_keywords = self.info.keywords + [
            self.info.family_id,
            #self.info.ability_group_id
        ]
        return sorted(list(set(all_keywords)))

    def get_keywords_str(self):
        return ", ".join(self.get_keywords())

    def get_root_abilities(self):
        """
        Return a list of abilities that have no prerequisites.

        """
        root_abilities = []
        for ability in self.abilities:
            if ability.ability_ref_prereq is None:
                root_abilities.append(ability)
        return root_abilities

    def get_name(self):
        return f"{self.info.name} {len(self.abilities)}"

    def get_abilities(self):
        return self.abilities

    def get_id(self):
        return self.info.ability_group_id

    def get_info(self):
        return self.info

    def get_description(self):
        return self.info.get_description()

    def is_aspect_family(self):
        return self.info.family_id == "Aspect"

    def is_lore_family(self):
        return self.info.family_id == "Lore"

    def is_general_family(self):
        return self.info.family_id == "General"

    def is_magic_family(self):
        return self.info.family_id == "Magic"

    def is_martial_family(self):
        return self.info.family_id == "Martial"

    def is_primary_family(self):
        return self.info.family_id == "Primary"

    def is_common_family(self):
        return self.info.family_id == "Common"

    def is_wyrd_science_family(self):
        return self.info.family_id == "Wyrd-Science"

    def is_hazards_family(self):
        return self.info.family_id == "Hazards"

    def is_conditions_family(self):
        return self.info.family_id == "Conditions"

    def get_family(self):
        return self.info.family_id

    def __iter__(self):
        return iter(self.abilities)

    def has_abilities(self):
        return len(self.abilities) != 0

    def __cmp__(self, other):
        return cmp(self.get_name(), other.get_name())

    def __lt__(self, other):
        return self.get_name()  < other.get_name()

    def load(self, node = None):
        if node is None:
            root = self.doc.getroot()
        else:
            root = node

        # check it's the right sort of element
        if root.tag != "abilitygroup":
            raise Exception("UNKNOWN (%s) %s\n" % (root.tag, str(root)))

        # handle all the children of the ability group
        for child in list(root):
           tag = child.tag
           if tag == "abilitygroupinfo":
               if self.info is not None:
                   raise Exception("Only one abilitygroupinfo per file."
                                   f"Filename: {self.fname}")
               else:
                   self.info = AbilityGroupInfo(self.fname)
                   self.info.load(child)

           elif tag == "ability" or tag == "antagability" :
               ability = Ability(self.fname, ability_group_id=self.get_id())
               try:
                   ability.load(child)
               except Exception as e:
                    # Add some extra debug info if we can.
                    e.add_note(f"File name: {self.fname}")
                    raise
               ability.set_group(self)
               self.abilities.append(ability)

           #elif tag is COMMENT:
           elif is_comment(child):
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return

    def get_rank(self):
        return self.info.rank

    def draw_skill_tree(self):
        return self.info.draw_skill_tree

    def get_problems(self):
        """
        Perform some sanity checks.

        """
        problems = []
        group_id = self.info.ability_group_id

        if "_" in group_id:
            problems.append(f"Group id {group_id} contains an underscore.  "
                            "Latex doesn't like underscores. "
                            "Use a hyphen instead.")
        return problems

    def check_sanity(self):
        problems = self.get_problems()
        if len(problems) > 0:
            raise Exception(", ".join([str(p) for p in problems]))
        return


class AbilityGroups:
    """
    A list of all abilities.

    """
    def __init__(self):
        self.ability_groups = []

        # id -> ability, e.g. "perception" -> Perception Ability obj
        self.ability_lookup = {}
        return

    def get_abilities_children(self, ability):
        """
        Return a list of abilities that require this ability
        as a prerequisite.

        """

        print(f"GET ABILITIES CHILDREN {ability.get_id()}")
        children = []

        # Do it the hard way.
        found = None
        ability_id = ability.get_id()
        print(f"\t{ability_id}")
        for group in self.ability_groups:
            # if "wyrd" in group.get_id():
            #     print(f"\tGroup {group}")
            assert isinstance(group, AbilityGroup)
            #group_ability = group.get_ability(ability_id)
            #if group_ability is None:
            #    continue
            #assert isinstance(ability, Ability)
            #print(f"\t{group_ability}")
            
            print(f"\t --- ability .. {ability}")
            for a2 in group:
                print(f"\t\t --- child? .. {a2.get_id()}")
                if a2.ability_ref_prereq is not None:
                    a2_prereq_id = a2.ability_ref_prereq.get_id()
                    ability_prereq = self.get_ability(a2_prereq_id)
                    print(f"\t\t XXX {ability_prereq}")
                    if ability_prereq is None:
                        #prereq_id = ability_ref_prereq.get_ability_rank_id()
                        raise Exception(
                            f"Ability prereq {ability_prereq} does not "
                            f"exist for ability: {ability.get_name()} "
                            f"{a2.get_name()}")
                    if ability_prereq == ability:
                        children.append(a2)
        return children


    def __iter__(self):
        return iter(self.ability_groups)

    def get_abilities(self):
        for group in self.ability_groups:
            for ability in group.get_abilities():
                yield ability
        return

    def get_abilities_by_family(self, family_type):
        abilities = []
        for ability_group in self.ability_groups:
            if ability_group.info.family_id == family_type:
                for ability in ability_group.get_abilities():
                    abilities.append(ability)
        abilities = sorted(abilities, key=lambda ability: ability.title)
        return abilities

    def get_abilities_by_family_paginated(self, family_type, page_size=30):
        abilities = self.get_abilities_by_family(family_type)
        return [abilities[i:i+page_size]
                for i in range(0, len(abilities), page_size)]

    def get_ability(self, ability_id: str):
        for group in self.ability_groups:
            ability =  group.get_ability(ability_id)
            if ability is not None:
                return ability
        return None

    def get_ability_group(self, ability_group_id):
        for group in self.ability_groups:
            if group.get_id() == ability_group_id:
                return group
        return None

    def load(self, abilities_dir, fail_fast):

        # load all the ability groups
        for xml_fname in listdir(abilities_dir):

            if not xml_fname.endswith(".xml"):
                continue

            if xml_fname.startswith(".#"):
                continue

            xml_fname = join(abilities_dir, xml_fname)
            ability_group = AbilityGroup(xml_fname)
            ability_group.load()

            self.ability_groups.append(ability_group)

            # populate the ability_id -> ability lookup table
            for ability in ability_group.get_abilities():
                self.ability_lookup[ability.get_id()] = ability

        # sort the groups
        self.ability_groups.sort()

        # die if anything is misconfigured.
        self.check_sanity()
        return True

    def check_sanity(self):
        """
        Checks the "correctness" of the configuration.
        Complains if it doesn't like it.

        """
        for ability_group in self:
            for ability in ability_group:
                ability.check_sanity()
                ability_group.check_sanity()
        return

    def get_ability_groups(self):
        return self.ability_groups

    def __getitem__(self, key):
        return self.ability_groups[key]

    def get_ability_rank_total_prereqs(self , ability_rank, prereqs=None):
        """
        Gets a list of all the prereqs for this ability rank
        (including this ability rank).

        """
        if prereqs is None:
            prereqs = set()
        rank_number = ability_rank.get_rank_number()
        prereqs.add(ability_rank)

        ability = ability_rank.get_ability()
        for i in range(1, rank_number):
            pal = ability.get_ability_rank(i)
            get_ability_rank_total_prereqs(
                self,
                pal,
                prereqs=prereqs)

        for prereq in ability_rank.get_prerequisites():
            if isinstance(prereq, AbilityRankPrereq):
                prereq_ability_rank = self.get_ability_rank(
                    prereq.ability_rank_id)
                get_ability_rank_total_prereqs(
                    ability_groups,
                    prereq_ability_rank,
                    prereqs=prereqs)
        return prereqs


    def tabulate(self, n_lines_per_page, n_columns, n_lines_first_page=None):
        abilities = []
        for g in self:
            for a in g:
                abilities.append(a)

        sort_by_title = lambda a: a.get_name()
        abilities.sort(key=sort_by_title)
        
        return utils.tabulate(abilities,
                              n_lines_per_page,
                              n_columns,
                              n_lines_first_page=n_lines_first_page)



def generate_ability_check_table():
    """
    Creates an html table listing all the abilities and their checks.

    """
    ability_groups = AbilityGroups()
    ability_groups.load(ability_groups_dir, fail_fast=True)

    count = 0
    abilities = []
    for g in ability_groups:
        for a in g:
            abilities.append(a)

    sort_by_title = lambda a: a.get_name()
    abilities.sort(key=sort_by_title)

    fname = "abilities.html"
    with open(fname, "w") as f:
        f.write("<html>\n")
        f.write("\t<body>\n")
        f.write('\t\t<table style="border: 1px solid black;">\n')
        
        f.write("\t\t\t<tr>\n")
        f.write(f"\t\t\t\t<th>Ability Name</th>\n")
        f.write(f"\t\t\t\t<th>Check Name</th>\n")
        f.write(f"\t\t\t\t<th>Check Type</th>\n")
        f.write("\t\t\t</tr>\n")
        
        for ability in abilities:
            for check in ability.get_checks():

                n = check.get_name()
                f.write("\t\t\t<tr>\n")
                f.write(f"\t\t\t\t<td>{ability.get_name()}</td>\n")
                f.write(f"\t\t\t\t<td>{check.get_name()}</td>\n")
                f.write(f"\t\t\t\t<td>{check.check_type}</td>\n")
                f.write("\t\t\t</tr>\n")

        f.write("\t\t</table>\n")
        f.write("\t</body>\n")
        f.write("</html>\n")

    import webbrowser
    webbrowser.open(fname)
    return
    

if __name__ == "__main__":
    ability_groups = AbilityGroups()
    ability_groups.load(ability_groups_dir, fail_fast=True)

    #for k, v in ability_rank_lookup.items():
    #    print(f"{k}: {v}")

    # g = ability_groups.get_ability_group("lore")


    for g in ability_groups:
        print(g.get_family())
    
    
    # a = g.get_ability("alchemy")
    # print(a)
    # print(a.keywords)
    # print(a.ability_group.get_keywords())

    # print(g.info.keywords)
    # print("X")
    # print(g.info.family_id)
    # print(g.info.ability_group_id)
    

    #for ability in a.abilities:
    #    print(ability)
    #assert isinstance(n, Ability)
    #c = ability_groups.get_abilities_children(n)
    # PROBlEM C is Empty!
    #print(f"---> {n} {c}")


