import sys
import numpy
import pandas
import math
import numpy as np

from sklearn.metrics import mean_squared_error
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import *

from common import *

numpy.random.seed(0)

sums, mccs = ReadEvents(sys.argv[1])

monthes = 3
lday = 92
vday = int(sys.argv[2])
eday = int(sys.argv[3])

output = open(sys.argv[4], 'wt')

trainX, trainY, validX, validY = [], [], [], []
mccNames = []

for day in xrange(eday):
    if day < lday:
        continue
    month, dayOfMonth = DayOfMonth(day)
    F = [0] * 8
    Y = []
    F[day % 7] = 1
    if IsHoliday(day): F[7] = 1
    for m in mccs:
        if day == lday: mccNames.append(m)
        features = []

        for i in xrange(monthes): features.append(PrevMonthMean(sums, m, day, 1+i))
        for i in xrange(monthes): features.append(PrevWeekendMonthMean(sums, m, day, 1+i))
        for i in xrange(monthes): features.append(PrevSamedayMonthMean(sums, m, day, 1+i))

        features.append(AllPrevMonthMean(sums, m, day, False))
        features.append(AllPrevMonthMean(sums, m, day, True))
        features.append(SuperMean(sums, m, day))
        features.append(SuperWeekendMean(sums, m, day))

        k = str(day) + '_' + m
        y = sums[k] if k in sums else 0
        y = math.log(500.0 + y)
        F.extend(features)
        Y.append(y)
    if day < vday:
        trainX.append(F)
        trainY.append(Y)
    if day >= vday:
        validX.append(F)
        validY.append(Y)
num = len(validY)
trainX, trainY, validX, validY = map(numpy.asarray, [trainX, trainY, validX, validY])

kernel = 1.0 * RBF() + 1.0 * WhiteKernel() + 1.0 * RationalQuadratic() + 1.0 * DotProduct()

gp = GaussianProcessRegressor(kernel=kernel)
gp.fit(trainX, trainY)

y_pred, sigma = gp.predict(validX, return_std=True)
err, n = 0.0, 0

f.write('mcc_code,day,volume\n')
for i in xrange(num):
    for j in xrange(184):
        err += (validY[i][j] - (y_pred[i][j])) ** 2
        n += 1
        f.write(','.join(map(str, [mccNames[j], vday + i, math.exp(y_pred[i][j]-0.01) - 500])) + '\n')
print str(math.sqrt(err / n))

