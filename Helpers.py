def InterpretYear(yearstring):
    try:
        year=int(yearstring)
    except:
        print("***Year conversion failed: '" + yearstring+"'")
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
                          "spring" : 4,
                          "summer" : 7,
                          "fall" : 10, "autumn" : 10,
                          "winter" : 1,
                          "march-april" : 4,
                          "may-june" : 6,
                          "july-august" : 8,
                          "september-october" : 11,
                          "september-december" : 12,
                          "december-january" : 12}
    try:
        month=monthConversionTable[monthstring.lower()];
    except:
        print("***Month conversion failed: "+monthstring)
        month=None
    return month