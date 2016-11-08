from optparse import OptionParser                                                                                                                                           
import sys
import xgboost                                                                                                                                        
import numpy as np
import random
import math

from names import AllNames

class My:
    def __init__(self, options):
        self.FF, self.Names = AllNames()
        if options.names:
            for n in self.Names: print n
            sys.exit(0)
        self.ValidUsers, self.Users = set(), set()
        for line in open(options.toeval):
            self.ValidUsers.add(line.rstrip('\n').split(',')[0])
        self.UserF = {}
        for line in open('user_feature', 'rt'):
            line = line.rstrip('\n').split('\t')
            self.UserF[line[0]] = map(float, line[1:])
        self.MccList = {}
        self.Answers = {}
        self.MonthInfo = {}
        self.Months = 16
        self.Spent = {}
        self.DayAnswers = {}
        self.NumAnswers = {}
        self.Income = {}
        self.MccSpent = {}
        for line in open(options.events, 'rt'):
            customer, ts, mcc, tp, amount, term = line.rstrip('\n').split(',')
            if mcc not in self.MccList: self.MccList[mcc] = len(self.MccList)
            amount = float(amount)
            self.Users.add(customer)
            day = int(ts.split(' ')[0])
            month, dayOfMonth = self.DayOfMonth(day)
            if amount >= 0:
                k = str(month) + '_' + customer
                if k not in self.Income:
                    self.Income[k] = 0
                self.Income[k] += amount
                continue
            amount = -amount
            k = customer + '_' + mcc
            if customer not in self.Spent: self.Spent[customer] = [0] * self.Months
            if mcc not in self.MccSpent: self.MccSpent[mcc] = [0] * self.Months
            if k not in self.Answers: self.Answers[k] = [0] * self.Months
            if k not in self.NumAnswers: self.NumAnswers[k] = [0] * self.Months
            if k not in self.DayAnswers: self.DayAnswers[k] = [0] * 487
            self.Spent[customer][month] += amount
            self.MccSpent[mcc][month] += amount
            self.Answers[k][month] += amount
            self.NumAnswers[k][month] += 1
            self.DayAnswers[k][day] += amount
        for u in self.Users:
            for m in self.MccList:
                k = u + '_' + m
                if k not in self.Answers: self.Answers[k] = [0] * self.Months
                if k not in self.NumAnswers: self.NumAnswers[k] = [0] * self.Months
                if k not in self.DayAnswers: self.DayAnswers[k] = [0] * 487

    def Answer(self, customer, mcc):
        k = customer + '_' + mcc
        return math.log(1.0 + self.Answers[self.DayOfMonth(self.EndDay - 1)[0]])

    def Set(self, name, value): 
        self.F[self.FF[name]] = value                                                                                                              
    def Add(self, name, value):
        self.F[self.FF[name]] += value

    def FirstDay(self, month):
        data = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        s = 0
        for i in xrange(1000):
            if i == month: break
            s += data[i]
        return s

    def DaysByMonth(self, month):
        a = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return a[month]
    
    def DayOfMonth(self, day):
        idx = 0
        data = [31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        while True:
            if day < data[idx]:
                return idx, day
            day -= data[idx]
            idx += 1
        return -1, -1

    def Features(self, customer, mcc, month):
        self.F = [0] * len(self.FF)
        v = self.Answers[customer + '_' + mcc]
        vNum = self.NumAnswers[customer + '_' + mcc]
        s, n = 0, 0
        d = self.FirstDay(month) - 1
        vDay = self.DayAnswers[customer + '_' + mcc]
        for i in xrange(90):
            s += vDay[d - i]
            n += 1
            self.Set('PREVDAYS_' + str(i), math.log(1.0 + s / n))
        vv = self.UserF[customer]
        for i in xrange(13):
            self.Set('USER' + str(i), vv[i])
        A, B, C = 0, 0, 0
        for i in xrange(14):
            A += v[month - i - 1]
            B += self.DaysByMonth(month - i - 1)
            C += vNum[month - i - 1]
            mean = float(v[month - i - 1]) / self.DaysByMonth(month - i - 1)
            self.Set('PREVMONTH_' + str(i), math.log(1.0 + v[month - i - 1]))
            self.Set('PREVMONTHNUM_' + str(i), vNum[month - i - 1])
            self.Set('PREVMONTH2_' + str(i), math.log(1.0 + mean * self.DaysByMonth(i)))
            k = str(month - i - 1) + '_' + customer
            if k in self.Income:
                self.Set('INCOME_' + str(i), math.log(1.0 + self.Income[k]))
            if mcc in self.MccSpent:
                self.Set('MCCSPENT_' + str(i), self.MccSpent[mcc][month - i - 1])
            if customer in self.Spent:
                self.Set('SPENT_' + str(i), math.log(1.0 + self.Spent[customer][month - i - 1]))
        self.Set('MCC_' + str(self.MccList[mcc]), 1)
        self.Set('SUPERMEAN', math.log(1.0 + self.DaysByMonth(month) * A / B))
        self.Set('PREVNUM', C)
        self.Set('PREVSUM', A)
        return self.F


def Options():                                                                                                                                                              
    op = OptionParser()                                                                                                                                              
    op.add_option('-E', '--events')
    op.add_option('-l', '--train')
    op.add_option('-F', '--fstr')
    op.add_option('-B', '--bags')
    op.add_option('-R', '--seed')
    op.add_option('-T', '--trees')
    op.add_option('-O', '--out')
    op.add_option('-d', '--depth')
    op.add_option('-e', '--eta')
    op.add_option('-S', '--subsample')
    op.add_option('-v', '--toeval')
    op.add_option("-V", action="store_true", dest="verbose")                                                                                                              
    op.add_option("-D", action="store_true", dest="dump")                                                                                                              
    op.add_option("-Q", action="store_true", dest="names")                                                                                                              
    op.add_option("-P", action="store_true", dest="production")                                                                                                              
    return op.parse_args()[0]

def Features(my, prodShift):                                                                                                                                       
    Xtrain, Ytrain, Xvalid, Yvalid = [], [], [], []                                                                                      
    keys = []
    for u in my.Users:
        for m in my.MccList:
            for month in xrange(15 + prodShift):
                if month < 13 + prodShift: continue
                f = my.Features(u, m, month)
                ans = math.log(1.0 + my.Answers[u + '_' + m][month])
                if month == 14 + prodShift:
                    if u not in my.ValidUsers: continue
                    Xvalid.append(f)
                    Yvalid.append(ans)
                    keys.append([u, m])
                else:
                    Xtrain.append(f)
                    Ytrain.append(ans)
    Xtrain, Ytrain, Xvalid, Yvalid = map(np.asarray, [Xtrain, Ytrain, Xvalid, Yvalid])
    return xgboost.DMatrix(Xtrain, Ytrain), xgboost.DMatrix(Xvalid, Yvalid), Yvalid, keys

def GetParam(options):                                                                                                                                                      
    param = {'silent' : 1, 'objective' : 'reg:linear', 'eval_metric' : 'rmse', 'booster' : 'gblinear'}            
    param['eta'] = float(options.eta)
    param['lambda'] = 0.1
    return param

def GetParamTree(options):
    param = {'silent' : 1, 'objective' : 'reg:linear', 'eval_metric' : 'rmse', 'booster' : 'gbtree'}
    param['max_depth'] = 5
#    param['max_depth'] = 4
    param['eta'] = float(options.eta)
    param['subsample'] = 0.6
    param['colsample_bytree'] = 0.8
#    param['min_child_weight'] = 3
    param['tree_method'] = 'exact'
    return param

if __name__ == '__main__':                                                                                                                                           
    options = Options()                                                                                                                                                    
    my = My(options)
#    param = GetParam(options)                                                                                                                                               
    param = GetParamTree(options)                                                                                                                                               
    param['seed'] = int(options.seed)                                                                                                                                       
    err, n = 0.0, 0
    f = open(options.out, 'wt')
#    for m in my.MccList:
    learn, valid, y, keys = Features(my, 1 if options.production else 0)                                                                                        
    validArray = []                                                                                                                                                         
    if options.verbose:                                                                                                                                                     
        validArray.append((valid, 'eval'))                                                                                                                                  
    bst = xgboost.train(param, learn, int(options.trees), validArray)                                                                                            
    preds = bst.predict(valid)
    f.write('customer_id,mcc_code,volume\n')
    for i in xrange(len(keys)):
        err += (preds[i] - y[i]) ** 2
        n += 1
        f.write(','.join(map(str, [keys[i][0], keys[i][1], math.exp(preds[i]) - 1])) + '\n')
    print math.sqrt(err / n)

