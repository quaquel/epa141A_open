"""
Created on Thu Jul 06 14:51:04 2017

@author: ciullo
"""
import numpy as np


def dikefailure(
    sb, inflow, hriver, hbas, hground, status_t1, Bmax, Brate, simtime, tbreach, critWL
):
    """Function establising dike failure as well as flow balance between the
    river and the polder

     inflow = flow coming into the node
     status = if False the dike has not failed yet
     critWL = water level above which we have failure

    """
    tbr = tbreach
    #    h1 = hriver - hbreach
    #    h2 = (hbas + hground) - hbreach

    # h river is a water level, hbas a water depth
    h1 = hriver - (hground + hbas)

    # if the dike has already failed:
    if status_t1 == True:
        B = Bmax * (1 - np.exp(-Brate * (simtime - tbreach)))

        if h1 > 0:
            breachflow = 1.7 * B * (h1) ** 1.5

        # h1 <0 ==> no flow:
        else:
            breachflow = 0

        outflow = max(0, inflow - breachflow)
        status_t2 = status_t1

    # if the dike has not failed yet:
    else:
        failure = hriver > critWL
        outflow = inflow
        breachflow = 0
        # if it fails:
        if failure:
            status_t2 = True
            tbr = simtime
        # if it does not:
        else:
            status_t2 = False

    # if effects of hydrodynamic system behaviour have to be ignored:
    if sb == False:
        outflow = inflow

    return outflow, breachflow, status_t2, tbr


def Lookuplin(MyFile, inputcol, searchcol, inputvalue):
    """Linear lookup function"""
    return np.interp(inputvalue, MyFile[:, inputcol], MyFile[:, searchcol])


def init_node(value, time):
    init = np.repeat(value, len(time)).tolist()
    return init
