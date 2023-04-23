"""
Created on Sun Oct 29 15:52:12 2017

@author: ciullo
"""
import numpy as np


def cost_fun(ratio, c, b, lambd, dikeinit, dikeincrease):
    """Cost of raising the dikes, assuming an exponential function"""

    dikeincrease = dikeincrease * 100  # cm
    dikeinit = dikeinit * 100

    cost = ((c + b * dikeincrease) * np.exp(lambd * (dikeinit + dikeincrease))) * ratio
    return cost * 1e6


def discount(amount, rate, n):
    """discount function overall a planning period of n years"""

    factor = 1 + rate / 100
    disc_amount = amount * 1 / (np.repeat(factor, n) ** (range(1, n + 1)))
    return disc_amount


def cost_evacuation(N_evacuated, days_to_threat):
    # if days to threat is zero, then no evacuation happens, costs are zero
    cost = N_evacuated * 22 * (days_to_threat + 3) * (int(days_to_threat > 0))
    return cost
