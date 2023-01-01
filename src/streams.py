import re
from copy import copy

from utils import (
    #node_to_string,
    contents_to_string,
    COMMENT,
)

class TagConstraint:
    """
    This is an ability tag (like martial), not an xml element tag.

    """
    def __init__(self):
        self.tag = None

    def parse(self, fname, tag_op):
        self.tag = contents_to_string(tag_op)
        return

    def matches(self, ability):
        return self.tag in ability.get_tags()


ability_regex = re.compile(
    "✱?"
    "(?P<ability_id>[a-zA-Z]+\.[a-zA-Z]+)"
    "(?P<template>\[[a-zA-Z\-\?]\]]?)?"
    "(?P<rank>(?:_)0-9)?")
    
class AbilityConstraint:
    """
    This represents a specific ability or ability-rank

    """
    def __init__(self):
        self.ability_id = None
        self.rank = None
        self.template = None

    def parse(self, fname, ability_op):
        token = contents_to_string(ability_op)
        match = ability_regex.match(token)
        if match is not None:
            self.ability_id = match.group("ability_id")
            self.template = match.group("template")
            self.rank = match.group("rank")
        return

    def matches(self, ability):

        #print(f"  {ability.get_id()} ==? {self.ability_id}")
        
        if self.ability_id == ability.get_id():
            if self.rank is not None:
                return ability.is_valid_rank(self.rank)
            else:
                # matches and no rank specified.
                return True
        return False


        

    
    
class Operator:

    def __init__(self):
        self.operands = []
        
        
    def matches(self, tags):
        raise NotImplementedError

    def parse(self, fname, node):
        # handle all the children
        for child in list(node):

            tag = child.tag
            if tag == "or":
                or_op = OrNode()
                or_op.parse(fname, child)
                self.operands.append(or_op)

            elif tag == "and":
                and_op = AndNode()
                and_op.parse(fname, child)
                self.operands.append(and_op)

            elif tag == "not":
                not_op = NotNode()
                not_op.parse(fname, child)
                self.operands.append(not_op)
                
            elif tag == "tag":
                tag_constraint = TagConstraint()
                tag_constraint.parse(fname, child)
                self.operands.append(tag_constraint)
               
            elif tag == "ability":
                ability_constraint = AbilityConstraint()
                ability_constraint.parse(fname, child)
                self.operands.append(ability_constraint)
               
            elif tag is COMMENT:
                # ignore comments!
                pass
            else:
                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                                (child.tag, fname, child.sourceline))
        return True


    def __iter__(self):
        return iter(self.operands)
    

            

    
class AndNode(Operator):

    def matches(self, ability):
        for expression in self.operands:
            if not expression.matches(ability):
                return False
        return True


class OrNode(Operator):

    def matches(self, ability):
        for expression in self.operands:
            if expression.matches(ability):
                return True
        return False
    


class NotNode(OrNode):

    def __init__(self):
        OrNode.__init__(self)

    def matches(self, ability):
        return not OrNode.matches(self, ability)    


class Stream:

    def __init__(self):
        self.title = None
        self.min_level = 1
        self.max_level = 3

        # local constraints on the abilities for this stream
        self.operands = []

        # children
        self.streams = []        

        # This is a list of abilities the stream matches directly.
        self.simple_abilities = set()
        
        # list of  abilities described by this stream.
        # available after we resolve abilities.
        self.resolved_abilities = set()

    def get_id(self):
        return self.title

    def parse(self, fname, node):
        self.title = node.get("id", None)

        # handle all the children
        for child in list(node):

            tag = child.tag
            if tag == "or":
                or_op = OrNode()
                or_op.parse(fname, child)
                self.operands.append(or_op)

            elif tag == "and":
                and_op = AndNode()
                and_op.parse(fname, child)
                self.operands.append(and_op)

            elif tag == "not":
                not_op = NotNode()
                not_op.parse(fname, child)
                self.operands.append(not_op)
                
            elif tag == "tag":
                tag_constraint = TagConstraint()
                tag_constraint.parse(fname, child)
                self.operands.append(tag_constraint)
               
            elif tag == "ability":
                ability_constraint = AbilityConstraint()
                ability_constraint.parse(fname, child)
                self.operands.append(ability_constraint)
               
            elif tag == "stream":
                stream = Stream()
                stream.parse(fname, child)
                self.streams.append(stream)
               
            elif tag is COMMENT:
                # ignore comments!
                pass
            else:
                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                                (child.tag, fname, child.sourceline))
        return True

        


    def walk(self, all_streams=None):
        """
        Append any streams to the list of streams passed in.

        """
        if all_streams is None:
            all_streams = []
        all_streams.extend(self.streams)
        for stream in self.streams:
            stream.walk(all_streams)
        return all_streams

    def match_abilities(self, all_abilities):
        for ability in all_abilities:
            if self.matches(ability):
                self.simple_abilities.add(ability)
        return

    def matches(self, ability):
        for expression in self.operands:
            if expression.matches(ability):
                return True
        return False
    
        
    
    

class StreamConfig(Stream):

    def parse(self, fname, streams_node):
        """
        Parse the xml.

        """
        # handle all the children
        for child in list(streams_node):
            
           tag = child.tag
           if tag == "stream":
               stream = Stream()
               stream.parse(fname, child)
               # if stream.title in self.streams:
               #     raise Exception(f"Stream {stream.title} appears in streams in {fname} twice")               
               self.streams.append(stream)

           elif tag is COMMENT:
               # ignore comments!
               pass
               
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))
        return


    def resolve_abilities(self, fname, abilities):
        all_streams = self.walk()

        # check the names of the streams first.
        stream_names = set()
        for stream in all_streams:
            if stream.title in stream_names:
                raise Exception(f"There are two or more streams with the name {stream.title} in "
                                f"the file {fname}")            
            stream_names.add(stream.title)

        # assign all matching "simple" abilities to each stream.
        for stream in all_streams:
            stream.match_abilities(abilities)


        # abilities from child streams are removed from parent streams.
        # First build a set of edges from stream to stream (parent, child).
        edges = set() 
        for stream in all_streams:
            for child in stream.streams:
                edges.add((stream, child))
            stream.resolved_abilities = copy(stream.simple_abilities)

        # subtract all the child abilities from the parent abilities            
        for parent, child in edges:
            print(f" f{parent.title} f{child.title} ")
            parent.resolved_abilities -= child.simple_abilities
        return
                


    def __iter__(self):
        return iter(self.streams)

    def __len__(self):
        return len(self.streams)
