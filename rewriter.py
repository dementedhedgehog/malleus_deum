import sys
import re

fname = sys.argv[1]

print(fname)

f = open(fname)
data = f.read()


tokens = re.split(r'(<abilityrankid>.*?</abilityrankid>)', data)

new_tokens = []
skip_l = len("<abilityrankid>")
skip_r = len("</abilityrankid>")
for token in tokens:
    if token.startswith("<abilityrankid>"):

        t = token[skip_l:-skip_r]
        print(t)

        ref_tokens = t.rsplit("_", 1)

        assert len(ref_tokens) >= 1
        ab_id = ref_tokens[0]
        ab_rank = ref_tokens[1]

        print(ab_id)
        print(ab_rank)
        
        token = f'<abilityref id="{ab_id}" rank="{ab_rank}"/>'

    new_tokens.append(token)

    
#print(new_tokens)

f = open(fname, "w")
for token in new_tokens:
    f.write(token)
f.close()
