

from config import use_imperial



def normalize_ws(text): 
    """
    Latex is white space sensitive .. so strip any whitespace from the raw xml
    (as xml is whitespace agnostic) and replace with a single space.
    
    Leaves whitespace at front and back of string.

    """
    if text is None:
        return None

    if len(text) == 0:
        return ""

    leading_ws = " " if text[0].isspace() else ""
    trailing_ws = " " if text[-1].isspace() else ""
    return leading_ws + " ".join(text.split()) + trailing_ws


def convert_to_roman_numerals(number):
    if number <= 0:
        return "0"
    elif number <= 10:
        return ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")[number - 1]
    else:
        return number


def convert_str_to_bool(str_bool):
    return str_bool.lower() != "false"


def convert_str_to_int(str_int):
    # later we might want some error handling!
    return int(str_int)


def parse_measurement_to_str(fname, measurement_node):
    
    # check at most once
    metric_found = False
    imperial_found = False

    # get the appropriate text representation.
    text_repr = ""
    for child in list(measurement_node):

        tag = child.tag
        if tag == "metric":
            if metric_found:
                raise NonUniqueTagError(tag, fname, child.sourceline)
            else:
                metric_found = True
                if not use_imperial:
                    text_repr += normalize_ws(child.text)

        elif tag == "imperial":
            if imperial_found:
                raise NonUniqueTagError(tag, self.fname, child.sourceline)
            else:
                imperial_found = True
                if use_imperial:
                    text_repr += normalize_ws(child.text)

        else:
            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                            (child.tag, fname, child.sourceline))

    return text_repr
    


