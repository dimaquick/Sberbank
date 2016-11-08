import math

def AllDays():
    data = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31]
    idx, num = 0, 0
    m = 7
    y = 2014
    res = []
    for i in xrange(490):
        res.append('%d-%02d-%02d' % (y, m + 1, num + 1))
        num += 1
        if num == data[idx]:
            num = 0
            idx += 1
            m += 1
            if m == 12:
                y += 1
                m = 0
    return res

def IsHoliday(day):
    if day == 152: return True #31 dec
    if day == 153: return True #1 yan
    if day == 197: return True #14 feb
    if day == 206: return True #23 feb
    if day == 219: return True #8 mar
    if day == 273: return True #1 may
    if day == 281: return True #9 may
    if day == 315: return True #12 jun
    return False

def IsWinter(month):
    return (month >= 3 and month <= 6) #from nov to feb                                                                                                                        

def DayOfMonth(day):
    idx = 0
    data = [31, 30, 31, 30, # 122
            31, 31, 28, 31, # 243
            30, 31, 30, 31, 31, 30, 31, 30, 31]
    while True:
        if day < data[idx]:
            return idx, day
        day -= data[idx]
        idx += 1
    return -1, -1

def DaysByMonth(month):
    a = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return a[month]

def MonthBorders(month):
    idx = 0
    data = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for i in xrange(len(data)):
        if i == month:
            return [idx, idx + data[i]]
        idx += data[i]
    return [-1, -1]

def Weekend(day):
    day = day % 7
    return day == 1 or day == 2

def ReadEvents(path):
    res, mccs = {}, {}
    for line in open(path, 'rt'):
        customer, ts, mcc, tp, amount, term = line.rstrip('\n').split(',')
        if mcc not in mccs: mccs[mcc] = len(mccs)
        day = int(ts.split(' ')[0])
        amount = float(amount)
        if amount >= 0: continue
        amount = -amount
        k = str(day) + '_' + mcc
        if k not in res: res[k] = 0.0
        res[k] += amount
    return res, mccs

def SuperMean(sums, mcc, day):
    day -= 35
    m, n = 0, 0
    while day >= 0:
        k = str(day) + '_' + mcc
        n += 1
        day -= 1
        if k in sums:
            m += math.log(500.0 + sums[k])
        else:
            m += math.log(500.0)
    return m / n if n > 0 else -1

def SuperWeekendMean(sums, mcc, day):
    sday = day
    day -= 35
    m, n = 0, 0
    while day >= 0:
        k = str(day) + '_' + mcc
        day -= 1
        if Weekend(day+1) and not Weekend(sday): continue
        if not Weekend(day+1) and Weekend(sday): continue    
        n += 1
        if k in sums:
            m += math.log(500.0 + sums[k])
        else:
            m += math.log(500.0)
    return m / n if n > 0 else -1

def AllPrevMonthMean(sums, mcc, day, weekendOnly):
    month, idx = DayOfMonth(day)
    begin, end = 10000, 0
    for i in xrange(100):
        month -= 1
        b, e = MonthBorders(month)
        if b < begin: begin = b
        if e > end: end = e
        if begin == 0: break
    m, n = 0, 0
    while begin < end:
        k = str(begin) + '_' + mcc
        begin += 1
        if weekendOnly:
            if Weekend(begin - 1) and not Weekend(day): continue
            if not Weekend(begin -1 ) and Weekend(day): continue
        if k in sums:
            m += math.log(500.0 + sums[k])
            n += 1
        else:
            m += math.log(500.0)
            n += 1
    return m / n if n > 0 else math.log(500.0)

def PrevMonthZero(sums, mcc, day, step):
    month, idx = DayOfMonth(day)
    begin, end = 10000, 0
    for i in xrange(step):
        month -= 1
        b, e = MonthBorders(month)
        if b < begin: begin = b
        if e > end: end = e
    m, n = 0, 0
    while begin < end:
        k = str(begin) + '_' + mcc
        if k not in sums:
            m += 1
        n += 1
        begin += 1
    return float(m) / n if n > 0 else -1

def Predict(sums, mcc, day, step):
    month, idx = DayOfMonth(day)
    lst = []
    for i in xrange(step):
        month -= 1
        b, e = MonthBorders(month)
        m, n = 0, 0
        while b < e:
            k = str(b) + '_' + mcc
            n += 1
            b += 1
            if k in sums:
                m += math.log(500.0 + sums[k])
            else:
                m += math.log(500.0)
        lst.append(m / n)
    res = []
    for i in xrange(len(lst)):
        if i == 0: continue
        df = lst[0] - lst[i]
        res.append(lst[0] + df / i)
    return res

def PrevMonthMean(sums, mcc, day, step):
    month, idx = DayOfMonth(day)
    begin, end = 10000, 0
    for i in xrange(step):
        month -= 1
        b, e = MonthBorders(month)
        if b < begin: begin = b
        if e > end: end = e
    m, n = 0, 0
    while begin < end:
        k = str(begin) + '_' + mcc
        if k in sums:
            m += math.log(500.0 + sums[k])
            n += 1
        else:
            m += math.log(500.0)
            n += 1
        begin += 1
    m = m / n if n > 0 else math.log(500.0)
    return m

def Friday(day): return day % 7 == 0

def PrevSamedayMonthMean(sums, mcc, day, step):
    month, idx = DayOfMonth(day)
    begin, end = 10000, 0
    for i in xrange(step):
        month -= 1
        b, e = MonthBorders(month)
        if b < begin: begin = b
        if e > end: end = e
    m, n = 0, 0
    while begin < end:
        k = str(begin) + '_' + mcc
        begin += 1
        if day % 7 != (begin - 1) % 7: continue
        if k in sums:
            m += math.log(500.0 + sums[k])
            n += 1
        else:
            m += math.log(500.0)
            n += 1
    return m / n if n > 0 else math.log(500.0)

def PrevWeekendMonthMean(sums, mcc, day, step):
    month, idx = DayOfMonth(day)
    begin, end = 10000, 0
    for i in xrange(step):
        month -= 1
        b, e = MonthBorders(month)
        if b < begin: begin = b
        if e > end: end = e
    m, n = 0, 0
    while begin < end:
        k = str(begin) + '_' + mcc
        begin += 1
        if Weekend(day) and not Weekend(begin - 1): continue
        if not Weekend(day) and Weekend(begin - 1): continue
        if k in sums:
            m += math.log(500.0 + sums[k])
            n += 1
        else:
            m += math.log(500.0)
            n += 1
    m = m / n if n > 0 else math.log(500.0)
    return m

def PrevWeekendSpentMonthMean(sums, day, step, mccList):
    month, idx = DayOfMonth(day)
    begin, end = 10000, 0
    for i in xrange(step):
        month -= 1
        b, e = MonthBorders(month)
        if b < begin: begin = b
        if e > end: end = e
    m, n = 0, 0
    while begin < end:
        begin += 1
        if Weekend(day) and not Weekend(begin - 1): continue
        if not Weekend(day) and Weekend(begin - 1): continue
        s = 0
        for curm in mccList:
            k2 = str(begin-1) + '_' + curm
            if k2 in sums:
                s += sums[k2]
        m += math.log(500.0 + s)
        n += 1
    return m / n if n > 0 else math.log(500.0)

def PrevWeekAgo(sums, mcc, day, num):
    day -= 35
    res = []
    for i in xrange(num):
        k = str(day) + '_' + mcc
        if k in sums:
            res.append(sums[k])
        else:
            res.append(0)
        day -= 7
    return map(lambda x: math.log(500.0 + x), res)

def PrevMonthDays(sums, mcc, day, num):
    month, idx = DayOfMonth(day)
    begin, end = MonthBorders(month - 1)
    res = []
    for i in xrange(num):
        end -= 1
        k = str(end) + '_' + mcc
        if k in sums:
            res.append(sums[k])
        else:
            res.append(0)
    return map(lambda x: math.log(500.0 + x), res)
