
# Dice Mechanics

A discussion on the new mechanics for Malleus Deum.  We'll refer 
to the old mechanics as MD1.

Problems with the old system dice mechanics:
 - Not a sufficiently large range of results.  E.g. Most results of 
 a 2d12 system fall in the 6-18 range.  This makes it a little difficult
 for fine scale min/maxing - which some people enjoy.  If the granularity
 of your results are too large then it's hard to have extra bonuses without 
 unbalancing the system.  Contrariwise, if the granularity is too small
 then bonuses become meaningless.
 (like Pathfinder's +1 to hit but only when the moon is full, and you're
 attacking frogs of small or medium size with a mace)
 - The dice mechanics have no way of knowing whether the check succeeded or not.
 Which makes it hard to assign meaning to the results.  E.g. if you roll two 10s 
 that's a boon, but it might not be a success (e.g. hit in melee).
 - Boons and banes are too frequent in MD1 and they are ill-defined.


Other problems:
 - Organizing abilities and finding abilities.  Is/will be fixed by having 
  a set of standard abilities that everyone has e.g. same as Skills in
  Pathfinder (in PF2e they are Acrobatics, Arcana, Athletics, etc..).  This 
  was always the plan but now the character sheet actually is organized to 
  show this.
 - The dice pool system was complicated and hard to balance in the face of 
   level progression.
 - Level progression not defined.


## Goals

Greater variety of outcomes. 
: We want more than hit, miss, crit hit and crit miss results.
: Different results like having to make a weapon or armour break check, 
: dropping an item, falling prone, losing actions etc.. for spells they
: can be extra cost to cast, miscasting (rarely) etc.

Well defined outcomes.
: Being the GM and constantly having to choose what crits
: mean is a little draining.  It's hard to keep thinking
: of novel outcomes.

Simple.
: Not overly complicated. Learnable without resorting to a 
: lot of tables.

One dice system.  One dice mechanism.
: No dice pools. This is a corollary of the Simple requirement.

Special results with the same frequency of the d20 system.
: 1 in 20 seems to be a sweet spot for special results.  I imagine
: it's fine to have "great results" with a lower frequency, say
: 1 in 100 but I think 1 in 20 is sufficiently rare that it's 
: exciting when it happems, but sufficiently common that it 
: happens fairly frequently.

A bit more egalitarian than PF2e
: e.g. there are plenty of checks in PF2e that have a DC of, say, 30.
: Only those with a +12 in that ability have a reasonable chance of
: succeeding. This stops people from attempting things their character 
: is shit at. I'd like for there to be a *bit* less of a chasm between doing the 
: things you're trained at and not trained at for most things.

Player Facing
: The players do most of the rolling.. check for attacks and checking for
: defending against monster attacks.

Triggers
: We want to be able to allow some (secondary) abilities to be triggered
: semi-randomly, e.g. see the example from 13th age below (the 13th age 
: triggers get very complicated so it's just to illustrate the point here).
: In MD1 doubles used to be special with evens and odds being good or bad.
: The problem with this is that if you 

> *Counter-Attack - example from 13th Age*
> Once per round when the escalation die is even and an enemy
> misses you with a natural odd melee attack roll, you can make a
> basic melee attack dealing half damage against that enemy as a
> free action. (The attack can’t use any limited abilities or flexible
> attack maneuvers.)


## Current Proposed Mechanic

The mechanic I'm thinking about currently is as follows.
Two d20 of different colours that are rolled simultaneously and interpreted
separately (they're not added together). The lighter colour dice we'll call
the Skill die, the darker colour die we'll call the Fate die.

The dice pools are replaced by point pools, e.g. you'll have Magic, Mettle and
Luck point pools and certain abilities have a point cost to cast.  (so they're
similar to the Stamina and Health hit point pools).  Aspects will also have a 
pool cost of some sort (one point pool per aspect). 


### The Skill Die ###
The interpretation of the Skill die is similar to that of a normal d20 system.
To make a check you add the rank of the ability you're using to the face value
of the Skill die and you succeed if that *result* is >= a DC.

Special results are as follows: 

If the face value is 20 that's a Crit Success
If the face value is 1 that's a Crit Fail
If the *result* is >= DC+8 that's a Righteous Success (the 8 number is debatable should be < 10 though).
If the *result* is >= DC that's a Success
If the *result* is < DC that's a Fail
If the *result* is < DC-8 that's a Grim Fail


I see these different results being interpreted in fairly standard ways, e.g for melee:
Success does weapon damage (a constant), Righteous Success does weapon damage x2, a 
Critical Success does weapon damage x3.

Any Knowledge checks would have something like a Success gets, say, 2 true facts and 1
false fact, fail get 1 true fact and 2 false facts, a Righteous Success gets 3 true facts.

Spells would define their own bespoke outcomes for these different results.  Damage dealing spells would probably all have the same kind of damage modification as the melee abilities.

For defence abilities a Success means no damage, a fail means full damage, and a grim fail means 2x damage.

Misc abilities like climbing would have their own interpretations per check.. with for example, a Fail you don't make it but you can try-agin, Grim Fail means check athletics or fall or something along those lines.

Each aspect has its own DC and own point pool (or maybe uses the Mettle pool).  Successes reduce the DC for subsequent checks.


A crit fail results in a roll on a fumble table (with broad categories of results, e.g. melee, melee defence, spell, knowledge, language, ranged attack, fire/acid?, poison? falling? etc).



### The Fate Die ###


The other d20, the Fate die, is used to trigger other random stuff.  The result is 
the face value of the die plus the Rank.  Results are interpreted as follows:

If the face value is 20 the result is said to be *Blessed*
If the face value is 1 it's *Damned*
If the *result* is >= 20 it's a *Boon*
If the *result* is >= 8 it's *Indifferent*
If the *result* is < 8 it's a *Bane*

Ability Ranks max out at say +6


E.g. of how these results might be interpreted as follows:

Melee .. Secondary abilities can be triggered by these results.. Mighty Blow might trigger when you make a melee attack with a Boon+Righteous Success.  You might have a Sneaky Git ability that lets you get a free step on any Boon.

Magic.. Boons have half magic point cost to cast, Bane's have 2x magic point cost to cast.

The same point pool expense results would apply to any of the point pool abilities.

Knowledge Checks.. Boon +1 true fact, Bane +1 false fact.

(For the purposes of triggering things the Skill results are subsets of one another all Crit Successes are Successes, All Righteous Successes are Successes...)

Furthermore in opposed checks (pc vs monster, pc vs hazard) the various results can be used to trigger events/abilites for the opposition.  E.g. Orcs might have a retaliate where they get a free counter attack every time you roll a Bane in melee against them.




My main concern with the approach described is that the extra complexity might be a pain to play with.  Also frequency of Banes and Boons change with Rank (it might be reasonable to not add Rank to the Fate die and use fixed DCs).
