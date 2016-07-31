import tkinter
from tkinter import filedialog
import os
import re

# Get the directory containing the lst files to be analyzed.
root = tkinter.Tk()
root.withdraw()
dirname = filedialog.askdirectory()

# Get a list of all the filenames of the .lst files in that directory.
os.chdir(dirname)
filelist = os.listdir(".")
filelist = [f for f in filelist if os.path.splitext(f)[1].lower() == ".lst"]

# We walk the list of .lst files, analyzing each one.
# The structure of a .lst file is:
# A single line containing the following, semi-colon delimited: Title, Editors, Date range, Zine type
# One or more repetitions of the following
# A blank line
# One or more lines of descriptive material bounded by <P>, </P>
# A blank line
# A column definition line comprised of a semicolon-delimited list of column headings.  It always begins with "Issue"
# A blank line
# One line for each issue, each comprised of a semicolon-delimited list of data for that fanzine which matches the headings
for name in filelist:
    f = open(name)
    print("\nOpening "+name)
    header = ""
    description = []        # There may be more than one description block, so this is a list of strings
    partialDescription=""   # When we have processed some but not all of the lines in a description, this holds the material found so far
    columnDef = ""
    while True:
        l = f.readline()
        if len(l) == 0:  # Check for EOF
            break
        if len(l) == 1:  # Ignore blank lines
            continue
        # OK, we have a line with content
        l=l.strip() # Remove leading and trailing whitespace, including the trailing \n
        if len(header) == 0:    # If no header has been processed, then the first non-blank line is the header
            header = l
            print("Header: "+l)
            continue

        # Might this be a Description?  A Description is bounded by <P> </P> blocks
        # First look at the case where we're already processing a multi-line description
        if len(partialDescription) > 0:
            partialDescription = partialDescription + " " + l
            if len(l) > 4 and l[-4:].lower() == "</p>":        # Does this line close the description?
                description.append(partialDescription)
                print("Description: " + partialDescription)
                partialDescription=""
            continue

        # Might this be a the start of a Description?  A Description is bounded by <P> </P> blocks
        if (len(l) > 3 and l.lower()[:3] == "<p>"):
            if len(l) > 4 and l[-4:].lower() == "</p>":        # Does this line also close the description?  (I.e., it's a single-line description.)
                description.append(l)   # This is a single-line description
                print("Description: " + l)
            else:
                partialDescription=l    # It has <P> but no </P>, so it's the start of a multi-line description.
            continue

        if len(columnDef) == 0:
            columnDef = l
            print("ColumDef: "+l)
            continue
        print("FanzineDef:"+l)
