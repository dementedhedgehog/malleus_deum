"""

   Generate the Check Difficulty Table.

   Shows actor rank vs object rank = prob success.

   This is done semi-manually.  It prints a partial table and you can paste it
   into a table xml file.  (This shouldn't change too much).

"""

actor_ranks = (-6, -3, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
object_ranks = (-6, -3, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

#
# You need to write your own table start and end code.. we're only doing the
# rows here.
#

def get_prob(actor_rank, object_rank):
    return  max(1, min(20, (actor_rank - object_rank + 11))) * 5 # percent

#
# Table Header Rows
#
print(f"""
  <tableheaderrow>
    <th></th>
    <th width="{len(object_ranks)}" align="c">Object Ranks</th>
  </tableheaderrow>

  <tableheaderrow>
    <th>Actor Rank</th>""")
for object_rank in object_ranks:
    print(f'    <th align="c">{object_rank}</th>')
print("    </tableheaderrow>\n")

for actor_rank in actor_ranks:
    print("    <tablerow>", end="")
    print(f'<td align="c">{actor_rank}</td>', end="")
    for object_rank in object_ranks:
        prob = get_prob(actor_rank, object_rank)
        print(f'<td align="r">{prob}<percent/></td>', end="")
    print("</tablerow>")
