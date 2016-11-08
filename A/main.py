from optparse import OptionParser                                                                                                                                           
import sys
import xgboost                                                                                                                                        
import numpy as np
import random
import math
from sklearn import metrics

from names import AllNames

from sklearn.naive_bayes import BernoulliNB, GaussianNB

class Customer:
    def __init__(self, line):
        self.Id = line[0]
        self.IsLearn = len(line) > 1
        if self.IsLearn:
            self.Ans = int(line[1])
        else:
            self.Ans = 0 if random.random() < 0.5 else 1
        self.Events = []
    def Answer(self): return self.Ans
    def Bag(self, bags): return hash(self.Id) % bags

def ReadStat(path, lmt):
    res = {}
    i = 0
    for line in open(path, 'rt'):
        num, key = line.rstrip('\n').split('\t')
        if int(num) < lmt: continue
        res[key] = [int(num), i]
        i += 1
    return res

class My:
    def __init__(self, options):
        self.MccStat  = ReadStat(options.stat + 'mcc_user', 2)
        self.TypeStat = ReadStat(options.stat + 'type_user', 20)
        self.TermStat = ReadStat(options.stat + 'term', 200)
        self.PairsStat = ReadStat(options.stat + 'pairs_mcc', 500)
        self.FF, self.Names = AllNames(len(self.MccStat), len(self.TypeStat), len(self.TermStat), len(self.PairsStat))
        if options.names:
            for n in self.Names:
                print n
            sys.exit(0)
        self.Learn, self.Validate = [], []
        self.Idx = {}
        self.Male, self.Female = set(), set()
        self.TypeMale, self.TypeFemale = set(), set()
        self.PlusMale, self.PlusFemale = set(), set()
        for line in open(options.stat + 'mcc_male', 'rt'):      self.Male.add(line.rstrip('\n').split('\t')[0])
        for line in open(options.stat + 'type_male', 'rt'):     self.TypeMale.add(line.rstrip('\n').split('\t')[0])
        for line in open(options.stat + 'mcc_male_plus', 'rt'): self.PlusMale.add(line.rstrip('\n').split('\t')[0])

        for line in open(options.stat + 'mcc_female', 'rt'):      self.Female.add(line.rstrip('\n').split('\t')[0])
        for line in open(options.stat + 'type_female', 'rt'):     self.TypeFemale.add(line.rstrip('\n').split('\t')[0])
        for line in open(options.stat + 'mcc_female_plus', 'rt'): self.PlusFemale.add(line.rstrip('\n').split('\t')[0])

        for line in open(options.learn, 'rt'):
            c = Customer(line.rstrip('\n').split(','))
            self.Idx[c.Id] = c
            self.Learn.append(c)
        for line in open(options.valid, 'rt'):
            c = Customer(line.rstrip('\n').split(','))
            self.Idx[c.Id] = c
            self.Validate.append(c)
        self.MccIndex = {}
        self.Auto = {}
        for line in open(options.events, 'rt'):
            customer, ts, mcc, tp, amount, term = line.rstrip('\n').split(',')
#            amount = float(amount) / (math.pi ** math.e)
            day = int(ts.split(' ')[0])
            k = mcc + '_' + str(day)
            if mcc not in self.MccIndex: self.MccIndex[mcc] = len(self.MccIndex)
            if customer in self.Idx:
                if len(self.Idx[customer].Events) > 0 and abs(float(amount) + self.Idx[customer].Events[-1][3]) < 0.01:
                    if customer not in self.Auto: self.Auto[customer] = [0, 0]
                    self.Auto[customer][0] += 1
                    self.Auto[customer][1] += abs(float(amount))
                    self.Idx[customer].Events.pop()
                else:
                    self.Idx[customer].Events.append([ts, mcc, tp, float(amount), term, amount])

    def Set(self, name, value):                                                                                                                                             
        self.F[self.FF[name]] = value 
    def Add(self, name, value):                                                                                                                                             
        self.F[self.FF[name]] += value

    def DayType(self, day):
        day = day % 7
        if day == 0: return 0 #friday
        if day < 3: return 1 #saturday/sunday
        return 2
    
    def DayOfMonth(self, day):
        idx = 0
        data = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        while True:
            if day < data[idx]:
                return idx, day
            day -= data[idx]
            idx += 1
        return -1, -1

    def AddFeatures(self, values, prefix, idx, norm1, norm2, norm3, useAbs):
        self.Set(prefix + 'PLUS_'  + str(idx), values[0]+0.000001)
#        self.Set(prefix + 'PLUSPART_'  + str(idx), values[0]/(values[0]+values[2]+0.00001))
#        self.Set(prefix + 'ALL_'  + str(idx), values[0]+values[2])
        self.Set(prefix + 'MINUS_' + str(idx), values[2])
#        self.Set(prefix + 'MINUSLOG_' + str(idx), math.log(values[2]+0.00001))
        self.Set(prefix + 'NUM_'   + str(idx), values[1])
        if norm1 > 0: self.Set(prefix + 'PLUS_NORM_'  + str(idx), values[0] / float(norm1))
        if norm2 > 0: self.Set(prefix + 'MINUS_NORM_' + str(idx), values[2] / float(norm2))
        if norm3 > 0: self.Set(prefix + 'NUM_NORM_'   + str(idx), values[1] / float(norm3))

    def HistoryFeatures(self, events):
        p, mx, mn, n = 0, -1000000, 1000000, 0
        income, wastes, smallWaste, swnum = 0, 0, 0, 0
        mcc, tp, pairs = {}, {}, {}
        days, hours, dday, dom, dayType = [], [], [], [], []
        for i in xrange(7): days.append([0, 0, 0])
        for i in xrange(24): hours.append([0, 0, 0])
        for i in xrange(18): dday.append([0, 0, 0])
        for i in xrange(3): dayType.append([0, 0, 0])
        for i in xrange(31): dom.append([0, 0, 0])
        prevV, prevMcc, prevDay = 0, '', 0
        for e in events:
            n += 1
            v = e[3]
            day = int(e[0].split(' ')[0])
            dayt = self.DayType(day)
            month, dayOfMonth = self.DayOfMonth(day)
            hour = int(e[0].split(' ')[1].split(':')[0])
            hr, minute, sec = map(int, e[0].split(' ')[1].split(':'))
            pairKey = e[1] + '_' + prevMcc
            if e[1] not in mcc: mcc[e[1]] = [0, 0, 0]
            if e[2] not in tp:  tp[e[2]] = [0, 0, 0]
            if pairKey not in pairs: pairs[pairKey] = [0, 0, 0]
            if v > 0: pairs[pairKey][0] += v
            else: pairs[pairKey][2] -= v
            if prevV > 0: pairs[pairKey][0] += prevV
            else: pairs[pairKey][2] -= prevV
            pairs[pairKey][1] += 1
            prevV, prevMcc = v, e[1]
            if v > 0:
                dday[month][0] += v
                dom[month][0] += v
                days[day % 7][0] += v
                dayType[dayt][0] += v
                hours[hour][0] += v
                mcc[e[1]][0] += v
                tp[e[2]][0] += v
                p += 1
                income += v
            else:
                days[day % 7][2] -= v
                dday[month][2] -= v
                dayType[dayt][2] -= v
                hours[hour][2] -= v
                dom[month][2] -= v
                mcc[e[1]][2] -= v
                tp[e[2]][2] -= v
                wastes -= v
                if abs(v) < 23000:
                    smallWaste -= v
                    swnum += 1
            dday[month][1] += 1
            dom[month][1] += 1
            days[day % 7][1] += 1
            dayType[dayt][1] += 1
            hours[hour][1] += 1
            mcc[e[1]][1] += 1
            tp[e[2]][1] += 1
            if mx < v: mx = v
            if mn > v: mn = v
            if e[4] in self.TermStat:
                curVal = self.TermStat[e[4]]
                self.Set('TERMINAL_' + str(curVal[1]), 1)

        for i in xrange(18):
            self.AddFeatures(dday[i],  'DDAY',       i, income, wastes, n, True)
        for i in xrange(31):
            self.AddFeatures(dom[i],   'DAYOFMONTH', i, income, wastes, n, True)
        for i in xrange(7):
            self.AddFeatures(days[i],  'DAY',        i, income, wastes, n, False)
        for i in xrange(3):
            self.AddFeatures(dayType[i], 'DAYTYPE',  i, income, wastes, n, False)
        for i in xrange(24):
            self.AddFeatures(hours[i], 'HOUR',       i, income, wastes, n, False)

        self.Set('EVENTS_NUM', n)
        self.Set('EVENTS_POS_PART', p / (0.000001 + n))
        self.Set('EVENTS_MIN', mn)
        self.Set('EVENTS_MAX', mx)
        self.Set('EVENTS_INCOME', income)
        self.Set('EVENTS_WASTE', wastes)
#        self.Set('SMALL_WASTE', smallWaste / (wastes + 0.000001))
#        self.Set('SMALL_WASTE_PART', swnum / (n + 0.000001))
        male, female, maleNum, femaleNum = 0, 0, 0, 0
        pmale, pfemale, pmaleNum, pfemaleNum = 0, 0, 0, 0

        for k in mcc:
            if k in self.Male:
                male       += mcc[k][2]
                maleNum    += mcc[k][1]
            if k in self.Female:
                female     += mcc[k][2]
                femaleNum  += mcc[k][1]
            if k in self.PlusMale:
                pmale       += mcc[k][0]
                pmaleNum    += mcc[k][1]
            if k in self.PlusFemale:
                pfemale     += mcc[k][0]
                pfemaleNum  += mcc[k][1]
            if k not in self.MccStat: 
                continue
            v = self.MccStat[k]
            self.AddFeatures(mcc[k], 'MCC', v[1], income, wastes, n, True)
        idx = 0
        for i in xrange(7):
            if days[i][2] > days[idx][2]:
                idx = i
        self.Set('SPENDDAY', idx)
        if male > female: self.Set('MALEMORE', 1)
        if income > wastes: self.Set('INCOMEMORE', 1)

        self.Set('MALE_SPENT', male)
        self.Set('MALE_SPENT_NUM', maleNum)
        self.Set('FEMALE_SPENT', female)
        self.Set('FEMALE_SPENT_NUM', femaleNum)
        self.Set('PMALE_SPENT', pmale)
        self.Set('PMALE_SPENT_NUM', pmaleNum)
        self.Set('PFEMALE_SPENT', pfemale)
        self.Set('PFEMALE_SPENT_NUM', pfemaleNum)
        male, female, maleNum, femaleNum = 0, 0, 0, 0
        for k in tp:
            if k in self.TypeMale:
                male       += tp[k][2]
                maleNum    += tp[k][1]
            if k in self.TypeFemale:
                female     += tp[k][2]
                femaleNum  += tp[k][1]
            if k not in self.TypeStat:
                continue
            v = self.TypeStat[k]
            self.AddFeatures(tp[k], 'TYPE', v[1], income, wastes, n, True)
        self.Set('TPMALE_SPENT', male)
        self.Set('TPMALE_SPENT_NUM', maleNum)
        self.Set('TPFEMALE_SPENT', female)
        self.Set('TPFEMALE_SPENT_NUM', femaleNum)
        for k in pairs:
            if k not in self.PairsStat:
                continue
            v = self.PairsStat[k]
            self.AddFeatures(pairs[k], 'PAIRS', v[1], income, wastes, n, True)
        
    def Features(self, customer):
        self.F = [0] * len(self.FF)
        self.HistoryFeatures(self.Idx[customer.Id].Events)
        return self.F

    def Convert(self, f):
        res = [0] * len(self.MccStat)
        for i in xrange(len(self.MccStat)):
            if f[self.FF['MCCNUM_' + str(i)]] > 0:
                res[i] = 1
        return res

    def ConvertGauss(self, f):
        res = [0] * len(self.MccStat)
        for i in xrange(len(self.MccStat)):
            res[i] = f[self.FF['MCCMINUS_' + str(i)]]
        return res

    def Fit(self, bags, bagData):
        self.Bayes, self.GBayes = [], []
        for i in xrange(10):
            bnb = BernoulliNB()
            gnb = GaussianNB()
            x, y, xg = [], [], []
            for j in xrange(10):
                if i != j:
                    for vv in xrange(len(bagData[j][0])):
                        x.append(self.Convert(bagData[j][0][vv]))
                        xg.append(self.ConvertGauss(bagData[j][0][vv]))
                    y.extend(bagData[j][1])
            bnb.fit(x, y)
            gnb.fit(xg, y)
            self.Bayes.append(bnb)
            self.GBayes.append(gnb)
    
    def ApplyBayes(self, bag, x):
        lst = [self.Convert(x)]
        val = self.Bayes[bag].predict_proba(lst)[0][0]
        x[self.FF['BAYES']] = val
        lst = [self.ConvertGauss(x)]
        val = self.GBayes[bag].predict_proba(lst)[0][0]
        x[self.FF['GBAYES']] = val

def Dump(feat, my, customer):
    toPrint = [customer]
    toPrint.extend(feat[:11])
    toPrint.append(math.log(1.0 + feat[my.FF['MALE_SPENT']]))
    toPrint.append(math.log(1.0 + feat[my.FF['FEMALE_SPENT']]))
    print '\t'.join(map(str, toPrint))

def Options():                  
    op = OptionParser()                                                                                                                                              
    op.add_option('-l', '--learn')
    op.add_option('-v', '--valid')
    op.add_option('-d', '--depth')
    op.add_option('-e', '--eta')
    op.add_option('-E', '--events')
    op.add_option('-F', '--fstr')
    op.add_option('-M', '--meta')
    op.add_option('-s', '--stat')
    op.add_option('-S', '--subsample')
    op.add_option('-R', '--seed')
    op.add_option('-T', '--trees')
    op.add_option('-O', '--out')
    op.add_option("-V", action="store_true", dest="verbose")                                                                                                              
    op.add_option("-D", action="store_true", dest="dump")                                                                                                              
    op.add_option("-Q", action="store_true", dest="names")                                                                                                              
    return op.parse_args()[0]

def Features(my, dump):                                                                                                                                       
    Xtrain, Ytrain, Xvalid, Yvalid = [], [], [], []                                                                                      
    bags = []
    for i in xrange(10): bags.append([[], [], []])
    for i in my.Learn:                                                                    
        f = my.Features(i)
        b = i.Bag(10)
        bags[b][0].append(f)
        bags[b][1].append(i.Answer())
        bags[b][2].append(i.Id)
    my.Fit(10, bags)
    for i in xrange(10):
        for j in xrange(len(bags[i][0])):
            v = bags[i][0][j]
            my.ApplyBayes(i, v)
            Xtrain.append(v)
            Ytrain.append(bags[i][1][j])
            if dump:
                Dump(v, my, bags[i][2][j])
    for i in my.Validate:                                                                                                                                 
        f = my.Features(i)              
        my.ApplyBayes(i.Bag(10), f)
        Xvalid.append(f)                                                                                                                                                 
        Yvalid.append(i.Answer())         
        if dump:
            Dump(f, my, i.Id)
    if dump:
        sys.exit(0)
    Xtrain, Ytrain, Xvalid, Yvalid = map(np.asarray, [Xtrain, Ytrain, Xvalid, Yvalid])
    return xgboost.DMatrix(Xtrain, Ytrain), xgboost.DMatrix(Xvalid, Yvalid), Yvalid

def GetParam(options):                                                                                                                                                      
    param = {'silent' : 1, 'objective' : 'binary:logistic', 'eval_metric' : 'logloss'}            
    param['max_depth'] = int(options.depth)                                                     
    param['eta'] = float(options.eta)                                                                                                                 
    param['subsample'] = float(options.subsample)                                                                                                        
    param['colsample_bytree'] = 0.8
#    param['gamma'] = 2
#    param['colsample_bylevel'] = 0.9
    param['min_child_weight'] = 3                                                                                                           
    return param                                                                                                                                                            

if __name__ == '__main__':                                                                                                                                           
    options = Options()                                                                                                                                                    
    my = My(options)
    learn, valid, y = Features(my, options.dump)                                                                                        
    param = GetParam(options)                                                                                                                                               
    param['seed'] = int(options.seed)                                                                                                                                       
    validArray = []                                                                                                                                                         
    if options.verbose:                                                                                                                                                     
        validArray.append((valid, 'eval'))                                                                                                                                  
    bst = xgboost.train(param, learn, int(options.trees), validArray)                                                                                            
    if options.fstr:                                                                                                                                       
        with open(options.fstr, 'wt') as f:                                                                                                                     
            for k in bst.get_fscore().keys():                                                                                                                    
                f.write(str(k) + '\t' + str(bst.get_fscore()[k]) + '\n')
    preds = bst.predict(valid)  
    fpr, tpr, thresholds = metrics.roc_curve(y, preds)
    print metrics.auc(fpr, tpr)
    if options.out:
        f = open(options.out, 'wt')
        for p in preds:
            f.write(str(p) + '\n')
