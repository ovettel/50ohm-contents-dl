#!/usr/bin/env python3

# 2026, DARC e. V., Matthias Jung (DL9MJ) and others.
import tempfile
import subprocess
import pathlib

def build_drawing(id, width=9.0):

    # Create build directory:
    with tempfile.TemporaryDirectory(prefix="build_", dir="./") as tmp:
        build_path = pathlib.Path(tmp)

        # Read the LaTeX drawing file:
        drawings_path = pathlib.Path("contents/drawings")
        drawing = drawings_path / f"{id}.tex"
        if not drawing.is_file():
            print(f"Error: drawing file '{drawing}' not found.")
            return False
        with drawing.open("r", encoding="utf-8") as file:
            latex = file.read()
    
        # Workaround, if the picture contains a document class it should be ignored:
        if ("\\begin{document}" in latex or "\\begin{table}" in latex): 
            print(f"Error: drawing file '{drawing}' contains a document environment.")
            return False

        # Write the include file:
        img_path = build_path / "img"
        img_path.mkdir(parents=True, exist_ok=True)
        with (img_path / f"{id}include.tex").open("w") as file:
            file.write(latex)

        # Write the auxilary LaTeX file:
        aux_file = build_path / f"{id}.tex"
        
        with aux_file.open("w", encoding="utf-8") as file:
            file.write(f"\\documentclass{{FiftyOhm}}\\DARCimageOnly{{{width}cm}}{{{id}include}}")

        # Symlink photos, so LaTeX can access these assets to render into graphics.
        photos_path = pathlib.Path("../contents/photos")

        foto_link = build_path / "foto"
        foto_link.symlink_to(photos_path)

        foto_link2 = build_path / "img/foto"
        foto_link2.symlink_to(photos_path)

        # Build the picture:
        subprocess.run(f"latexmk -lualatex {aux_file}",
                       shell=True, check=True, stdin=subprocess.DEVNULL)
        
        # Convert the PDF to SVG and store it in the drawings folder:
        subprocess.run(f"pdftocairo -svg {build_path}/{id}.pdf - > {drawings_path}/{id}.svg",
                       shell=True, check=True, stdin=subprocess.DEVNULL)

        return True

if __name__ == "__main__":

    # One may want to pass the drawing number and the size as arguments.
    
    print("Build SVG from LaTeX")
    print("Please type number of drawing:")
    
    id = int(input())
    
    print("Please type size of drawing (default 9):")
    
    if (width_str := input()) != "":
        width = float(width_str)
    else:
        width = 9.0
    
    print(f"Building picture {id}. This might take a while ... ") 
    build_drawing(id, width)
