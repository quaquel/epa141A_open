
"""
Python model ./model/SEIR or SIR 20170501.py
Translated using PySD version 0.7.2
"""
from __future__ import division
import numpy as np
from pysd import utils
import xarray as xr

from pysd.functions import cache
from pysd import functions

_subscript_dict = {}

_namespace = {
    'Exposed population': 'exposed_population', 'TIME': 'time', 'Time': 'time',
    'Basic reproduction number': 'basic_reproduction_number',
    'Deceased population': 'deceased_population', 'Dying': 'dying', 'SAVEPER': 'saveper',
    'Case fatality rate': 'case_fatality_rate', 'Susceptible population': 'susceptible_population',
    'Initial recovered population': 'initial_recovered_population',
    'Average infectious period': 'average_infectious_period',
    'Initial susceptible population': 'initial_susceptible_population',
    'INITIAL TIME': 'initial_time', 'Recovered population': 'recovered_population',
    'Incubation': 'incubation', 'FINAL TIME': 'final_time',
    'Initial exposed population': 'initial_exposed_population',
    'Initial infectious population': 'initial_infectious_population', 'TIME STEP': 'time_step',
    'Fraction susceptible population': 'fraction_susceptible_population',
    'Switch SEIR or SIR': 'switch_seir_or_sir',
    'Initial deceased population': 'initial_deceased_population',
    'Total population': 'total_population', 'Infectious population': 'infectious_population',
    'Infecting': 'infecting', 'Surviving': 'surviving',
    'Average incubation time': 'average_incubation_time'}


integ_deceased_population = functions.Integ(lambda: dying(), lambda: initial_deceased_population())


@cache('step')
def incubation():
    """
    Incubation
    ----------
    (incubation)
    Person/Day

    """
    return functions.if_then_else(
        switch_seir_or_sir() == 1,
        exposed_population() /
        average_incubation_time(),
        infecting())


@cache('step')
def exposed_population():
    """
    Exposed population
    ------------------
    (exposed_population)
    Person

    """
    return integ_exposed_population()


integ_infectious_population = functions.Integ(
    lambda: incubation() - dying() - surviving(),
    lambda: initial_infectious_population())


@cache('run')
def initial_deceased_population():
    """
    Initial deceased population
    ---------------------------
    (initial_deceased_population)
    Person

    """
    return 0


@cache('run')
def case_fatality_rate():
    """
    Case fatality rate
    ------------------
    (case_fatality_rate)
    Dmnl

    """
    return 0.01


@cache('step')
def dying():
    """
    Dying
    -----
    (dying)
    Person/Day

    """
    return case_fatality_rate() * infectious_population() / average_infectious_period()


@cache('run')
def initial_infectious_population():
    """
    Initial infectious population
    -----------------------------
    (initial_infectious_population)
    Person

    """
    return 1


@cache('step')
def time():
    """
    TIME
    ----
    (time)
    None
    The time of the model
    """
    return _t


@cache('run')
def switch_seir_or_sir():
    """
    Switch SEIR or SIR
    ------------------
    (switch_seir_or_sir)
    Dmnl [1,1,2]
    1 = SEIR, ELSE = SIR
    """
    return 0


@cache('run')
def average_infectious_period():
    """
    Average infectious period
    -------------------------
    (average_infectious_period)
    Day

    """
    return 14


@cache('step')
def deceased_population():
    """
    Deceased population
    -------------------
    (deceased_population)
    Person

    """
    return integ_deceased_population()


@cache('step')
def recovered_population():
    """
    Recovered population
    --------------------
    (recovered_population)
    Person

    """
    return integ_recovered_population()


@cache('run')
def initial_time():
    """
    INITIAL TIME
    ------------
    (initial_time)
    Day
    The initial time for the simulation.
    """
    return 0


@cache('step')
def saveper():
    """
    SAVEPER
    -------
    (saveper)
    Day [0,?]
    The frequency with which output is stored.
    """
    return time_step()


@cache('step')
def infecting():
    """
    Infecting
    ---------
    (infecting)
    Person/Day

    """
    return infectious_population(
    ) * basic_reproduction_number() * fraction_susceptible_population() / average_infectious_period()


@cache('step')
def surviving():
    """
    Surviving
    ---------
    (surviving)
    Person/Day

    """
    return (1 - case_fatality_rate()) * infectious_population() / average_infectious_period()


@cache('step')
def infectious_population():
    """
    Infectious population
    ---------------------
    (infectious_population)
    Person

    """
    return integ_infectious_population()


@cache('run')
def final_time():
    """
    FINAL TIME
    ----------
    (final_time)
    Day
    The final time for the simulation.
    """
    return 360


integ_recovered_population = functions.Integ(
    lambda: surviving(), lambda: initial_recovered_population())


@cache('run')
def time_step():
    """
    TIME STEP
    ---------
    (time_step)
    Day [0,?]
    The time step for the simulation.
    """
    return 0.125


@cache('run')
def average_incubation_time():
    """
    Average incubation time
    -----------------------
    (average_incubation_time)
    Day

    """
    return 2


@cache('run')
def initial_susceptible_population():
    """
    Initial susceptible population
    ------------------------------
    (initial_susceptible_population)
    Person

    """
    return 100000


@cache('run')
def basic_reproduction_number():
    """
    Basic reproduction number
    -------------------------
    (basic_reproduction_number)
    Dmnl

    """
    return 2


@cache('run')
def initial_exposed_population():
    """
    Initial exposed population
    --------------------------
    (initial_exposed_population)
    Person

    """
    return 0


integ_susceptible_population = functions.Integ(
    lambda: -infecting(), lambda: initial_susceptible_population())


@cache('run')
def initial_recovered_population():
    """
    Initial recovered population
    ----------------------------
    (initial_recovered_population)
    Person

    """
    return 0


@cache('step')
def fraction_susceptible_population():
    """
    Fraction susceptible population
    -------------------------------
    (fraction_susceptible_population)
    Dmnl

    """
    return susceptible_population() / total_population()


integ_exposed_population = functions.Integ(
    lambda: infecting() - incubation(),
    lambda: initial_exposed_population())


@cache('step')
def total_population():
    """
    Total population
    ----------------
    (total_population)
    Person

    """
    return susceptible_population() + exposed_population() + infectious_population() + recovered_population()


@cache('step')
def susceptible_population():
    """
    Susceptible population
    ----------------------
    (susceptible_population)
    Person

    """
    return integ_susceptible_population()


def time():
    return _t


functions.time = time
functions._stage = lambda: _stage
