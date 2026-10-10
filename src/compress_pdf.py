"""

   PDF Compression functions.

   Running on the current phb.pdf
   gs_optimize_pdf : 27Mb --> 7Mb 73% reduction in size.
   pymupdf_optimize_pdf : 27Mb --> 18Mb 33% reduction in size   

"""
import pymupdf
import subprocess
import os

def pymupdf_optimize_pdf(input_path, output_path, aggressive=True):
    """
    Compression nowhere near as good as ghostscript (see next fn).
    But I imagine installation is less hassle on non-linux platforms.
    
    """
    # Open the document
    doc = pymupdf.open(input_path)

    # Remove hidden baggage (metadata, thumbnails, attached files)
    doc.scrub(
        metadata=True,
        attached_files=True,
        embedded_files=True,
        thumbnails=True
    )
    
    # Minimize font file sizes by removing unused characters
    doc.subset_fonts()    
    
    # Downsample all images in the document
    # This targets images above 150 DPI and shrinks them to 96 DPI at 75%
    # JPEG quality
    if aggressive:
        doc.rewrite_images(
            dpi_threshold=150,
            dpi_target=96,
            quality=75,
            lossy=True
        )
    
    # Save with advanced optimization arguments
    doc.save(
        output_path,
        # Drastically eliminates duplicate & unreferenced objects
        garbage=4,          
        # Compresses uncompressed streams (images/fonts)
        deflate=True,       
        # Packs object definitions into streams (cuts ~25% text size)
        use_objstms=True,   
    )
    doc.close()
    print(f"Optimized PDF saved to: {output_path}")


def gs_optimize_pdf(input_path, output_path, quality="ebook"):
    """
    Quality presets:
    /screen  = low-res (72 dpi), maximum compression
    /ebook   = mid-res (150 dpi), ideal for digital reading
    /printer = high-res (300 dpi), ideal for printing
    """
    
    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]
    
    try:
        subprocess.run(gs_command, check=True)
        print(f"Compressed file generated successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Ghostscript: {e}")
    return


if __name__ == "__main__":
    gs_optimize_pdf("./build/phb.pdf", "phb_opt.pdf")
    #pymupdf_optimize_pdf("./build/phb.pdf", "phb_opt2.pdf")




