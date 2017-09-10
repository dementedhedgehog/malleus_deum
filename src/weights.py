#!/usr/bin/python


FROM = 40 # kgs
TO = 110 # kgs


POUND = 2.20462

class Imperial:

    def __init__(self, kgs):
        self.convert(kgs)
        return

    def convert(self, kgs):
        self.pounds = kgs * POUND
        return

    def __str__(self):
        return "%i pounds" % self.pounds
    

for kgs in range(FROM, TO + 1):
    pounds = Imperial(kgs)
    print "%8s kgs --> %8s" % (kgs, pounds)
    
