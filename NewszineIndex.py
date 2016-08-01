
import tkinter
from tkinter import filedialog
import os
import Helpers
import operator

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
# One or more lines of descriptive material bounded by <P>-</P> or <H3>-</H3>
# A blank line
# A column definition line comprised of a semicolon-delimited list of column headings.  It always begins with "Issue"
# A blank line
# One line for each issue, each comprised of a semicolon-delimited list of data for that fanzine which matches the headings
fanzineList=[]
for name in filelist:
    f = open(name)
    print("\nOpening "+name)
    header = ""
    description = []        # There may be more than one description block, so this is a list of strings
    partialDescription=""   # When we have processed some but not all of the lines in a description, this holds the material found so far
    columnDefs = []         # An array of columdef strings
    while True:
        parseFailure=False
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

        # Might this be a Description?  A Description is bounded by <P>-</P> or <H3>-</H3>blocks
        # First look at the case where we're already processing a multi-line description
        if len(partialDescription) > 0:
            partialDescription = partialDescription + " " + l
            if Helpers.RecognizeDescriptionBlockEnd(l):        # Does this line close the multi-line description?
                description.append(partialDescription)
                print("Description: " + partialDescription)
                partialDescription=""
            continue

        # Might this be a the start of a Description?  A Description is bounded by <P>-</P> or <H3>-</H3> blocks
        if Helpers.RecognizeDescritpionBlockStart(l):
            if Helpers.RecognizeDescriptionBlockEnd(l):        # Does this line also close the description?  (I.e., it's a single-line description.)
                description.append(l)   # This is a single-line description
                print("Description: " + l)
            else:
                partialDescription=l    # It has <P> or <H3> but no </P> or </H3>, so it's the start of a multi-line description.
            continue

        # Is this the columdef line?
        if len(columnDefs) == 0 and len(l) > 5 and (l[:6].lower() == "issue;" or l[:6].lower() == "title;"):
            columnDefs = l.lower().split(";")               # Split the columndefs line on semicolon
            columnDefs=[c.strip() for c in columnDefs]      # Remove whitespace padding
            columnDefs=[Helpers.CannonicizeColumnHeaders(c) for c in columnDefs]    # Cannonicize headers
            try:
                yearCol = columnDefs.index("year")
            except ValueError:
                yearCol=None
            try:
                monthCol = columnDefs.index("month")
            except ValueError:
                monthCol=None
            try:
                dayCol = columnDefs.index("day")
            except ValueError:
                dayCol=None
            print("ColumnDef: "+l)
            print("ColumnDef: YearCol="+str(yearCol)+" MonthCol="+str(monthCol)+" DayCol="+str(dayCol))
            continue

        # OK, it must be a fanzine line
        # We need to analyze it based on the columdefs.
        # Like columndefs, it's a single line of columns separated by semicolons, but in this case we want to preserve case
        fanzineLine = l.split(";")
        fanzineLine=[f.strip() for f in fanzineLine]

        # Let's figure out the date
        if (yearCol != None):
            if yearCol < len(fanzineLine):
                year=Helpers.InterpretYear(fanzineLine[yearCol])
            else:
                print("   ***FanzineLine too short: yearCol="+str(yearCol)+" Fanzineline='"+l+"'")
                parseFailure=True
        if (monthCol != None):
            if monthCol < len(fanzineLine):
                month=Helpers.InterpretMonth(fanzineLine[monthCol])
        else:
            print(   "***FanzineLine too short: yearCol=" + str(monthCol) + " Fanzineline='" + l + "'")
            parseFailure = True

        if year == None:
            year=0
            parseFailure = True
        if month == None:
            month=0
            parseFailure = True
        fanzineList.append((year, month, l))

        if parseFailure:
            print("FanzineDef:"+l)

# Ok, hopefully we have a list of all the fanzines.  Sort it and print it out
fanzineList=sorted(fanzineList, key=operator.itemgetter(0, 1))
year=0
month=0
for f in fanzineList:
    line=""
    if f[0] != year:
        year=f[0]
        line=str(year)
    else:
        line="    "
    if f[1] != month:
        month=f[1]
        line=line+"  "+str(month)
    else:
        line=line+"    "
    line=line+"  >>"+str(f[2])
    print(line)


