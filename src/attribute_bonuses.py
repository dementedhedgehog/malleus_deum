#!/usr/bin/env python

class AttrBonus:

    # map from level number -> dictionary of classname -> bonus
    level_lookup = {}
    
    def __init__(self, level, value):
        self.level = level
        self.value = value

        if level not in AttrBonus.level_lookup:
            AttrBonus.level_lookup[level] = {}

        #print value
        AttrBonus.level_lookup[level][self.__class__.__name__] = value
        assert isinstance(AttrBonus.level_lookup[level],  dict)
        #self.x = "T"
        return

    #@classmethod
    #def __getitem__(cls, key):
    #    return cls.level_lookup[key]

class StrDmgBonus(AttrBonus):
    pass

class StrHealthBonus(AttrBonus):
    pass

class StaminaEnduranceBonus(AttrBonus):
    pass

class ACAgilityBonus(AttrBonus):
    pass

class InitiativeSpeedBonus(AttrBonus):
    pass

class MoveSpeedBonus(AttrBonus):
    pass

class FateLuckBonus(AttrBonus):
    pass

class ResolveWillpowerBonus(AttrBonus):
    pass

class MagicWillpowerBonus(AttrBonus):
    pass

#
#  Attribute Bonus Table Data
#
StrDmgBonus(3, -4)
StaminaEnduranceBonus(3, 0)
StrHealthBonus(3, 0)
ACAgilityBonus(3, -3)
InitiativeSpeedBonus(3, -3)
MoveSpeedBonus(3, -2)
FateLuckBonus(3, "+0<d4/>")
ResolveWillpowerBonus(3, "+0<d4/>")
MagicWillpowerBonus(3, "+0<d4/>")

StrDmgBonus(4, -3)
StaminaEnduranceBonus(4, 0)
StrHealthBonus(4, 0)
ACAgilityBonus(4, -2)
InitiativeSpeedBonus(4, -2)
MoveSpeedBonus(4, -1)
FateLuckBonus(4, "+0<d4/>")
ResolveWillpowerBonus(4, ":+0<d4/>")
MagicWillpowerBonus(4, "+0<d4/>")

StrDmgBonus(5, -2)
StaminaEnduranceBonus(5, 0)
StrHealthBonus(5, 0)
ACAgilityBonus(5, -1)
InitiativeSpeedBonus(5, -1)
MoveSpeedBonus(5, -1)
FateLuckBonus(5, "+0<d4/>")
ResolveWillpowerBonus(5, "+0<d4/>")
MagicWillpowerBonus(5, "+0<d4/>")

StrDmgBonus(6, -1)
StaminaEnduranceBonus(6, 0)
StrHealthBonus(6, 0)
ACAgilityBonus(6, -1)
InitiativeSpeedBonus(6, -1)
MoveSpeedBonus(6, -1)
FateLuckBonus(6, "+0<d4/>")
ResolveWillpowerBonus(6, "+0<d4/>")
MagicWillpowerBonus(6, "+0<d4/>")


StrDmgBonus(7, 0)
StaminaEnduranceBonus(7, 0)
StrHealthBonus(7, 0)
ACAgilityBonus(7, +0)
InitiativeSpeedBonus(7, +0)
MoveSpeedBonus(7, +0)
FateLuckBonus(7, "+0<d4/>")
ResolveWillpowerBonus(7, "+0<d4/>")
MagicWillpowerBonus(7, "+0<d4/>")

StrDmgBonus(8, 0)
StaminaEnduranceBonus(8, 0)
StrHealthBonus(8, 0)
ACAgilityBonus(8, +0)
InitiativeSpeedBonus(8, +0)
MoveSpeedBonus(8, +0)
FateLuckBonus(8, "+1<d4/>")
ResolveWillpowerBonus(8, "+1<d4/>")
MagicWillpowerBonus(8, "+0<d4/>")

StrDmgBonus(9, 0)
StaminaEnduranceBonus(9, 1)
StrHealthBonus(9, 1)
ACAgilityBonus(9, 0)
InitiativeSpeedBonus(9, +0)
MoveSpeedBonus(9, +0)
FateLuckBonus(9, "+1<d4/>")
ResolveWillpowerBonus(9, "+1<d4/>")
MagicWillpowerBonus(9, "+1<d4/>")

StrDmgBonus(10, 1)
StaminaEnduranceBonus(10, 1)
StrHealthBonus(10, 1)
ACAgilityBonus(10, 1)
InitiativeSpeedBonus(10, +1)
MoveSpeedBonus(10, +0)
FateLuckBonus(10, "+1<d4/>")
ResolveWillpowerBonus(10, "+1<d4/>")
MagicWillpowerBonus(10, "+1<d4/>")

StrDmgBonus(11, 1)
StaminaEnduranceBonus(11, 2)
StrHealthBonus(11, 2)
ACAgilityBonus(11, 1)
InitiativeSpeedBonus(11, +1)
MoveSpeedBonus(11, +0)
FateLuckBonus(11, "+2<d4/>")
ResolveWillpowerBonus(11, "+2<d4/>")
MagicWillpowerBonus(11, "+2<d4/>")

StrDmgBonus(12, +2)
StaminaEnduranceBonus(12, 3)
StrHealthBonus(12, 3)
ACAgilityBonus(12, 2)
InitiativeSpeedBonus(12, +2)
MoveSpeedBonus(12, +0)
FateLuckBonus(12, "+3<d4/>")
ResolveWillpowerBonus(12, "+3<d4/>")
MagicWillpowerBonus(12, "+3<d4/>")

StrDmgBonus(13, 3)
StaminaEnduranceBonus(13, 4)
StrHealthBonus(13, 4)
ACAgilityBonus(13, 2)
InitiativeSpeedBonus(13, +2)
MoveSpeedBonus(13, +1)
FateLuckBonus(13, "+3<d4/>")
ResolveWillpowerBonus(13, "+3<d4/>")
MagicWillpowerBonus(13, "+3<d4/>")

StrDmgBonus(14, 4)
StaminaEnduranceBonus(14, 5)
StrHealthBonus(14, 5)
ACAgilityBonus(14, 3)
InitiativeSpeedBonus(14, +3)
MoveSpeedBonus(14, +1)
FateLuckBonus(14, "+4<d4/>")
ResolveWillpowerBonus(14, "+4<d4/>")
MagicWillpowerBonus(14, "+4<d4/>")

StrDmgBonus(15, 5)
StaminaEnduranceBonus(15, 6)
StrHealthBonus(15, +6)
ACAgilityBonus(15, 3)
InitiativeSpeedBonus(15, +3)
MoveSpeedBonus(15, +1)
FateLuckBonus(15, "+4<d4/>")
ResolveWillpowerBonus(15, "+5<d4/>")
MagicWillpowerBonus(15, "+4<d4/>")


StrDmgBonus(16, 6)
StaminaEnduranceBonus(16, 7)
StrHealthBonus(16, 7)
ACAgilityBonus(16, 4)
InitiativeSpeedBonus(16, +4)
MoveSpeedBonus(16, +2)
FateLuckBonus(16, "+4<d4/>")
ResolveWillpowerBonus(16, "+5<d4/>")
MagicWillpowerBonus(16, "+4<d4/>")


StrDmgBonus(17, 7)
StaminaEnduranceBonus(17, 8)
StrHealthBonus(17, 8)
ACAgilityBonus(17, 4)
InitiativeSpeedBonus(17, +4)
MoveSpeedBonus(17, +2)
FateLuckBonus(17, "+5<d4/>")
ResolveWillpowerBonus(17, "+6<d4/>")
MagicWillpowerBonus(17, "+4<d4/>")


StrDmgBonus(18, 8)
StaminaEnduranceBonus(18, 9)
StrHealthBonus(18, 9)
ACAgilityBonus(18, 5)
InitiativeSpeedBonus(18, +5)
MoveSpeedBonus(18, +3)
FateLuckBonus(18, "+6<d4/>")
ResolveWillpowerBonus(18, "+6<d4/>")
MagicWillpowerBonus(18, "+5<d4/>")


StrDmgBonus(19, 9)
StaminaEnduranceBonus(19, 10)
StrHealthBonus(19, 10)
ACAgilityBonus(19, 6)
InitiativeSpeedBonus(19, +6)
MoveSpeedBonus(19, +3)
FateLuckBonus(19, "+7<d4/>")
ResolveWillpowerBonus(19, "+7<d4/>")
MagicWillpowerBonus(19, "+5<d4/>")

StrDmgBonus(20, 10)
StaminaEnduranceBonus(20, +11)
StrHealthBonus(20, +11)
ACAgilityBonus(20, 7)
InitiativeSpeedBonus(20, +7)
MoveSpeedBonus(20, +3)
FateLuckBonus(20, "+8<d4/>")
ResolveWillpowerBonus(20, "+8<d4/>")
MagicWillpowerBonus(20, "+6<d4/>")

# export something readable
attribute_bonuses = AttrBonus.level_lookup
