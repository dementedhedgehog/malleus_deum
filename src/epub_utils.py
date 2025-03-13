

# def build_epub(xml_fname,
#                verbosity,
#                doc,
#                db,                  
#                archetype=None,
#                patron=None):
#     # base name .. no extension
#     doc_base_fname, _ = splitext(basename(xml_fname))
#     epub_fname = join(build_dir, "%s.epub" % doc_base_fname)

#     print((f"\tBuilding {epub_fname}"))

#     # check we have a book_node to format
#     if not doc.has_book_node():
#         if verbosity >= 1:
#             print("No book node to format in document: %s IGNORING!" % doc_fname)
#         return

#     # build the epub document 
#     #with codecs.open(tex_fname, "w", "utf-8") as f:
#     epub_formatter = EPubFormatter(epub_fname=epub_fname, db=db)

#     errors = doc.format(epub_formatter)
#     if len(errors) > 0:
#         print("Errors:")
#         for error in errors:
#             print("\t%s\n\n\n" % error)                
#             exit()

#     # Copy the pdf from the build dir to the pdfs dir
#     copy(epub_fname, pdfs_dir)
    
#     print((f"\tFinished building {epub_fname}"))
#     return True
