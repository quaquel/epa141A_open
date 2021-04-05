
import numpy as np
from scipy.optimize import brentq

cimport cython
cimport numpy as cnp
from libc.math cimport log, sqrt

cdef inline float float_max(float a, float b): return a if a >= b else b
cdef inline float float_min(float a, float b): return a if a <= b else b

ctypedef cnp.float_t DTYPE_t

@cython.cdivision(True)
cpdef float cython_get_anthropogenic_release(float xt, float c1, float c2,
                                             float r1, float r2, float w1):
    '''
    Parameters
    ----------
    xt : float      polution in lake at time t (current)
    c1 : float      center rbf 1
    c2 : float      center rbf 2
    r1 : float      radius rbf 1
    r2 : float      radius rbf 2
    w1 : float      weight of rbf 1

    note:: w2 = 1 - w1
    '''
    cdef float rule, at, var1, var2

    var1 = (xt-c1)/r1
    var1 = abs(var1)
    var2 = (xt-c2)/r2
    var2 = abs(var2)

    rule = w1*(var1**3)+(1-w1)*(var2**3)
    at = float_min(float_max(rule, 0.01), 0.1)
    return at

@cython.cdivision(True)
@cython.boundscheck(False)
def lake_model(float b=0.41, float q=2.0,
                      float mean=0.02, float stdev=0.001,
                      float alpha=0.4, float delta=0.98,
                      #Policy Variables
                      float c1=0.25, float c2=0.25,
                      float r1=0.5, float r2=0.5,
                      float w1=0.5,
                      #End Policy Variables
                      int reps=100, int steps=100):
    '''
    runs the lake model for 1 stochastic realisation using specified
    random seed.

    Parameters
    ----------
    b     : float   decay rate for P in lake (0.42 = irreversible)
    q     : float   recycling exponent
    mean  : float   mean of natural inflowsa
    stdev : float   standard deviation of natural inflows
    alpha : float   utility from pollution
    delta : float   future utility discount rate
    reps  : int
    c1    : float
    c2    : float
    r1    : float
    r2    : float
    w1    : float
    steps : int     the number of time steps (e.g., days)
    '''
    cdef float Pcrit, transformed_mean, transformed_sigma
    cdef float utility, inertia, max_p, mean_reliability
    cdef Py_ssize_t t, r
    cdef cnp.ndarray[DTYPE_t, ndim=2] X = np.zeros([reps, steps], dtype=np.float)
    cdef cnp.ndarray[DTYPE_t, ndim=2] decisions = np.zeros([reps, steps], dtype=np.float)
    cdef cnp.ndarray[DTYPE_t, ndim=1] reliability = np.zeros([reps,], dtype=np.float)
    cdef cnp.ndarray[DTYPE_t, ndim=1] natural_inflows

    Pcrit = brentq(lambda x: x**q/(1+x**q) - b*x, 0.01, 1.5)

    transformed_mean = log(mean**2 / sqrt(stdev**2 + mean**2))
    transformed_sigma = sqrt(log(1.0 + stdev**2 / mean**2))
    natural_inflows = np.random.lognormal(transformed_mean, transformed_sigma, size=steps)

    for r in range(reps):
        natural_inflows = np.random.lognormal(transformed_mean, transformed_sigma, size=steps)

        for t in range(1, steps):
            decisions[r, t-1] = cython_get_anthropogenic_release(X[r, t-1], c1, c2, r1, r2, w1)
            X[r, t] = (1-b)*X[r, t-1] + X[r, t-1]**q/(1+X[r, t-1]**q) + decisions[r, t-1] + natural_inflows[t-1]

        reliability[r] = np.sum(X[r, :] < Pcrit)/steps

    mean_reliability = np.mean(reliability)
    inertia = np.mean(np.sum(np.abs(np.diff(decisions)) < 0.01, axis=1)/(steps-1))
    utility = np.mean(np.sum(alpha*decisions*np.power(delta,np.arange(steps)), axis=1))
    max_p = np.max(np.mean(X, axis=1))

    return max_p, utility, inertia, mean_reliability
