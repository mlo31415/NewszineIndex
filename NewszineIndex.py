import tkinter
from tkinter import filedialog
import os
import Helpers
import operator

# Get the directory containing the lst files to be analyzed.
root = tkinter.Tk()
root.withdraw()
lstDirname = filedialog.askdirectory()
if len(lstDirname) == 0:
    exit()

# Get a list of all the filenames of the .lst files in that directory.
os.chdir(lstDirname)
lstList = os.listdir(".")
lstList = [f for f in lstList if os.path.splitext(f)[1].lower() == ".lst"]

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
internalNameDictionary={}
for name in lstList:
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
            internalNameDictionary[os.path.splitext(name)[0].lower()]=header.split(";")[0].strip()
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

        # First, if there isn't a ">" in the first item on the line, we don't actually have the fanzine, so we drop it.
        if fanzineLine[0].find(">") == -1:
            continue

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

        if not parseFailure:
            fanzineList.append((year, month, l, name))
        else:
            print("FanzineDef:"+l)

# Ok, hopefully we have a list of all the fanzines.  Sort it and print it out
fanzineList=sorted(fanzineList, key=operator.itemgetter(0, 1))
year=0
month=0
yearCounts={}
for f in fanzineList:
    if f[0] in yearCounts:
        yearCounts[f[0]]=yearCounts[f[0]]+1
    else:
        yearCounts[f[0]]=1
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

# Now print out the yearCounts data. We turn the dict into a list of tuples and sort it and print it
yearCountsList=[]
for y in yearCounts:
    yearCountsList.append((y, yearCounts[y]))
yearCountsList=sorted(yearCountsList)
for t in yearCountsList:
    print(str(t[0])+": "+str(t[1]))

# Now create the html
# The directories containing the scans are expected to be in a sibling directory called "fanzines"
fanzinesDirname=os.path.normpath(os.path.join(lstDirname, "../fanzines"))

# Get a list of all the directories in fanzines
os.chdir(fanzinesDirname)
dirlist = os.listdir(".")
dirlist = [f for f in dirlist if os.path.isdir(f)]

# OK.  Now we need to determine the directory name for each LST file.
# This is non-trivial.
# For each LST file:
#   Each LST file contains a header line with semicolon-delimited information in it.  The first field is the internal name of the fanzine.
#   We first check to see if there is a directory present matching the internal name (with all blanks replaced by '_')
#   If not, we check to see if there is a directory present matching the LST file's name.
#   If not, we check to see if there is an entry in the dirnameExceptions dictionary.
dirnameExceptions={
    "blooming" : "Bloomington_News",
    "bullshe1" : "Bullsheet",
    "bullshe2" : "Bullsheet",
    "fanewscard" : "FanewsCard",
    "fantasy_news_newseries" : "Fantasy_News_NewSeries",
    "luna" : "Luna",
    "midwest" : "MidWest_Fan_News",
    "neosfs" : "NEOSFS",
    "qx" : "QX",
    "sfnews" : "SF_News",
    "sfnewsco" : "SF_Newscope",
    "sfnl-rw" : "SFNL-RichardWilson"}

# Convert the values of the internalNameDictionary to directory form (spaces -> '_')
for d in internalNameDictionary:
    internalNameDictionary[d]=internalNameDictionary[d].replace(" ", "_")

lstNameToDirNameMap={}
for file in lstList:
    file=os.path.splitext(file)[0]
    dirname=None
    if internalNameDictionary[file.lower()] in dirlist:
        dirname=internalNameDictionary[file.lower()]
    else:
        if file in dirlist:
            dirname=file
        else:
            if file.lower() in dirnameExceptions:
                dirname=dirnameExceptions[file.lower()]

    if dirname == None:
        print("   ***'" + file + "' seems to have no matching directory")
    lstNameToDirNameMap[file]=dirname

for d in lstNameToDirNameMap:
    print(d+" --> "+lstNameToDirNameMap[d]+"    "+str(len(os.listdir(lstNameToDirNameMap[d]))))


months={1 : "January",
        2 : "February",
        3 : "March",
        4 : "April",
        5 : "May",
        6 : "June",
        7 : "July",
        8 : "August",
        9 : "September",
        10 : "October",
        11 : "November",
        12 : "December"}

f=open("../newszinestable.txt", "w")
print('<table border="1">', file=f)

fanzineList=sorted(fanzineList, key=operator.itemgetter(0, 1))
year=0
month=0
for fmz in fanzineList:
    print('    <tr>', file=f)
    line=""
    if fmz[0] != year:
        year=fmz[0]
        print('        <td>' + str(year) + '</td>', file=f)
    else:
        print('        <td>&nbsp;</td>', file=f)

    if fmz[1] != month:
        month=fmz[1]
        print('        <td>' + months[month] + '</td>', file=f)
    else:
        print('        <td>&nbsp;</td>', file=f)

    print('               <td>'+lstNameToDirNameMap[os.path.splitext(fmz[3])[0]]+'</<td>', file=f)
    print('               <td>'+str(fmz[2])+'</<td>', file=f)
    print('    </tr>', file=f)

print('</table>', file=f)
f.close()


pass