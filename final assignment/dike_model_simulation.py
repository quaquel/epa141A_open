from ema_workbench import Model, MultiprocessingEvaluator, Policy, Scenario

from ema_workbench.em_framework.evaluators import perform_experiments
from ema_workbench.em_framework.samplers import sample_uncertainties
from ema_workbench.util import ema_logging
import time
from problem_formulation import get_model_for_problem_formulation


if __name__ == "__main__":
    ema_logging.log_to_stderr(ema_logging.INFO)

    dike_model, planning_steps = get_model_for_problem_formulation(5)

    # Build a user-defined scenario and policy:
    reference_values = {
        "Bmax": 175,
        "Brate": 1.5,
        "pfail": 0.5,
        "ID flood wave shape": 4,
        "planning steps": 2,
    }
    reference_values.update({f"discount rate {n}": 3.5 for n in planning_steps})
    scen1 = {}

    for key in dike_model.uncertainties:
        name_split = key.name.split("_")

        if len(name_split) == 1:
            scen1.update({key.name: reference_values[key.name]})

        else:
            scen1.update({key.name: reference_values[name_split[1]]})

    ref_scenario = Scenario("reference", **scen1)

    # no dike increase, no warning, none of the rfr
    zero_policy = {"DaysToThreat": 0}
    zero_policy.update({f"DikeIncrease {n}": 0 for n in planning_steps})
    zero_policy.update({f"RfR {n}": 0 for n in planning_steps})
    pol0 = {}

    for key in dike_model.levers:
        s1, s2 = key.name.split("_")
        pol0.update({key.name: zero_policy[s2]})

    policy0 = Policy("Policy 0", **pol0)

    # Call random scenarios or policies:
    #    n_scenarios = 5
    #    scenarios = sample_uncertainties(dike_model, 50)
    #    n_policies = 10

    # single run
    #    start = time.time()
    #    dike_model.run_model(ref_scenario, policy0)
    #    end = time.time()
    #    print(end - start)
    #    results = dike_model.outcomes_output

    # series run
    experiments, outcomes = perform_experiments(dike_model, ref_scenario, 5)

# multiprocessing
#    with MultiprocessingEvaluator(dike_model) as evaluator:
#        results = evaluator.perform_experiments(scenarios=10, policies=policy0,
#                                                uncertainty_sampling='sobol')
