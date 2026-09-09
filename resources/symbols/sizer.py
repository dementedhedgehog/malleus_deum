from pathlib import Path
from PIL import Image

def print_png_heights(directory_path):
    """
    Scans a directory for all .png files and prints their height.
    """
    # Convert string path to a Path object
    dir_path = Path(directory_path)
    
    # Check if the provided directory actually exists
    if not dir_path.is_dir():
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    # Use rglob("*.png") for recursive scanning, or glob("*.png") for just the top folder
    png_files = list(dir_path.glob("*.png"))

    if not png_files:
        print("No .png files found in the specified directory.")
        return

    print(f"Scanning directory: {dir_path.resolve()}\n")
    print(f"{'File Name':<40} | {'Height (px)':<12}")
    print("-" * 55)

    for file_path in png_files:
        try:
            # Open the image file (lazy-loads metadata only)
            with Image.open(file_path) as img:
                # Use img.height or img.size[1] to get the height
                height = img.height
                print(f"{file_path.name:<40} | {height:<12}")
        except Exception as e:
            print(f"Could not read {file_path.name}: {e}")

if __name__ == "__main__":
    # Replace with your actual directory path (e.g., "C:/Images" or "relative/path")
    target_directory = "." 
    
    print_png_heights(target_directory)
