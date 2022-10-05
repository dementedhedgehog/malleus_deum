#!/usr/bin/env python3
"""

  Convert pdf to png.


"""
import sys
from os.path import splitext
from pdf2image import convert_from_path, convert_from_bytes


def usage(msg, err=None):
    
    print(
        f"Convert pdf to pngs."
        f"Usage:"
        f"  {sys.argv[0]} foo.pdf"
    )
    if err is not None:
        print(err)
    sys.exit(2)
    


def main():
    if len(sys.argv) == 0:
        usage()

    fnames = sys.argv[1:]
    for fname in fnames:        

        print(f"Converting {fname}")
        basename, _ = splitext(fname)

        images = convert_from_path(fname)
        for i, image in enumerate(images):
            outfile = f"{basename}_{i}.png"
            print(f"\tSaving {outfile}")
            image.save(outfile)
        


if __name__ == "__main__":
    main()
