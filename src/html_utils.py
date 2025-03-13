


def build_html_doc(template_fname, verbosity, archetype = None):
    """
    Archetype required only when building archetype docs.

    """
    # archetypes all use the same template.. but we don't want to 
    # put them in the same doc file.
    if archetype is not None:
        doc_fname = archetype.get_id()
    else:
        doc_fname = template_fname

    # base name .. no extension
    doc_base_fname, _ = splitext(basename(doc_fname))
    xml_fname = join(build_dir, "%s.xml" % doc_base_fname)
    html_fname = join(build_dir, "%s.html" % doc_base_fname)

    # parse an xml document
    print(f"--------------> PARSING {xml_fname}")
    doc = Doc(xml_fname)        
    if not doc.parse():
        print("Problem parsing the xml.")
        exit(0)

    print(f"--------------> VALIDATING {xml_fname}")
    if not doc.validate():
        print("Fatal: xml errors are fatal!")
        print("Run with the -s cmd line option to ignore xml errors.")
        exit(0)
        
    # build the html document by converting the xml into tex
    with codecs.open(html_fname, "w", "utf-8") as f:
        html_formatter = HtmlFormatter(f)
        errors = doc.format(html_formatter)
        if len(errors) > 0:
            print("Errors:")
            for error in errors:
                print("\t%s\n\n\n" % error)
                exit()
    return

