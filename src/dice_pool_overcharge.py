#!/usr/bin/python3
"""

  Investigate dice pool mechanics with overflow.

"""
import math
import functools
from os.path import join
import pygal
from utils import build_dir


ONE_SIXTH = 1/6.0
FIVE_SIXTH = 5/6.0
MAX_DC = 30

# @functools.lru_cache
# def prob_sixes_in_pool(n_sixes, pool_size):
#     """
#     Returns the probability of getting "n_sixes" when rolling "pool_size" d6's.

#     """
#     assert n_sixes >= 0 and n_sixes <= pool_size
#     return math.comb(pool_size, n_sixes) * ONE_SIXTH**n_sixes * FIVE_SIXTH**(pool_size-n_sixes)


# @functools.lru_cache
# def prob_overcharge(n_sixes, pool_size):
#     prob = 0.0
#     for n in range(n_sixes, pool_size+1):
#         prob += prob_sixes_in_pool(n, pool_size)
#     return prob

# @functools.lru_cache
# def get_overcharge_probs(n_sixes, pool_size, max_dc=MAX_DC):

#     # get the range we'll graph the overcharge over.
#     min_dc = min(n_sixes, MAX_DC)
#     new_max_dc = min(6*n_sixes, 6*pool_size, max_dc)

#     prob_oc = prob_overcharge(n_sixes, pool_size)

#     probs = [None, ] * (new_max_dc+1)
#     for dc in range(min_dc, new_max_dc+1):
#         probs[dc] = prob_oc
#     return probs


# @functools.lru_cache
# def get_counts(pool_size):
#     """
#     Returns a tuple where the first element is the total number of results for
#     the pool size and the second element is an array of size 6*pool_size, where
#     entry n indicates the count of getting that exact sum when rolling
#     "pool_size" d6's

#     """
#     assert pool_size >= 1

#     if pool_size == 1:
#         return 6, (1, 1, 1, 1, 1, 1)

#     _, old_counts = get_counts(pool_size-1)
#     counts = pool_size * 6 * [0, ]

#     # for each dice results 1-6 ...
#     for d in range(1, 7):
#         for old_sum, old_count in enumerate(old_counts):
#             counts[old_sum + d] += old_count
#     return sum(counts), counts



# @functools.lru_cache
# def get_counts_with_sixes(pool_size):
#     """
#     Returns a tuple where the first element is the total number of results for
#     the pool size and the second element is an array of size 6*pool_size, where
#     entry n indicates the count of getting that exact sum when rolling
#     "pool_size" d6's

#     """
#     assert pool_size >= 1

#     if pool_size == 1:
#         return (6,  # number of results
#                 (1, 1, 1, 1, 1, 1), # count for results 1-6
#                 (0, 0, 0, 0, 0, 1)) # count of number of 6s for results 1-6

#     _, old_counts, old_sixes_counts = get_counts_with_sixes(pool_size-1)
#     counts = pool_size * 6 * [0, ]
#     sixes_counts = pool_size * 6 * [0, ]

#     # for each dice results 1-6 ...
#     for d in range(1, 7):
#         for old_sum in range(counts):
#             old_count = old_counts[old_sum]
#             old_sixes_count = old_sixes_counts[old_sum]
        
#             # for old_sum, old_count in enumerate(old_counts):
#             counts[old_sum + d] += old_count
#             sixes_counts[old_sum + d] += old_sixes_counts
#             if d == 6:
#                 sixes_counts[old_sum + d] += 1
                
#     return sum(counts), counts, sixes_counts


# @functools.lru_cache
# def get_probs(pool_size):
#     n_counts, counts = get_counts(pool_size)
#     return [c / float(n_counts) if c is not 0 else None for c in counts]


# def prob_sum_gte_dc(pool_size, dc):
#     """
#     Returns the probability that the sum when rolling "pool_size" d6s is >= the given dc.

#     """
#     assert dc >= 1
#     probs = get_probs(pool_size)
#     return sum(probs[dc-1:])


# # for n, s in ((0,1), (1,1),
# #              (0,2), (1,2), (2,2),
# #              (0,3), (1,3), (2,3), (3,3)):
# #     print(f"pool size: {s}, number of sixes: {n}, prob: {prob_sixes_in_pool(n, s)}")
    
# # p = get_probs(3)
# # print(p)
# # print(sum(p))
# print(prob_sum_gte_dc(2, 12))



# def get_overcharge_probs_given_success_probs(overcharge_probs, dc_probs):
#     max_dc = max(len(overcharge_probs), len(dc_probs))

#     conditional_probs = [None, ] * max_dc
#     for dc in range(max_dc+1):
#         if overcharge_probs[dc] is not None and dc_probs is not None:
#             conditional_probs[dc] = overcharge_probs / dc_probs[]
        
    

"""
dc ... 


n dice.. 
probs 

probs for number of sixes


number of dice?

DC on the x axis.
Prob success on y1
Prob OC2 on y2
Prob OC3 on y2
Prob OC4 on y2
Prob OC5 on y2



chance of success? on x
chance of oc on y?

each point is DC/n dice?


we don't want spells that have a 30% success rate.. but when you succeed you have a 80% chance of OC.
(e.g. we care about OC%|success)? 


# def get_oc_probs(n_sixes, pool_size):

# We care about chance to succeed with/without OC
# REQUIRE THAT OC always must succeed .. eg "OC d6" * 6 > DC

"""



# 


MAX_POOL_SIZE = 12
MAX_DC = MAX_POOL_SIZE * 6


class Combos:
    """
    For each number of dice we want a 2d array with index (dc, n6s) --> count

    """
    def __init__(self):
        self.counts = {}
        for dc in range(1, MAX_DC+1):
            self.counts[dc] = [0, ] * (MAX_POOL_SIZE+1)
                
    def __str__(self):
        str_rep = " *** Combos ***\n"
        str_rep += "\t\t *N Sixes*\n"
        str_rep += " *Sum*   0   1   2   3   4   5   6\n"
        for dc in range(1, MAX_DC+1):
            counts_for_dc = self.counts[dc]            
            counts_str = " ".join([f"{c:3}" for c in counts_for_dc])
            str_rep += f" {dc:2}    {counts_str}\n"
        str_rep += "\n"
        return str_rep    

    def __iter__(self):
        for dc in range(1, MAX_DC+1):
            yield dc, self.counts[dc]

    def get_total(self):
        total = 0
        for dc in range(1, MAX_DC+1):
            total += sum(self.counts[dc])
        return total
        

class Probs:
    
    def __init__(self):
        self.probs = {}
        for dc in range(1, MAX_DC+1):
            self.probs[dc] = [0.0, ] * (MAX_POOL_SIZE+1)
                  
    def __str__(self):
        str_rep = " *** Probs ***\n"
        str_rep += "\t\t *N Sixes*\n"
        str_rep += " *Sum*   0   1   2   3   4   5   6\n"
        for dc in range(1, MAX_DC+1):
            probs_for_dc = self.probs[dc]
            probs_str = " ".join([f"{p:3}" for p in probs_for_dc])
            str_rep += f" {dc:2}    {probs_str}\n"
        str_rep += "\n"
        return str_rep    
  
    def __iter__(self):
        for dc in range(1, MAX_DC+1):
            yield dc, self.probs[dc]

    def get_total(self):
        total = 0.0
        for dc in range(1, MAX_DC+1):
            total += sum(self.probs[dc])
        return total
        


@functools.lru_cache
def get_combos(n_dice):
    """

    """
    assert n_dice >= 1

    combos = Combos()
    if n_dice == 1:
        combos.counts[1][0] = 1
        combos.counts[2][0] = 1
        combos.counts[3][0] = 1
        combos.counts[4][0] = 1
        combos.counts[5][0] = 1
        combos.counts[6][1] = 1
        return combos

    old_combos = get_combos(n_dice=n_dice-1)
    #print(old_combos)
    #print()
    
    # for each dice results 1-6 ...
    for dc, counts in old_combos:
        for n_sixes, count in enumerate(counts):

            # exit early.. 
            if count == 0:
                continue
            
            for d in range(1, 7): # n_dice):
                print(f"dice {d}")
                new_dc = dc + d

                if new_dc > MAX_DC:
                    continue

                if d == 6:
                    combos.counts[new_dc][n_sixes+1] += count
                else:
                    combos.counts[new_dc][n_sixes] += count
    return combos


@functools.lru_cache
def get_probs(combos):
    probs = Probs()
    total = float(combos.get_total())
    for dc in range(1, MAX_DC+1):
        for n_sixes in range(MAX_POOL_SIZE+1):
            probs.probs[dc][n_sixes] = combos.counts[dc][n_sixes] / total
    return probs
    

# def get_probs():

#     array.array()

#probs = get_combos(1)
combos = get_combos(3)
print(combos)
print(combos.get_total())

probs = get_probs(combos)
print(probs)
print(probs.get_total())

#for x in probs:
#   print(x)


# def draw_oc_graph():    
#     """
#       Graph comparison 
#     """
#     hist = pygal.Line(
#         human_readable=True,
#         title="Probability of Getting n 6s",
#         x_title="Number of 6s rolled",
#         y_title="Probability",
#         legend_at_bottom=False,
#         legend_at_bottom_columns=5,
#         x_label_rotation=15,
#     )


#     for pool_size in (3, ):
#         #for dc in range(2, 20):

#         # probs = get_probs(pool_size)
#         # hist.add(f'{pool_size}d6', probs)

        
#         # probs = get_overcharge_probs(n_sixes=1, pool_size=pool_size)
#         # print(probs)
#         # hist.add(f'OC 1, {pool_size}d6', probs)

#     # min_prob = 0.05 # percent
#     # hist.add('2d6', prob_of_n6s(2, min_prob))
#     # hist.add('3d6', prob_of_n6s(3, min_prob))
#     # hist.add('4d6', prob_of_n6s(4, min_prob))
#     # hist.add('5d6', prob_of_n6s(5, min_prob))
#     # hist.add('6d6', prob_of_n6s(6, min_prob))
#     # hist.add('7d6', prob_of_n6s(7, min_prob))
#     # hist.add('8d6', prob_of_n6s(8, min_prob))
#     # hist.add('9d6', prob_of_n6s(9, min_prob))
#     # hist.add('10d6', prob_of_n6s(10, min_prob))
#     # hist.add('11d6', prob_of_n6s(11, min_prob))
#     # hist.add('12d6     ', prob_of_n6s(12, min_prob))
#     hist.x_labels = map(str, range(1, MAX_DC+1))
#     #                     [0, 1, "2 Lvl1 OC!", "3 Lvl2 OC!", "4 Lvl3 OC!", 5, 6, 7])

#     fname = join(build_dir, 'd6_overcharge.png')
#     hist.render_to_png(fname)


#draw_oc_graph()
