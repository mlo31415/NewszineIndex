def InterpretYear(yearstring):
    try:
        year=int(yearstring)
    except:
        print("   ***Year conversion failed: '" + yearstring+"'")
        year=None
    return year

def InterpretMonth(monthstring):
    monthConversionTable={"jan" : 1, "january" : 1, "1" : 1,
                          "feb" : 2, "february" : 2, "2" : 2,
                          "mar" : 3, "march" : 3, "3" : 3,
                          "apr" : 4, "april" : 4, "4" : 4,
                          "may" : 5, "5" : 5,
                          "jun" : 6, "june" : 6, "6" : 6,
                          "jul" : 7, "july" : 7, "7" : 7,
                          "aug" : 8, "august" : 8, "8" : 8,
                          "sep" : 9, "sept" : 9, "september" : 9, "9" : 9,
                          "oct" : 10, "october" : 10, "10" : 10,
                          "nov" : 11, "november" : 11, "11" : 11,
                          "dec" : 12, "december" : 12, "12" : 12,
                          "1q" : 1,
                          "4q" : 4,
                          "7q" : 7,
                          "10q" : 10,
                          "spring" : 4,
                          "summer" : 7,
                          "fall" : 10, "autumn" : 10,
                          "winter" : 1,
                          "january-february" : 2,
                          "march-april" : 4,
                          "april-may" : 5,
                          "apr-may" : 5,
                          "may-june" : 6,
                          "july-august" : 8,
                          "september-october" : 10,
                          "sep-oct" : 10,
                          "october-november" : 11,
                          "oct-nov" : 11,
                          "september-december" : 12,
                          "november-december" : 12,
                          "december-january" : 12,
                          "dec-jan" : 12}
    try:
        month=monthConversionTable[monthstring.replace(" ", "").lower()]
    except:
        print("   ***Month conversion failed: "+monthstring)
        month=None
    return month

def CannonicizeColumnHeaders(header):
    translationTable={"title" : "title",
                      "issue" : "title",
                      "month" : "month",
                      "mo." : "month",
                      "day" : "day",
                      "year" : "year",
                      "repro" : "repro",
                      "editor" : "editor",
                      "editors" : "editor",
                      "notes" : "notes",
                      "pages" : "pages",
                      "size" : "size",
                      "type" : "type",
                      "#" : "#",
                      "no" : "#",
                      "number" : "#",
                      "vol" : "vol",
                      "volume" : "vol",
                      "num" : "num",
                      "headline" : "headline",
                      "publisher" : "publisher"}
    try:
        return translationTable[header.replace(" ", "").lower()]
    except:
        print("   ***Column Header conversion failed: '" + header + "'")
        return None

def RecognizeDescritpionBlockStart(line):
    starters={"<p>", "<h2>", "<h3>"}
    line=line.lower()
    for starter in starters:
        if len(line) > len(starter) and line[:len(starter)] == starter:
            return True
    return False

def RecognizeDescriptionBlockEnd(line):
    enders={"</p>", "</h2>", "</h3>"}
    line=line.lower()
    for ender in enders:
        if len(line) > len(ender) and line[-len(ender):] == ender:
            return True
    return False