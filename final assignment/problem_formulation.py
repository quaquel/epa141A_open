# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 17:34:11 2018

@author: ciullo
"""
from ema_workbench import (Model, CategoricalParameter,
                           ScalarOutcome, IntegerParameter, RealParameter)
from dike_model_function import DikeNetwork  # @UnresolvedImport


def sum_over(*args):
    return sum(args)


def get_model_for_problem_formulation(problem_formulation_id):
    ''' Prepare DikeNetwork in a way it can be input in the EMA-workbench.
    Specify uncertainties, levers and problem formulation.
    '''
    # Load the model:
    function = DikeNetwork()
    # workbench model:
    dike_model = Model('dikesnet', function=function)

    # Uncertainties and Levers:
    # Specify uncertainties range:
    Real_uncert = {'Bmax': [30, 350], 'pfail': [0, 1]}  # m and [.]
    # breach growth rate [m/day]
    cat_uncert_loc = {'Brate': (1., 1.5, 10)}

    cat_uncert = {'discount rate {}'.format(n): (1.5, 2.5, 3.5, 4.5)
                    for n in function.planning_steps}
    
    Int_uncert = {'A.0_ID flood wave shape': [0, 132]}
    # Range of dike heightening:
    dike_lev = {'DikeIncrease': [0, 10]}    # dm

    # Series of five Room for the River projects:
    rfr_lev = ['{}_RfR'.format(project_id) for project_id in range(0, 5)]

    # Time of warning: 0, 1, 2, 3, 4 days ahead from the flood
    EWS_lev = {'EWS_DaysToThreat': [0, 4]}  # days

    uncertainties = []
    levers = []

    for uncert_name in cat_uncert.keys():
        categories = cat_uncert[uncert_name]
        uncertainties.append(CategoricalParameter(uncert_name, categories))

    for uncert_name in Int_uncert.keys():
        uncertainties.append(IntegerParameter(uncert_name, 
                                              Int_uncert[uncert_name][0],
                                              Int_uncert[uncert_name][1]))    

    # RfR levers can be either 0 (not implemented) or 1 (implemented)
    for lev_name in rfr_lev:
        for n in function.planning_steps:
            lev_name_ = '{} {}'.format(lev_name, n)
            levers.append(IntegerParameter(lev_name_, 0, 1))

    # Early Warning System lever
    for lev_name in EWS_lev.keys():
        levers.append(IntegerParameter(lev_name, EWS_lev[lev_name][0],
                                       EWS_lev[lev_name][1]))
    
    for dike in function.dikelist:
        # uncertainties in the form: locationName_uncertaintyName
        for uncert_name in Real_uncert.keys():
            name = "{}_{}".format(dike, uncert_name)
            lower, upper = Real_uncert[uncert_name]
            uncertainties.append(RealParameter(name, lower, upper))

        for uncert_name in cat_uncert_loc.keys():
            name = "{}_{}".format(dike, uncert_name)
            categories = cat_uncert_loc[uncert_name]
            uncertainties.append(CategoricalParameter(name, categories))

        # location-related levers in the form: locationName_leversName
        for lev_name in dike_lev.keys():
            for n in function.planning_steps:
                name = "{}_{} {}".format(dike, lev_name, n)
                levers.append(IntegerParameter(name, dike_lev[lev_name][0],
                                           dike_lev[lev_name][1]))

    # load uncertainties and levers in dike_model:
    dike_model.uncertainties = uncertainties
    dike_model.levers = levers

    # Problem formulations:
    # Outcomes are all costs, thus they have to minimized:
    direction = ScalarOutcome.MINIMIZE

    # 2-objective PF:
    if problem_formulation_id == 0:
        variable_names = []
        variable_names_ = []
        
        for n in function.planning_steps:
            
            variable_names.extend(
                ['{}_{} {}'.format(dike, e, n) for e in [
                  'Expected Annual Damage', 'Dike Investment Costs'] for dike in function.dikelist])

            variable_names_.extend(
                ['{}_{} {}'.format(dike, e, n) for e in [
                  'Expected Number of Deaths'] for dike in function.dikelist])
    
            variable_names.extend(['RfR Total Costs {}'.format(n)])
            variable_names.extend(['Expected Evacuation Costs {}'.format(n)])

        dike_model.outcomes = [ScalarOutcome('All Costs',
                                             variable_name=[
                                                 var for var in variable_names],
                                             function=sum_over, kind=direction),

                               ScalarOutcome('Expected Number of Deaths',
                                             variable_name=[var for var in variable_names_
                                             ], function=sum_over, kind=direction)]

    # 3-objectives PF:
    elif problem_formulation_id == 1:
        variable_names = []
        variable_names_ = []
        variable_names__ = []
        
        for n in function.planning_steps:
            variable_names.extend(['{}_Expected Annual Damage {}'.format(dike, n)
                                         for dike in function.dikelist])
    
            variable_names_.extend(['{}_Dike Investment Costs {}'.format(dike, n)
                                    for dike in function.dikelist] + [
                                  'RfR Total Costs {}'.format(n)
                                   ] + ['Expected Evacuation Costs {}'.format(n)])
    
            variable_names__.extend(['{}_Expected Number of Deaths {}'.format(dike, n)
                                         for dike in function.dikelist])

            
        dike_model.outcomes = [
                    ScalarOutcome('Expected Annual Damage',
                          variable_name=[var for var in variable_names],
                          function=sum_over, kind=direction),

                ScalarOutcome('Total Investment Costs',
                          variable_name=[var for var in variable_names_],
                          function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths',
                          variable_name=[var for var in variable_names__],
                          function=sum_over, kind=direction)]

    # 5-objectives PF:
    elif problem_formulation_id == 2:
        variable_names = []
        variable_names_ = []
        variable_names__ = []        
        variable_names___ = []
        variable_names____ = []
        
        for n in function.planning_steps:
            variable_names.extend(['{}_Expected Annual Damage {}'.format(dike, n)
                                         for dike in function.dikelist])
            variable_names_.extend(['{}_Dike Investment Costs {}'.format(dike, n)
                                      for dike in function.dikelist])
            variable_names__.extend(['RfR Total Costs {}'.format(n)])       
            variable_names___.extend(['Expected Evacuation Costs {}'.format(n)])
            variable_names____.extend(['{}_Expected Number of Deaths {}'.format(dike, n)
                                         for dike in function.dikelist])

        dike_model.outcomes = [
                    ScalarOutcome('Expected Annual Damage',
                          variable_name=[var for var in variable_names],
                          function=sum_over, kind=direction),

                ScalarOutcome('Dike Investment Costs',
                          variable_name=[var for var in variable_names_],
                          function=sum_over, kind=direction),

                ScalarOutcome('RfR Investment Costs',
                          variable_name=[var for var in variable_names__],
                          function=sum_over, kind=direction),
                
                ScalarOutcome('Evacuation Costs',
                          variable_name=[var for var in variable_names___],
                          function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths',
                          variable_name=[var for var in variable_names____],
                          function=sum_over, kind=direction)]

    # Disaggregate over locations:
    elif problem_formulation_id == 3:
        outcomes = []
        
        for dike in function.dikelist:
            variable_name = []
            for e in ['Expected Annual Damage', 'Dike Investment Costs']:
                variable_name.extend(['{}_{} {}'.format(dike, e, n)
                                          for n in function.planning_steps])
            
            outcomes.append(ScalarOutcome('{} Total Costs'.format(dike),
                                          variable_name=[var for var in variable_name],
                                          function=sum_over, kind=direction))

            outcomes.append(ScalarOutcome('{}_Expected Number of Deaths'.format(dike),
                                          variable_name=['{}_Expected Number of Deaths {}'.format(
                                                  dike, n) for n in function.planning_steps],
                                          function=sum_over, kind=direction))

        outcomes.append(ScalarOutcome('RfR Total Costs', 
                                      variable_name=['RfR Total Costs {}'.format(n
                                                     ) for n in function.planning_steps],
                                          function=sum_over, kind=direction))
        outcomes.append(ScalarOutcome('Expected Evacuation Costs', 
                                      variable_name=['Expected Evacuation Costs {}'.format(n
                                                     ) for n in function.planning_steps],
                                          function=sum_over, kind=direction))

        dike_model.outcomes = outcomes

    # Disaggregate over time:
    elif problem_formulation_id == 4:
        outcomes = []

        for n in function.planning_steps:
            for dike in function.dikelist:
    
                outcomes.append(ScalarOutcome('Expected Annual Damage {}'.format(n),
                                variable_name=['{}_Expected Annual Damage {}'.format(dike,n)
                                                for dike in function.dikelist],
                                function=sum_over, kind=direction))
            
                outcomes.append(ScalarOutcome('Dike Investment Costs {}'.format(n),
                                variable_name=['{}_Dike Investment Costs {}'.format(dike,n)
                                                for dike in function.dikelist],
                                          function=sum_over, kind=direction))

                outcomes.append(ScalarOutcome('Expected Number of Deaths {}'.format(n),
                               variable_name=['{}_Expected Number of Deaths {}'.format(dike,n)
                                                for dike in function.dikelist],
                                          function=sum_over, kind=direction))

            outcomes.append(ScalarOutcome('RfR Total Costs {}'.format(n),
                                          kind=direction))
            outcomes.append(ScalarOutcome('Expected Evacuation Costs {}'.format(n),
                                          kind=direction))

        dike_model.outcomes = outcomes
        
    # Fully disaggregated:
    elif problem_formulation_id == 5:
        outcomes = []

        for n in function.planning_steps:
            for dike in function.dikelist:
                for entry in ['Expected Annual Damage', 'Dike Investment Costs',
                          'Expected Number of Deaths']:
                    
                    o = ScalarOutcome('{}_{} {}'.format(dike, entry, n), kind=direction)
                    outcomes.append(o)

            outcomes.append(ScalarOutcome('RfR Total Costs {}'.format(n), kind=direction))
            outcomes.append(ScalarOutcome('Expected Evacuation Costs {}'.format(n), kind=direction))
        dike_model.outcomes = outcomes
        
    else:
        raise TypeError('unknownx identifier')
        
    return dike_model, function.planning_steps

if __name__ == '__main__':
    get_model_for_problem_formulation(3)