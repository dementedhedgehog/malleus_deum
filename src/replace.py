#!/usr/bin/env python3
"""

   Batch replace text in files

"""
from utils import abilities_dir
from os import listdir
from os.path import isfile, join



for short_fname in listdir(abilities_dir):
    fname = join(abilities_dir, short_fname)

    if not isfile(fname):
        continue

    if not fname.endswith(".xml"):
        continue

    with open(fname, 'r') as f:
        content = f.read()

    # content = content.replace("""</check>

    #    <dc>""", """</check>
    #    <dc>""")

    # COMMENTED OUT FOR SAFETY
    #content = content.replace("""abilitykeywords>""", """keywords>""")
    #content = content.replace("""<combat/>""", """<martial/>""")
    #content = content.replace("""Std+Rank""", """2d12+Rank""")
    #content = content.replace("""abilityactiontype>""", """actiontype>""")
    #content = content.replace("""      <bane></bane>\n""", """      <bane></bane>\n      <bane-success></bane-success>\n      <bane-fail></bane-fail>\n""")
    with open(fname, 'w') as f:
        f.write(content)

    print(f"Wrote {fname}")
