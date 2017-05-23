'''


'''
from __future__ import (unicode_literals, print_function, absolute_import,
                                        division)

from ema_workbench import (RealParameter, IntegerParameter, ema_logging,
                           ScalarOutcome, CategoricalParameter)

from model_interface import WaasModel, SMALL, LARGE, XLARGE  # @UnresolvedImport
from ema_workbench.em_framework.parameters import Policy
from ema_workbench.em_framework.evaluators import (MultiprocessingEvaluator, SequentialEvaluator,
                                                   perform_experiments, PFF)
from ema_workbench.util.utilities import save_results
# Created on 1 Apr 2017
#
# .. codeauthor::jhkwakkel <j.h.kwakkel (at) tudelft (dot) nl>

policies = [{'params': {'RvR': '1', 'LandUseRvR': 'rundir\\landuservrsmall.pcr'}, 'name': 'RfR Small Scale'}, 
            {'params': {'RvR': '2', 'LandUseRvR': 'rundir\\landuservrmed.pcr'}, 'name': 'RfR Medium Scale'}, 
            {'params': {'RvR': '3', 'LandUseRvR': 'rundir\\landuservrlarge.pcr'}, 'name': 'RfR Large Scale'}, 
            {'params': {'RvR': '4', 'LandUseRvR': 'rundir\\landuservrnev.pcr'}, 'name': 'RfR Side channel'}, 
            {'params': {'MHW': 'rundir\\MHW500new.txt', 'MHWFactor': '1', 'DEMdijk': 'rundir\\dem7.pcr', 'OphoogMHW': '0.5'}, 'name': 'Dike 1:500 +0.5m'}, 
            {'params': {'MHW': 'rundir\\MHW00new.txt', 'MHWFactor': '1', 'DEMdijk': 'rundir\\demlijn.pcr', 'OphoogMHW': '0'}, 'name': 'Dike 1:500 extr.'}, 
            {'params': {'MHW': 'rundir\\MHW1000new.txt', 'MHWFactor': '1', 'DEMdijk': 'rundir\\dem7.pcr', 'OphoogMHW': '0.5'}, 'name': 'Dike 1:1000'}, 
            {'params': {'MHW': 'rundir\\MHW00new.txt', 'MHWFactor': '1', 'DEMdijk': 'rundir\\demq20000.pcr', 'OphoogMHW': '0'}, 'name': 'Dike 1:1000 extr.'}, 
            {'params': {'MHW': 'rundir\\MHW500jnew.txt', 'MHWFactor': '1.5', 'DEMdijk': 'rundir\\dem7.pcr', 'OphoogMHW': '0.5'}, 'name': 'Dike 2nd Q x 1.5'}, 
            {'params': {'FragTbl': 'rundir\\FragTab50lsmSD.tbl'}, 'name': 'Dike Climate dikes'}, 
            {'params': {'FragTbl': 'rundir\\FragTab50lsm.tbl'}, 'name': 'Dike Wave resistant'}, 
            {'params': {'maxQLob': '20000'}, 'name': 'Coop Small'}, 
            {'params': {'maxQLob': '18000'}, 'name': 'Coop Medium'}, 
            {'params': {'maxQLob': '14000'}, 'name': 'Coop Large'}, 
            {'params': {'DamFunctTbl': 'rundir\\damfunctionpalen.tbl', 'DEMterp': 'rundir\\dem7.pcr', 'StHouse': '0', 'FltHouse': '0', 'Terp': '0'}, 'name': 'DC Elevated'}, 
            {'params': {'DamFunctTbl': 'rundir\\damfunction.tbl', 'DEMterp': 'rundir\\demdikelcity.pcr', 'StHouse': '0', 'FltHouse': '0', 'Terp': '0'}, 'name': 'DC Dikes'}, 
            {'params': {'DamFunctTbl': 'rundir\\damfunction.tbl', 'DEMterp': 'rundir\\demterpini.pcr', 'StHouse': '0', 'FltHouse': '0', 'Terp': '1'}, 'name': 'DC Mounts'}, 
            {'params': {'DamFunctTbl': 'rundir\\damfunctiondrijf.tbl', 'DEMterp': 'rundir\\dem7.pcr', 'StHouse': '0', 'FltHouse': '0', 'Terp': '0'}, 'name': 'DC Floating'},
            {'params': {'AlarmValue': 20}, 'name': 'Alarm Early'},
            {'params': {}, 'name': 'no policy'},
            {'params': {'AlarmEdu': 1}, 'name': 'Alarm Education'}
            ]

if __name__ == '__main__':
    ema_logging.log_to_stderr(ema_logging.INFO)
    
    waas_model = WaasModel("waasmodel", wd='./model')
    waas_model.uncertainties = [IntegerParameter("climate scenarios", 1, 30, 
                                                 pff=True, resolution=[x for x in range(1, 31)]),
                                RealParameter("fragility dikes", -0.1, 0.1),
                                RealParameter("DamFunctTbl", -0.1, 0.1),
                                RealParameter("ShipTbl1", -0.1, 0.1),
                                RealParameter("ShipTbl2", -0.1, 0.1),
                                RealParameter("ShipTbl3", -0.1, 0.1),
                                RealParameter("collaboration",1, 1.6),
                                CategoricalParameter("land use scenarios", 
                                  ["NoChange", "moreNature", "Deurbanization",
                                   "sustainableGrowth", "urbanizationDeurbanization",
                                   "urbanizationLargeAndFast", "urbanizationLargeSteady"],
                                                       pff=True)]
    
    waas_model.outcomes = [ScalarOutcome("Flood damage (Milj. Euro)"),
                           ScalarOutcome("Number of casualties"),
                           ScalarOutcome("Costs"),
                           ScalarOutcome("Timing")]
    
    n_scenarios = 500
    policies = [Policy(kwargs['name'], **kwargs['params']) for kwargs in policies]
    
    with MultiprocessingEvaluator(waas_model) as evaluator:
    # with SequentialEvaluator(waas_model) as evaluator:
        results = perform_experiments(waas_model, n_scenarios, policies, 
                                      evaluator=evaluator)
        
    save_results(results, './data/partial factorial over pathways.tar.gz')