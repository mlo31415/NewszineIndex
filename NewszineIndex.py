import tkinter
from tkinter import filedialog
import os
import Helpers
import operator
import re

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
    #print("\nOpening "+name)
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
            #print("Header: "+l)
            internalNameDictionary[os.path.splitext(name)[0].lower()]=header.split(";")[0].strip()
            continue

        # Might this be a Description?  A Description is bounded by <P>-</P> or <H3>-</H3>blocks
        # First look at the case where we're already processing a multi-line description
        if len(partialDescription) > 0:
            partialDescription = partialDescription + " " + l
            if Helpers.RecognizeDescriptionBlockEnd(l):        # Does this line close the multi-line description?
                description.append(partialDescription)
                #print("Description: " + partialDescription)
                partialDescription=""
            continue

        # Might this be a the start of a Description?  A Description is bounded by <P>-</P> or <H3>-</H3> blocks
        if Helpers.RecognizeDescritpionBlockStart(l):
            if Helpers.RecognizeDescriptionBlockEnd(l):        # Does this line also close the description?  (I.e., it's a single-line description.)
                description.append(l)   # This is a single-line description
                #print("Description: " + l)
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
            #print("ColumnDef: "+l)
            #print("ColumnDef: YearCol="+str(yearCol)+" MonthCol="+str(monthCol)+" DayCol="+str(dayCol))
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
                print("   ***FanzineLine too short in "+name+": yearCol="+str(yearCol)+" Fanzineline='"+l+"'")
                parseFailure=True
        if (monthCol != None):
            if monthCol < len(fanzineLine):
                month=Helpers.InterpretMonth(fanzineLine[monthCol])
        else:
            print(   "***FanzineLine too short in"+name+": yearCol=" + str(monthCol) + " Fanzineline='" + l + "'")
            parseFailure = True

        if year == None:
            year=0
            parseFailure = True
        if month == None:
            month=0
            parseFailure = True

        if parseFailure:
            print("File: "+name+"  FanzineDef: " + l+"\n")
            continue
        pattern=re.compile("^([a-zA-Z]*)(.*)>(.*)$")
        m=pattern.match(fanzineLine[0])
        fanzineList.append((year, month, l, name, m.groups()[0], m.groups()[1], m.groups()[2]))
        if m.groups()[0] == None or m.groups()[1] == None or m.groups()[1] == None:
            print("   ***FanzineLine does not have all three RegExs: " + fanzineLine)


# Ok, hopefully we have a list of all the fanzines.  Sort it and print it out
# fanzineList=sorted(fanzineList, key=operator.itemgetter(0, 1))
year=0
month=0
yearCounts={}
for f in fanzineList:
    if f[0] in yearCounts:
        yearCounts[f[0]]=yearCounts[f[0]]+1
    else:
        yearCounts[f[0]]=1
#     line=""
#     if f[0] != year:
#         year=f[0]
#         line=str(year)
#     else:
#         line="    "
#     if f[1] != month:
#         month=f[1]
#         line=line+"  "+str(month)
#     else:
#         line=line+"    "
#     line=line+"  >>"+str(f[2])
#     print(line)

# Now print out the yearCounts data. We turn the dict into a list of tuples and sort it and print it to histogram.txt
histogram=open("./histogram.txt", "w")
yearCountsList=[]
for y in yearCounts:
    yearCountsList.append((y, yearCounts[y]))
yearCountsList=sorted(yearCountsList)
for t in yearCountsList:
    print(str(t[0])+": "+str(t[1]), file=histogram)
histogram.close()

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
    # LST name : Directory name
    # the LST name is case-insensitive
    "blooming" : "Bloomington_News",
    "bullshe1" : "Bullsheet",
    "bullshe2" : "Bullsheet",
    "fanewscard" : "FanewsCard",
    "fantasy_news_newseries" : "Fantasy_News_NewSeries",
    "file" : "File770",
    "luna" : "Luna",
    "midwest" : "MidWest_Fan_News",
    "neosfs" : "NEOSFS",
    "qx" : "QX",
    "sfchron" : "SF_Chronicle",
    "sfnews" : "SF_News",
    "sfnewsco" : "SF_Newscope",
    "sfnl-rw" : "SFNL-RichardWilson",
    "sftimes-ger" : "SFTimes_German",
    "sfweekly" : "SFWeekly",
    "sweetness" : "Sweetness_Light"}

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

# for d in lstNameToDirNameMap:
#    print(d+" --> "+lstNameToDirNameMap[d]+"    "+str(len(os.listdir(lstNameToDirNameMap[d]))))


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

filePrefix={    # This deals with the arbitrary fanzine prefixes used on the website
    # The key for each pair is the directory name, the value is the file prefix used in the directories
    "Ansible" : "Ansible",
    "Australian_SF_News" : "auss",
    "Axe" : "Axe",
    "Barsoomian_Times" : "Barsoomian_Times",
    "Bay_Area_News" : "Bay_Area",
    "Bloomington_News" : "Bloomington_News",
    "Bullsheet" : "Bullsheet",
    "FANAC" : "FANAC",
    "FanewsCard" : "Fanews",
    "Fanew_Sletter" : "Fanew_Sletter",
    "Fantasy_Fiction_Field" : "FanFic_Field",
    "Fantasy_News" : "Fantasy_News",
    "Fantasy_News_NewSeries" : "fn",
    "Fantasy_Times" : "Fantasy_Times",
    "Fiawol" : "Fiawol",
    "File770" : "File770",
    "Focal_Point" : "Focal_Point",
    "Futurian_Observer" : "Futurian_Observer",
    "Karass" : "Karass",
    "Luna" : "Luna",
    "MidWest_Fan_News" : "MidWest_Fan_News",
    "Nebula" : "Nebula",
    "NEOSFS" : "NEOSFS",
    "Norstrilian_News" : "Norstrilian_News",
    "Organlegger" : "Organlegger",
    "Phan" : "Phan",
    "QX" : "QX",
    "Rally" : "Rally",
    "Ratatosk" : "Ratatosk",
    "Sanders" : "Sanders",
    "Science_Fantasy_Review" : "scif",
    "Science_Fiction_Newsletter" : "SFNews",
    "Science_Fiction_Times" : "Science_Fiction_Times",
    "Scream" : "Scream",
    "SF_News" : "SF_News",
    "SF_Newscope" : "sfn",
    "SF_Chronicle" : "sfc",
    "SFTimes_German" : "SFTimes_German",
    "SFinctor" : "SFinctor",
    "SFNL-RichardWilson" : "SFNL",
    "SFTimes_German" : "SFTimes_German",
    "SFWeekly" : "SFWeekly",
    "Shards_of_Babel" : "Shards_of_Babel",
    "Skyrack" : "Skyrack",
    "Spang_Blah" : "Spang_Blah",
    "SpinDizzy" : "SpinDizzy",
    "Starspinkle" : "Starspinkle",
    "STEFCARD" : "STEFCARD",
    "Swefanac" : "Swefanac",
    "Sweetness_Light" : "Sweetness_Light",
    "Sylmarillion" : "Sylmaril",
    "Thyme" : "Thyme",
    "Tympany" : "Tympany",
    "Winnie" : "Winnie"
}

f=open("../newszinestable.txt", "w")
print('<table border="1">', file=f)

fanzineList=sorted(fanzineList, key=operator.itemgetter(0, 1))
monthYear=""
for fmz in fanzineList:

    # This section deals with complicated and sometimes problematic data, so we do a bit of trail and error

    url=lstNameToDirNameMap[os.path.splitext(fmz[3])[0]]        # Directory name
    try:
        filePrefix[url]     # We need to make sure that this fanzine is in the filePrefix table.
    except:
        print("   *** '"+url+"' is missing from the filePrefix table")
        continue

    # The file on disk can be a pdf or an html file.  If it's a pdf, it will already have a pdf extension
    url = url + "/" + filePrefix[url] + fmz[5]
    if url[-4:].lower() !=  ".pdf": # If it's not already got a .pdf extension, add an .html extension
        url=url+".html"

    if not os.path.isfile(url):
        print("   *** File does not exist: "+url)
        continue

    # Start the row
    print('   <tr>', file=f)
    # Put the month & year in the first column of the table only if it changes.
    newMothYear=str(months[fmz[1]])+" "+str(fmz[0])
    if newMothYear != monthYear:
        monthYear=newMothYear
        print('      <td>' + newMothYear + '</td>', file=f)
    else:
        print('      <td>&nbsp;</td>', file=f)

    # The hyperlink goes in column 2
    print('               <td>' + '<a href="./'+url+'">'+fmz[6]+'</a>' + '<td>', file=f)

    # And end the row
    print('   </tr>', file=f)

print('</table>', file=f)
f.close()


pass