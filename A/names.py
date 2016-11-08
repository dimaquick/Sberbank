
def Add(names, prefix, i):
    names.append(prefix + 'PLUS_' + str(i))
#    names.append(prefix + 'PLUSPART_' + str(i))
    names.append(prefix + 'MINUS_' + str(i))
#    names.append(prefix + 'MINUSLOG_' + str(i))
#    names.append(prefix + 'ALL_' + str(i))
    names.append(prefix + 'NUM_' + str(i))
    names.append(prefix + 'PLUS_NORM_' + str(i))
    names.append(prefix + 'MINUS_NORM_' + str(i))
    names.append(prefix + 'NUM_NORM_' + str(i))

def AllNames(mcc, types, term, pairs):
    names = []
    names.append('EVENTS_NUM')
    names.append('EVENTS_POS_PART')
    names.append('EVENTS_MIN')
    names.append('EVENTS_MAX')
    names.append('EVENTS_INCOME')
    names.append('EVENTS_WASTE')

    names.append('BAYES')
    names.append('GBAYES')
    names.append('SPENDDAY')
    names.append('MALEMORE')
    names.append('INCOMEMORE')

    names.append('MALE_SPENT')
    names.append('MALE_SPENT_NUM')
    names.append('FEMALE_SPENT')
    names.append('FEMALE_SPENT_NUM')
    names.append('PMALE_SPENT')
    names.append('PMALE_SPENT_NUM')
    names.append('PFEMALE_SPENT')
    names.append('PFEMALE_SPENT_NUM')
    names.append('TPMALE_SPENT')
    names.append('TPMALE_SPENT_NUM')
    names.append('TPFEMALE_SPENT')
    names.append('TPFEMALE_SPENT_NUM')

    for i in xrange(term):  names.append('TERMINAL_' + str(i))
    for i in xrange(mcc):   Add(names, 'MCC', i)
    for i in xrange(types): Add(names, 'TYPE', i)
    for i in xrange(pairs): Add(names, 'PAIRS', i)
    for i in xrange(7):     Add(names, 'DAY', i)
    for i in xrange(3):     Add(names, 'DAYTYPE', i)
    for i in xrange(24):    Add(names, 'HOUR', i)
    for i in xrange(18):    Add(names, 'DDAY', i)
    for i in xrange(31):    Add(names, 'DAYOFMONTH', i)
    res = {}                                                                                                                                               
    for i in xrange(len(names)):                                                                                                                                         
        res[names[i]] = i                                                                                                                           
    return res, names
