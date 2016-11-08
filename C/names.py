
def AllNames():
    names = []
    names.append('SUPERMEAN')
    names.append('PREVNUM')
    names.append('PREVSUM')
    for i in xrange(14):
        names.append('PREVMONTH_' + str(i))
        names.append('PREVMONTHNUM_' + str(i))
        names.append('PREVMONTH2_' + str(i))
        names.append('INCOME_' + str(i))
        names.append('SPENT_' + str(i))
        names.append('MCCSPENT_' + str(i))
    for i in xrange(13):
        names.append('USER' + str(i))
    for i in xrange(90):
        names.append('PREVDAYS_' + str(i))
    
    for i in xrange(184):
        names.append('MCC_' + str(i))

    res = {}                                                                                                                                               
    for i in xrange(len(names)):                                                                                                                                         
        res[names[i]] = i                                                                                                                           
    return res, names
