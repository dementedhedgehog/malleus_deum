




import re
import textwrap
import sys

text = """ If all else fails the character can make a check
for Divine Intervention.


      This action takes far too long to perform in the chaos of combat.
"""
_duplicate_ws_regex = re.compile(r'(?<=\S)\s+')

# Collapse multiple spaces between words BUT preserve
# leading whitespace
#text = re.sub(r'(?<=\S)\s+', ' ', text)
text = _duplicate_ws_regex.sub(' ', text)

# 1. Collapse multiple spaces between words BUT preserve leading whitespace
# This matches spaces that have characters before them
#text = re.sub(r'(?<=\S)\s+', ' ', text)

# # 2. Wrap the text while preserving spaces
#lines = textwrap.wrap(text, width=30, drop_whitespace=False, replace_whitespace=False)
lines = textwrap.wrap(text, width=30) # , drop_whitespace=False)

# # 3. Add newlines back (textwrap.wrap removes them, so writelines will bunch them into one line)
lines = [line + '\n' for line in lines]
if len(lines) > 0:
    print(lines[-1])
    lines[-1] = lines[-1].rstrip('\n')


print(lines)

#text = " ".join(text.split())
#lines = textwrap.wrap(text, width=30, drop_whitespace=False)
#lines = textwrap.wrap(text, width=30, drop_whitespace=False)


#buffer.writelines(lines_with_newlines)

print("[")
sys.stdout.writelines(lines)
print("]")
