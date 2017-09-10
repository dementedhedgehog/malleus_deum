

def filter_xelatex_output(xelatex_output, verbose):
    """Filter out some bs errors."""
    lines = xelatex_output.split("\n")

    line_no = 0
    while line_no < len(lines):
        line = lines[line_no]
        
        if line.startswith("Underfull"):
            # skip this error
            line_no += 2
        elif line.startswith("Overfull"):
            # skip this error
            line_no += 2
        else:
            print line
        
        line_no += 1
    return
