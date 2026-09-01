

from os.path import abspath, join, dirname

from utils import (
    src_dir,
    abilities_dir,
    docs_dir,
    parse_xml
    )


# hammer_xml = join(abilities_dir, "hammer.xml")

# doc = parse_xml(hammer_xml)
# print(doc)


phb_xml = join(docs_dir, "phb.xml")

doc = parse_xml(phb_xml)
print(doc)


