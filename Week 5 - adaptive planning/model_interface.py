'''
Created on 21 jan. 2015

@author: LocalAdmin
'''
import os
import subprocess
import tempfile

from ema_workbench import (RealParameter, IntegerParameter, ema_logging,
                           EMAError, ScalarOutcome, CategoricalParameter)
from ema_workbench.em_framework.model import FileModel, SingleReplication
from ema_workbench.util.ema_exceptions import CaseError

from model_data import *
 
class WaasModel(SingleReplication, FileModel):
    step_size = 5
    postion_on_path = 0
    
    #helper attribute mapping outcome name to files
    _outcomeFiles = {"Flood damage (Milj. Euro)": r'DamSumMeur.tss',
                     r"% of non-navigable time": "DamShipProcent.tss",
                      "Nature area": "Summary.asc",
                      "Number of casualties": "cassum.tss",
                      "Number of floods": "floodnumber.tss"}
    def __init__(self, name, wd):
        super(WaasModel, self).__init__(name, wd=wd, 
                                        model_file="RAMImiSUI_final.mod")
    
    
    def model_init(self, policy):
        super(WaasModel, self).model_init(policy)
       
        #change the working directory to the working directory
        ema_logging.debug("changing dir")
        os.chdir(self.working_directory)
        
        self.pathway = self.policy
        
        self.reset_model()

    def run_experiment(self, experiment):
        #make empty outcomes
        for outcome in self.outcomes:
            name = outcome.name
            self.output[name] = np.zeros((100,))
        
        # make input file
        bindings = self._make_binding(experiment)
        
        # make the tables
        self._make_damfact(experiment)
        self._make_shiptbl(experiment)
        self._make_fragtbl(experiment, bindings)
        
        #run model
        steps = [(x, x+self.step_size-1) for x in\
                 range(1,101-self.step_size, self.step_size)]
        if not steps:
            steps = [(1,100)]
        if steps[-1][1]<100:
            steps.append((steps[-1][1],100))
        elif steps[-1][1]>100:
            raise EMAError("steps defined incorrectly")

        for entry in steps:
            return_code = self._run(experiment, entry)

            #check if everything performed correctly
            if return_code != 0:
                #something went wrong
                for outcome in self.outcomes:
                    #make an empty return value, the 100 is conditions on the runtime
                    #this also assumes all outcomes are time series
                    self.output[outcome.name] = np.zeros((entry[1]-entry[0]+1,))
                raise CaseError("run not completed", experiment, self.policy)
            else:
                self.time = entry[1]
                self._parse_output(entry)
                self._evaluate_performance(entry)
        
 
        output = {}
        
        output["Costs"] = self._determine_costs(experiment)
        output["Flood damage (Milj. Euro)"] = np.sum(self.output["Flood damage (Milj. Euro)"])
        output["Number of casualties"] = np.sum(self.output["Number of casualties"])
        output["Timing"] = [entry[1] for entry in self.timing]
        
        while len(self.output["Timing"])<3:
            output["Timing"].append(100)
        
        return output


    def reset_model(self):
        """
        Method for reseting the model to its initial state. The default
        implementation only sets the outputs to an empty dict. 

        """
        super(WaasModel, self).reset_model()
        self.postion_on_path = 0
        self.timing = []
        self.time = 1
#         self.policy = 
#         self.policy["name"] = self.pathway.name    
        self._update_pathway()

    def _determine_costs(self, case):
        timing = self.timing
        
        # for each action
        # for a given duration
        # get costs
        duration = []
        policies = {}
        for i in range(len(timing)):
            a = timing[i]
            policies[a[0]] = i
            try:
                b = timing[i+1][1]
            except IndexError:
                b = 101
            duration.append((a[0], a[1], b-1))
        
        # duration of dikes aanpassen
        # which dike measures do we have on the path
        dop = set(DIKE).intersection(policies.keys())
        costs = 0
        
        if len(dop) == 1:
            index = policies[dop.pop()]
            entry = duration[index]
            entry = (entry[0], 1, 100)
            duration[index] = entry 
            
            costs = dike_costs[entry[0]]
            costs = np.sum(costs[:, case['climate scenarios'] ])
        elif len(dop)==2:
            indices = sorted([policies[entry] for entry in dop])
            index = indices[0]
            entry = duration[index]
            entry = (entry[0], 1, duration[indices[1]][1]-1)
            duration[index] = entry
            
            entry = duration[indices[-1]]
            dike = entry[0]
            data  = dike_costs[dike]
            costs = np.sum(data[:, case['climate scenarios']])
        elif len(dop)==3: 
            # three dike actions in a row
            entry = duration[-1]
            dike = entry[0]
            data  = dike_costs[dike]
            costs = np.sum(data[:, case['climate scenarios']])
    
        for entry in duration:
            policy = entry[0]
            if policy not in DIKE:
                costs += measure_costs[policy]
        
        return costs
        

    def _evaluate_performance(self, time_interval):
        casualties = self.output["Number of casualties"][0:time_interval[1]]
        costs = self.output['Flood damage (Milj. Euro)'][0:time_interval[1]]
        
        # threshold defaults
        cas_threshold = 20
        cost_threshold = 1500
        
        #duration of lookback defaults
        lookback_small = 2
        lookback_long = 9
        lookback_large = 14
        
        #determine small events
        small_events = np.zeros(casualties.shape)
        small_events[((casualties > 0) & (casualties < cas_threshold)) &\
                     ((costs>0)&(costs<cost_threshold))] = 1 
        
        #determine large events
        large_events = np.zeros(casualties.shape)
        large_events[(casualties >= cas_threshold) | (costs>=cost_threshold)] = 1
        
        #additional large events due to two events in 3 years
        events = small_events + large_events 
        assert np.any(events>1)==False
        
        timing_events = np.where(events==1)[0]
        for entry in timing_events:
            prior_events = small_events[max(0, entry-lookback_small):entry]+\
                           large_events[max(0, entry-lookback_small):entry]
            if np.sum(prior_events)>0:
                large_events[entry]=1
                small_events[entry]=0
                
        #additional large events due to three events in 10 years
        events = small_events + large_events 
        assert np.any(events>1)==False
        
        timing_events = np.where(events==1)[0]
        for entry in timing_events:
            prior_events = small_events[max(0, entry-lookback_long):entry]+\
                           large_events[max(0, entry-lookback_long):entry]
            if np.sum(prior_events)>1:
                large_events[entry]=1
                small_events[entry]=0
        
        #determine xl events
        xlarge_events = np.zeros(casualties.shape)
        timing_events = np.where(large_events==1)[0]
        temp_large_events = np.copy(large_events)
        for entry in timing_events:
            prior_events = large_events[max(0, entry-lookback_large):entry]
            if np.sum(prior_events)>0:
                xlarge_events[entry]=1
                temp_large_events[entry]=0
        large_events = temp_large_events
        
        #look back over the step size
        start_interval = time_interval[0]-1
        re_s = small_events[start_interval::]
        re_l = large_events[start_interval::]
        re_xl = xlarge_events[start_interval::]
        
        #apply specified rule
        next_action = False
        
        try:
            if self.rule == SMALL:
                next_action = np.any(re_s==1)
            elif self.rule == LARGE:
                next_action = np.any(re_l==1)
            elif self.rule == XLARGE:
                next_action = np.any(re_xl==1)
            else:
                raise EMAError("rule not specified correctly, should be one of\
                                small, medium, or large")
        except AttributeError:
            ema_logging.debug('no rule specified')
        
        if next_action:
            self._update_pathway()

    def _run(self, case, entry):
        command = r'pcrcalc -f RAMImiSUI_final.mod -b bindings.txt %d %d %s' % (entry[0],
                                       entry[1], case["climate scenarios"])  
        
        # run model and process results
        file_object = tempfile.TemporaryFile()
        
        ema_logging.debug("executing %s" % command)
        return_code = subprocess.Popen(command, stderr=file_object, shell=True).wait()
#        return_code = subprocess.Popen(command).wait()
        file_object.close()
        return return_code

    def _make_shiptbl(self, case):
        for i in range(1,4):
            param = case.get("ShipTbl"+str(i))
            basic_file_name = "shiptype"+str(i)+".tbl"
            basic_file = open(self.working_directory+"\\Input\\"+basic_file_name, 'r')
            new_file = open(self.working_directory+r"\\rundir\\"+basic_file_name, 'w')
            
            for line in basic_file:
                elements = line.strip()
                elements = line.split()
                if elements:
                    candidate_value = float(elements[-1])*(1+param)
                    candidate_value= max((candidate_value, 0))
                    candidate_value = min((candidate_value, 1))
                    elements[-1] = str(candidate_value)
                        
                    line = " ".join(elements)
                    new_file.write(line+"\n")
            basic_file.close()
            new_file.close()
            ema_logging.debug("made "+basic_file_name)
    
    def _make_fragtbl(self, case, bindings):
        param = case.get("fragility dikes")
        basic_file_name = bindings.get('FragTbl').split('\\')[1]
        
        basic_file = open(self.working_directory+"\\Input\\"+basic_file_name, 'r')
        new_file = open(self.working_directory+r"\\rundir\\"+basic_file_name, 'w')

        for line in basic_file:
            elements = line.strip()
            elements = line.split()
            if elements:
                candidate_value = float(elements[-1])*(1+param)
                candidate_value= max((candidate_value, 0))
                candidate_value = min((candidate_value, 1))
                elements[-1] = str(candidate_value)
                elements = "\t".join(elements)
                new_file.write(elements+"\n")
        basic_file.close()
        new_file.close()
    
    def _make_damfact(self, case):
        basic_file_name = "damfact.tbl"
        basic_file = open(self.working_directory+r"\\Input\\"+basic_file_name, "r")
        output_file = open(self.working_directory+r"\Rundir\\"+basic_file_name, 'w')
        
        param = case.get(("DamFunctTbl"))
        
        for line in basic_file:
            elements = line.strip()
            elements = line.split()
            if elements:
                candidate_value = float(elements[-1])*(1+param)
                candidate_value= max((candidate_value, 0))
                candidate_value = min((candidate_value, 1))
                elements[-1] = str(candidate_value)

                elements = " ".join(elements)
                output_file.write(elements+"\n")
        basic_file.close()
        output_file.close()
        ema_logging.debug("made damfact.tbl")
    
    def _make_binding(self, case):
        ema_logging.debug("making binding.txt")
        
        # write the bindings.txt file
        bindings_file = open(r'%s\bindings.txt' % (self.working_directory), 'w')
        
        bindingDict = {}
        
        for entry in ordering:
            value = self.policy.get("params")
            try:
                value = value[entry]
            except KeyError:
                value = bindings.get(entry)
            bindingDict[entry] = value
        
        bindingDict["ClimScenS"] = case["climate scenarios"]
        bindingDict[r'LandUseScA'] = case["land use scenarios"]+r"\landuse"
        bindingDict["maxQLob"] = bindingDict["maxQLob"] * case["collaboration"] 
                
        for entry in ordering:
            value = bindingDict.get(entry)
            bindings_file.write(entry+" = " + str(value)+";\n")
        bindings_file.close()   
        ema_logging.debug("bindings created")
        return bindingDict
    
    def _parse_output(self, entry):
        for outcome in self.outcomes:
            name = outcome.name
            ema_logging.debug("parsing outcome %s" % (name))
            try:
                data_file = self._outcomeFiles[name]
            except KeyError:
                ema_logging.debug("no parsing function defined for {}".format(name))
                continue
            
            result = self._parsing_methods[name](self,data_file)
            try:
                result =  result[entry[0]-1::]
                self.output[name][entry[0]-1:entry[1]] = result
            except ValueError:
                print(entry, name)
        ema_logging.debug("outcomes parsed")

    def _parse_timesereries(self, data_file):
        ema_logging.debug("trying to open %s" %(os.path.abspath('rundir\%s' %(data_file))))
        data_file = open(os.path.abspath('rundir\%s' % (data_file)))
        data = data_file.readlines()
        data_file.close()
        data = data[4::]
        data = [entry.replace('1.#INF', '0') for entry in data]
        data = [entry.strip() for entry in data]
        data = [entry.split() for entry in data]
        data = [float(entry[1]) for entry in data]
        data = np.asarray(data)
        data[data==1e31] = 0
        
        return np.asarray(data)
    
    def _update_pathway(self):
        def update_policy(policy):
            params = policy["params"]
            
            for key, value in params.items():
                self.policy["params"][key] = value
        
        def same_type(aia, a_list):
            for entry in aia:
                if entry in a_list:
                    return entry
            return None
        
        self.postion_on_path+=1
        try:
#            print 'action_%s' % (self.postion_on_path)
            next_policy = self.pathway['action_%s' % (self.postion_on_path)]
            policy_name = next_policy["name"]
            self.timing.append((policy_name, self.time))
            
            #already implemented actions
            aia = [self.pathway['action_%s'% (i)] for i in range(1, self.postion_on_path) ]
            aia = [entry["name"] for entry in aia]
                
            if aia:
                if policy_name in RFR and same_type(aia, RFR):
                    if RFR.index(policy_name) > RFR.index(same_type(aia, RFR)):
                        update_policy(next_policy)
                elif policy_name in DIKE and same_type(aia, DIKE):
                    if DIKE.index(policy_name) > DIKE.index(same_type(aia, DIKE)):
                        update_policy(next_policy)
                elif policy_name in COOP and same_type(aia, COOP):
                    if COOP.index(policy_name) > COOP.index(same_type(aia, COOP)):
                        update_policy(next_policy)
                elif policy_name in DC and same_type(aia, DC):
                    pass
                elif policy_name in CD and same_type(aia, CD):
                    pass
                else:
                    update_policy(next_policy)
            else:
                update_policy(next_policy)
 
 
            try:
                self.rule = self.pathway['rule_%s' % (self.postion_on_path) ]
            except KeyError:
                ema_logging.debug("no rule specified")
        except KeyError:
            ema_logging.debug("end of pathway has been reached")
    
    #helper attribute mapping outcome name to parser function
    _parsing_methods = {"Flood damage (Milj. Euro)": _parse_timesereries,
                        "Number of casualties": _parse_timesereries,
                        }
    
