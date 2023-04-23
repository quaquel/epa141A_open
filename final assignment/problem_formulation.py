"""
Created on Wed Mar 21 17:34:11 2018

@author: ciullo
"""
from ema_workbench import (
    Model,
    CategoricalParameter,
    ArrayOutcome,
    ScalarOutcome,
    IntegerParameter,
    RealParameter,
)
from dike_model_function import DikeNetwork  # @UnresolvedImport

import numpy as np


def sum_over(*args):
    numbers = []
    for entry in args:
        try:
            value = sum(entry)
        except TypeError:
            value = entry
        numbers.append(value)

    return sum(numbers)


def sum_over_time(*args):
    data = np.asarray(args)
    summed = data.sum(axis=0)
    return summed


def get_model_for_problem_formulation(problem_formulation_id):
    """Convenience function to prepare DikeNetwork in a way it can be input in the EMA-workbench.
    Specify uncertainties, levers, and outcomes of interest.

    Parameters
    ----------
    problem_formulation_id : int {0, ..., 5}
                             problem formulations differ with respect to the objectives
                             0: Total cost, and casualties
                             1: Expected damages, costs, and casualties
                             2: expected damages, dike investment costs, rfr costs, evacuation cost, and casualties
                             3: costs and casualties disaggregated over dike rings, and room for the river and evacuation costs
                             4: Expected damages, dike investment cost and casualties disaggregated over dike rings and room for the river and evacuation costs
                             5: disaggregate over time and space

    Notes
    -----
    problem formulations 4 and 5 rely on ArrayOutcomes and thus cannot straightforwardly
    be used in optimizations

    """
    # Load the model:
    function = DikeNetwork()
    # workbench model:
    dike_model = Model("dikesnet", function=function)

    # Uncertainties and Levers:
    # Specify uncertainties range:
    Real_uncert = {"Bmax": [30, 350], "pfail": [0, 1]}  # m and [.]
    # breach growth rate [m/day]
    cat_uncert_loc = {"Brate": (1.0, 1.5, 10)}

    cat_uncert = {
        f"discount rate {n}": (1.5, 2.5, 3.5, 4.5) for n in function.planning_steps
    }

    Int_uncert = {"A.0_ID flood wave shape": [0, 132]}
    # Range of dike heightening:
    dike_lev = {"DikeIncrease": [0, 10]}  # dm

    # Series of five Room for the River projects:
    rfr_lev = [f"{project_id}_RfR" for project_id in range(0, 5)]

    # Time of warning: 0, 1, 2, 3, 4 days ahead from the flood
    EWS_lev = {"EWS_DaysToThreat": [0, 4]}  # days

    uncertainties = []
    levers = []

    for uncert_name in cat_uncert.keys():
        categories = cat_uncert[uncert_name]
        uncertainties.append(CategoricalParameter(uncert_name, categories))

    for uncert_name in Int_uncert.keys():
        uncertainties.append(
            IntegerParameter(
                uncert_name, Int_uncert[uncert_name][0], Int_uncert[uncert_name][1]
            )
        )

    # RfR levers can be either 0 (not implemented) or 1 (implemented)
    for lev_name in rfr_lev:
        for n in function.planning_steps:
            lev_name_ = f"{lev_name} {n}"
            levers.append(IntegerParameter(lev_name_, 0, 1))

    # Early Warning System lever
    for lev_name in EWS_lev.keys():
        levers.append(
            IntegerParameter(lev_name, EWS_lev[lev_name][0], EWS_lev[lev_name][1])
        )

    for dike in function.dikelist:
        # uncertainties in the form: locationName_uncertaintyName
        for uncert_name in Real_uncert.keys():
            name = f"{dike}_{uncert_name}"
            lower, upper = Real_uncert[uncert_name]
            uncertainties.append(RealParameter(name, lower, upper))

        for uncert_name in cat_uncert_loc.keys():
            name = f"{dike}_{uncert_name}"
            categories = cat_uncert_loc[uncert_name]
            uncertainties.append(CategoricalParameter(name, categories))

        # location-related levers in the form: locationName_leversName
        for lev_name in dike_lev.keys():
            for n in function.planning_steps:
                name = f"{dike}_{lev_name} {n}"
                levers.append(
                    IntegerParameter(name, dike_lev[lev_name][0], dike_lev[lev_name][1])
                )

    # load uncertainties and levers in dike_model:
    dike_model.uncertainties = uncertainties
    dike_model.levers = levers

    # Problem formulations:
    # Outcomes are all costs, thus they have to minimized:
    direction = ScalarOutcome.MINIMIZE

    # 2-objective PF:
    if problem_formulation_id == 0:
        cost_variables = []
        casualty_variables = []

        cost_variables.extend(
            [
                f"{dike}_{e}"
                for e in ["Expected Annual Damage", "Dike Investment Costs"]
                for dike in function.dikelist
            ]
        )

        casualty_variables.extend(
            [
                f"{dike}_{e}"
                for e in ["Expected Number of Deaths"]
                for dike in function.dikelist
            ]
        )

        cost_variables.extend([f"RfR Total Costs"])
        cost_variables.extend([f"Expected Evacuation Costs"])

        dike_model.outcomes = [
            ScalarOutcome(
                "All Costs",
                variable_name=[var for var in cost_variables],
                function=sum_over,
                kind=direction,
            ),
            ScalarOutcome(
                "Expected Number of Deaths",
                variable_name=[var for var in casualty_variables],
                function=sum_over,
                kind=direction,
            ),
        ]

    # 3-objectives PF:
    elif problem_formulation_id == 1:
        damage_variables = []
        cost_variables = []
        casualty_variables = []

        damage_variables.extend(
            [f"{dike}_Expected Annual Damage" for dike in function.dikelist]
        )

        cost_variables.extend(
            [f"{dike}_Dike Investment Costs" for dike in function.dikelist]
            + [f"RfR Total Costs"]
            + [f"Expected Evacuation Costs"]
        )

        casualty_variables.extend(
            [f"{dike}_Expected Number of Deaths" for dike in function.dikelist]
        )

        dike_model.outcomes = [
            ScalarOutcome(
                "Expected Annual Damage",
                variable_name=[var for var in damage_variables],
                function=sum_over,
                kind=direction,
            ),
            ScalarOutcome(
                "Total Investment Costs",
                variable_name=[var for var in cost_variables],
                function=sum_over,
                kind=direction,
            ),
            ScalarOutcome(
                "Expected Number of Deaths",
                variable_name=[var for var in casualty_variables],
                function=sum_over,
                kind=direction,
            ),
        ]

    # 5-objectives PF:
    elif problem_formulation_id == 2:
        damage_variables = []
        dike_cost_variables = []
        rfr_costs_variables = []
        evac_cost_variables = []
        casuality_varaibles = []

        damage_variables.extend(
            [f"{dike}_Expected Annual Damage" for dike in function.dikelist]
        )
        dike_cost_variables.extend(
            [f"{dike}_Dike Investment Costs" for dike in function.dikelist]
        )
        rfr_costs_variables.extend([f"RfR Total Costs"])
        evac_cost_variables.extend([f"Expected Evacuation Costs"])
        casuality_varaibles.extend(
            [f"{dike}_Expected Number of Deaths" for dike in function.dikelist]
        )

        dike_model.outcomes = [
            ScalarOutcome(
                "Expected Annual Damage",
                variable_name=[var for var in damage_variables],
                function=sum_over,
                kind=direction,
            ),
            ScalarOutcome(
                "Dike Investment Costs",
                variable_name=[var for var in dike_cost_variables],
                function=sum_over,
                kind=direction,
            ),
            ScalarOutcome(
                "RfR Investment Costs",
                variable_name=[var for var in rfr_costs_variables],
                function=sum_over,
                kind=direction,
            ),
            ScalarOutcome(
                "Evacuation Costs",
                variable_name=[var for var in evac_cost_variables],
                function=sum_over,
                kind=direction,
            ),
            ScalarOutcome(
                "Expected Number of Deaths",
                variable_name=[var for var in casuality_varaibles],
                function=sum_over,
                kind=direction,
            ),
        ]

    # Disaggregate over locations:
    elif problem_formulation_id == 3:
        outcomes = []

        for dike in function.dikelist:
            cost_variables = []
            for e in ["Expected Annual Damage", "Dike Investment Costs"]:
                cost_variables.append(f"{dike}_{e}")

            outcomes.append(
                ScalarOutcome(
                    f"{dike} Total Costs",
                    variable_name=[var for var in cost_variables],
                    function=sum_over,
                    kind=direction,
                )
            )

            outcomes.append(
                ScalarOutcome(
                    f"{dike}_Expected Number of Deaths",
                    variable_name=f"{dike}_Expected Number of Deaths",
                    function=sum_over,
                    kind=direction,
                )
            )

        outcomes.append(
            ScalarOutcome(
                "RfR Total Costs",
                variable_name="RfR Total Costs",
                function=sum_over,
                kind=direction,
            )
        )
        outcomes.append(
            ScalarOutcome(
                "Expected Evacuation Costs",
                variable_name="Expected Evacuation Costs",
                function=sum_over,
                kind=direction,
            )
        )

        dike_model.outcomes = outcomes

    # Disaggregate over time:
    elif problem_formulation_id == 4:
        outcomes = []

        outcomes.append(
            ArrayOutcome(
                f"Expected Annual Damage",
                variable_name=[
                    f"{dike}_Expected Annual Damage" for dike in function.dikelist
                ],
                function=sum_over_time,
            )
        )

        outcomes.append(
            ArrayOutcome(
                f"Dike Investment Costs",
                variable_name=[
                    f"{dike}_Dike Investment Costs" for dike in function.dikelist
                ],
                function=sum_over_time,
            )
        )

        outcomes.append(
            ArrayOutcome(
                f"Expected Number of Deaths",
                variable_name=[
                    f"{dike}_Expected Number of Deaths" for dike in function.dikelist
                ],
                function=sum_over_time,
            )
        )

        outcomes.append(ArrayOutcome(f"RfR Total Costs"))
        outcomes.append(ArrayOutcome(f"Expected Evacuation Costs"))

        dike_model.outcomes = outcomes

    # Fully disaggregated:
    elif problem_formulation_id == 5:
        outcomes = []

        for dike in function.dikelist:
            for entry in [
                "Expected Annual Damage",
                "Dike Investment Costs",
                "Expected Number of Deaths",
            ]:

                o = ArrayOutcome(f"{dike}_{entry}")
                outcomes.append(o)

        outcomes.append(ArrayOutcome("RfR Total Costs"))
        outcomes.append(ArrayOutcome("Expected Evacuation Costs"))
        dike_model.outcomes = outcomes

    else:
        raise TypeError("unknown identifier")

    return dike_model, function.planning_steps


if __name__ == "__main__":
    get_model_for_problem_formulation(3)
