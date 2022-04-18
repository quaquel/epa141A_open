# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 15:55:19 2017

@author: ciullo
"""
import random
import numpy as np

#


def werklijn_cdf(Xlist, A):
    """  werklijn function: step-wise distribution of high discharges
    """

    X = np.asarray(Xlist)
    nl = np.shape(A)[0]
    a = A['a'].values
    b = A['b'].values

    XL = A['Q'].values
    XL = np.append(XL, np.inf)
    # A['Q'].loc[nl + 1] = np.inf

    # P = np.repeat(np.nan, np.size(X))
    P = np.empty(X.shape)
    P[:] = np.nan
    for j in range(0, nl):
        indexlow = X >= XL[j]
        indexup = X < XL[j + 1]
        index = np.where((indexlow * indexup) == True)[0]
        P[index] = np.exp(-np.exp(-(X[index] - b[j]) / a[j]))
    return P


def werklijn_inv(Plist, A):
    """ inverse probability distribution function
    probability is translated to frequency.
    X is a piece-wise linear function of log(frequency)

    input
    P:    probability of non-exceedance
    A:  parameters of the werklijn

    output
    X:    x-value, asociated with P
    """

    P = np.asarray(Plist)
    nl = np.shape(A)[0]
    a = A['a'].values
    b = A['b'].values
    # A['RP'].loc[nl + 1] = np.inf
    RPL = A['RP'].values
    RPL = np.append(RPL, np.inf)

    Fe = -np.log(P)
    RP = 1 / Fe

    X = np.empty(P.shape)
    X[:] = np.nan
    # X = np.repeat(np.nan, np.size(P))
    for j in range(nl):
        indexlow = RP >= RPL[j]
        indexup = RP < RPL[j + 1]
        index = np.where((indexlow * indexup) == True)[0]
        X[index] = a[j] * np.log(RP[index]) + b[j]

    return X


def werklijn_pdf(Xlist, A):
    """ pdf according to "werklijn"
    probability is translated to frequency.
    X is a piece-wise linear function of log(frequency)

    input
    X:    x-value
    A:  parameters of the werklijn

    output
    P:    probability density
    """

    X = np.array(Xlist)

    nl = np.shape(A)[0]
    a = A['a'].values
    b = A['b'].values
    A['Q'].loc[nl + 1] = np.inf
    XL = A['Q'].values

    # derive P-values
    P = np.repeat(np.nan, np.size(X))
    for j in range(0, nl):
        indexlow = X >= XL[j]
        indexup = X < XL[j + 1]
        index = np.where((indexlow * indexup) == True)[0]
        P[index] = werklijn_cdf(X[index], A) * \
            np.exp(-(X[index] - b[j]) / a[j]) * (1 / a[j])
    return P


def rand_werklijn(A):
    """ randomly sample from werklijn """
    u = random.random()
    return werklijn_inv([u], A)
