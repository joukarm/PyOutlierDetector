# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 20:04:58 2020

@author: Mohammad
"""

import statistics
import numpy as np


def AvgNeighbourDiff(dfProduction, index):
    err = 0
    t = dfProduction['time'][index]
    q = dfProduction['rate'][index]
    for i in range(5):
        if i != 2:
            t_current = dfProduction['time'][index - 2 + i]
            q_current = dfProduction['rate'][index - 2 + i]
            err += abs((q_current - q) / (t_current - t)) * (3 - abs(i))

    return err


def AvgNeighbourDiffSlopeDependent(dfProduction, index):
    err = 0
    t = dfProduction['time'][index]
    q = dfProduction['rate'][index]

    ns = 1
    for i in range(5):

        if i != 2:
            t_current = dfProduction['time'][index - 2 + i]
            q_current = dfProduction['rate'][index - 2 + i]
            err += abs((q_current - q) / (t_current - t))

        qim1 = dfProduction['rate'][index - 2 - 1]
        qip1 = dfProduction['rate'][index - 2 + 1]
        if (q_current - qim1) * (qip1 - q_current) < 0:
            ns = 1

    qmax = max(dfProduction['rate'][index - 2:index + 3])
    qmin = min(dfProduction['rate'][index - 2:index + 3])
    multiplier = 1
    if q_current - qmin > qmax - q_current:
        multiplier = 1 + (q_current - qmin) / q_current
    else:
        multiplier = 1 + (qmax - q_current) / q_current

    return err * multiplier * ns


def GetOutliersUsingStdDevMultiplier(df, stdDevMultiplier):
    errMargin = statistics.mean(df['kval']) + statistics.stdev(df['kval']) * stdDevMultiplier
    return df[df.kval > errMargin]


def GetOutliersUsingPercentile(df, TopOutliersPercentageToRemove):
    errMargin = np.percentile(a=df['kval'], q=100 - TopOutliersPercentageToRemove)
    return df[df.kval > errMargin]
