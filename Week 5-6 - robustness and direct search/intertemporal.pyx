from libc.math cimport log, sqrt

import numpy as np
from scipy.optimize import brentq

cimport cython
cimport numpy as cnp

ctypedef cnp.float_t DTYPE_t

@cython.cdivision(True)
@cython.boundscheck(False) 
def cython_lake_model(float b=0.42, float q=2.0, float mean=0.02, float stdev=0.001, 
                float delta=0.98, float alpha=0.4, int steps=100, int reps=100,
                float l0=0.0, float l1=0.0, 
                float l2=0.0, float l3=0.0, float l4=0.0, float l5=0.0, float l6=0.0,
                float l7=0.0, float l8=0.0, float l9=0.0, float l10=0.0, float l11=0.0,
                float l12=0.0, float l13=0.0, float l14=0.0, float l15=0.0, float l16=0.0,
                float l17=0.0, float l18=0.0, float l19=0.0, float l20=0.0, float l21=0.0,
                float l22=0.0, float l23=0.0, float l24=0.0, float l25=0.0, float l26=0.0,
                float l27=0.0, float l28=0.0, float l29=0.0, float l30=0.0, float l31=0.0,
                float l32=0.0, float l33=0.0, float l34=0.0, float l35=0.0, float l36=0.0,
                float l37=0.0, float l38=0.0, float l39=0.0, float l40=0.0, float l41=0.0,
                float l42=0.0, float l43=0.0, float l44=0.0, float l45=0.0, float l46=0.0,
                float l47=0.0, float l48=0.0, float l49=0.0, float l50=0.0, float l51=0.0,
                float l52=0.0, float l53=0.0, float l54=0.0, float l55=0.0, float l56=0.0,
                float l57=0.0, float l58=0.0, float l59=0.0, float l60=0.0, float l61=0.0,
                float l62=0.0, float l63=0.0, float l64=0.0, float l65=0.0, float l66=0.0,
                float l67=0.0, float l68=0.0, float l69=0.0, float l70=0.0, float l71=0.0,
                float l72=0.0, float l73=0.0, float l74=0.0, float l75=0.0, float l76=0.0,
                float l77=0.0, float l78=0.0, float l79=0.0, float l80=0.0, float l81=0.0,
                float l82=0.0, float l83=0.0, float l84=0.0, float l85=0.0, float l86=0.0,
                float l87=0.0, float l88=0.0, float l89=0.0, float l90=0.0, float l91=0.0,
                float l92=0.0, float l93=0.0, float l94=0.0, float l95=0.0, float l96=0.0,
                float l97=0.0, float l98=0.0, float l99=0.0): 
    '''
    # decay rate for P in lake (0.42 = irreversible)
    # recycling exponent
    # mean of natural inflows
    # future utility discount rate
    # standard deviation of natural inflows
    # utility from pollution
    # number of replications
    
    '''
    cdef float Pcrit, transformed_mean, transformed_sigma, mean_reliability,
    cdef float utility, inertia, max_p
    cdef int t, i, r
    cdef cnp.ndarray[DTYPE_t, ndim=2] X
    cdef cnp.ndarray[DTYPE_t, ndim=1] reliability
    cdef cnp.ndarray[DTYPE_t, ndim=1] decisions
    cdef cnp.ndarray[DTYPE_t, ndim=1] natural_inflows  
    
    X = np.zeros([reps, steps], dtype=np.float)
    reliability = np.zeros([reps,], dtype=np.float)
    decisions = np.array([l0, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13,
                            l14, l15, l16, l17, l18, l19, l20, l21, l22, l23, l24, l25,
                            l26, l27, l28, l29, l30, l31, l32, l33, l34, l35, l36, l37,
                            l38, l39, l40, l41, l42, l43, l44, l45, l46, l47, l48, l49,
                            l50, l51, l52, l53, l54, l55, l56, l57, l58, l59, l60, l61,
                            l62, l63, l64, l65, l66, l67, l68, l69, l70, l71, l72, l73,
                            l74, l75, l76, l77, l78, l79, l80, l81, l82, l83, l84, l85,
                            l86, l87, l88, l89, l90, l91, l92, l93, l94, l95, l96, l97,
                            l98, l99])
    
    Pcrit = brentq(lambda x: x**q/(1+x**q) - b*x, 0.01, 1.5)

    transformed_mean = log(mean**2 / sqrt(stdev**2 + mean**2))
    transformed_sigma = sqrt(log(1.0 + stdev**2 / mean**2))

    for r in range(reps):
        natural_inflows = np.random.lognormal(transformed_mean, transformed_sigma, size=steps)
        
        for t in range(1, steps):
            X[r, t] = (1-b)*X[r, t-1] + X[r, t-1]**q/(1+X[r, t-1]**q) + decisions[t-1] + natural_inflows[t-1]
        
        
        reliability[r] = np.sum(X[r, :] < Pcrit)/steps
    
    mean_reliability = np.mean(reliability)
    inertia = np.sum(np.abs(np.diff(decisions)) < 0.01)/(steps-1)
    utility = np.sum(alpha*decisions*np.power(delta,np.arange(steps)))
    
    max_p = np.max(np.mean(X, axis=1))
    return max_p, utility, inertia, mean_reliability