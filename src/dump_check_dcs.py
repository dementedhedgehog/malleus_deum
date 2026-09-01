"""

  Prints out a table of DCs to probabilities
  of various types of results, e.g. grim-fail,
  any-success, righteous success.
  (Saves human error).

"""

def get_probs(dc):
    grim_fail = min(max((dc - 8 - 1), 1), 19) * 5
    any_success = min(max((20 - dc + 1), 1), 19) * 5
    righteous_success = min(max((20 - 8 -dc + 1), 1), 19) * 5
    return (f"<smaller>{grim_fail}/</smaller>"
            f"<bold>{any_success}</bold>"
            f"<smaller>/{righteous_success}<percent/></smaller>")
    

if __name__ == "__main__":
    for dc in (5, 7, 9, 11, 13, 15, 17, 19, 21, 23): 
        print("\t<tablerow>")
        print(f'\t\t<td align="r"><bold>{dc}</bold></td>')
        for rank in (-6, -3, 0, 1, 2, 3, 4, 5, 6):
            print(f'\t\t<td align="c">{get_probs(dc-rank)}</td>')
        print("\t</tablerow>")
        print()


