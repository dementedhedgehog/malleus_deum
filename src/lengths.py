#!/usr/bin/python


FROM = 100 # cms
TO = 200 # cms


FOOT = 30.48
INCH = 2.54

class Imperial:

    def __init__(self, cms):
        self.convert(cms)
        return

    def convert(self, cms):
        self.feet = cms // FOOT
        self.inches = (cms -  self.feet * FOOT) / INCH
        return

    def __str__(self):
        return "%i'%i\"" % (self.feet, self.inches)
    

for cms in range(FROM, TO  + 1):
    imp = Imperial(cms)
    print "%8s cm --> %8s" % (cms, imp)
    
