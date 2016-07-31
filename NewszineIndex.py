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
filelist = [f for f in filelist if os.path.splitext(f)[1] == ".LST"]

# We walk the list of .lst files, analyzing each one.
# The structure of a .lst file is:
# A single line containing the following, semi-colon delimited: Title, Editors, Date range, Zine type
# One or more repetitions of the following
# A blank line
# One or more lines of descriptive material bounded by <P>, </P>
# A blank line
# A column definition line comprised of a semicolon-delimited list of column headings
# A blank line
# One line for each issue, each comprised of a semicolon-delimited list of data for that fanzine which matches the headings
for name in filelist:
    f = open(name)
    print("\nOpening "+name)
    header = ""
    description = ""
    columnDef = ""
    while True:
        l = f.readline()
        if len(l) == 0:  # Check for EOF
            break
        if len(l) == 1:  # Ignore blank lines
            continue
        # OK, we have a line with content
        l=l[:-1]    # Remove the trailing \n
        if len(header) == 0:
            header = l
            print("Header: "+l)
            continue
        if not len(description) == 0:
            description = l
            print("Description: "+l)
            continue
        if not len(columnDef) == 0:
            columnDef = l
            print("ColumDef: "+l)
            continue
        print("FanzineDef:"+l)
