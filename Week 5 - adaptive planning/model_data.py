'''
Created on 19 Feb 2013

@author: jhkwakkel
'''
import numpy as np

RFR = ['RfR Side channel', 'RfR Small Scale', 'RfR Medium Scale', 'RfR Large Scale']
DIKE = ['Dike 1:500 +0.5m', 'Dike 1:500 extr.', 'Dike 1:1000', 'Dike 1:1000 extr.', 'Dike 2nd Q x 1.5']
COOP = ['Coop Small', 'Coop Medium', 'Coop Large']
DC = ['DC Elevated', 'DC Dikes', 'DC Mounts', 'DC Floating']
CD = ['Dike Climate dikes', 'Dike Wave resistant'] 

SMALL = "small"
LARGE = "large"
XLARGE = "xlarge"

rules = [SMALL, LARGE, XLARGE]

bindings = {r"ClimScenS": r"5",
            r'LandUseScA': r'NoChange\landuse',
            r"LandUseScen" : r"rundir\Land00_2.pcr",
            r"LandUseRvR" : r"rundir\Land00_2.pcr",
            r"LandRnd" : r"0",
            r"FltHouse" : r"0",
            r"StHouse" : r"0",
            r"StadHa" : r"0",
            r"NatHa" : r"0",
            r"GlasbHa" : r"0",
            r"RecreHa" : r"0",
            r"DEMini" : r"rundir\dem7.pcr",
            r"DEMdijk" : r"rundir\dem7.pcr",
            r"DEMriv" : r"rundir\DEMriver3.pcr",
            r"DEMterp" : r"rundir\dem7.pcr",
            r"Terp" : r"0",
            r"maxQLob" : r"30000",
            r"DredgeQ" : r"-1",
            r"DredgeDepth" : r"-1",
            r"RvR" : r"0",
            r"OphoogQ" : r"0",
            r"OphoogMHW" : r"0",
            r"Ophoog1" : r"0",
            r"Ophoog2" : r"0",
            r"Ophoog3" : r"0",
            r"Ophoog4" : r"0",
            r"Ophoog5" : r"0",
            r"SupDijk" : r"0",
            r"FragTbl" : r"rundir\FragTab01lsm.tbl",
            r"DamFunctTbl" : r"rundir\damfunction.tbl",
            r"ShipTbl" : r"rundir\shiptype3.tbl",
            r"MHW" : r"rundir\mhw00new.txt",
            r"MHWFactor" : r"1",
            r"AlarmValue" : r"40",
            r"AlarmEdu" : r"0",
            r"ImplDuur" : r"0",
            r"timebegin" : r"1",
            r"timeend" : r"100"}

ordering = [ r"ClimScenS",
             r'LandUseScA',
             r"LandUseScen",
             r"LandUseRvR",
             r"LandRnd",
             r"FltHouse",
             r"StHouse",
             r"StadHa",
             r"NatHa",
             r"GlasbHa",
             r"RecreHa",
             r"DEMini",
             r"DEMdijk",
             r"DEMriv",
             r"DEMterp",
             r"Terp",
             r"maxQLob",
             r"DredgeQ",
             r"DredgeDepth",
             r"RvR",
             r"OphoogQ",
             r"OphoogMHW",
             r"Ophoog1",
             r"Ophoog2",
             r"Ophoog3",
             r"Ophoog4",
             r"Ophoog5",
             r"SupDijk",
             r"FragTbl",
             r"DamFunctTbl",
             r"ShipTbl",
             r"MHW",
             r"MHWFactor",
             r"AlarmValue",
             r"AlarmEdu",
             r"ImplDuur",
             r"timebegin",
             r"timeend"]

# column 0 is the timestep, so column number and scenario number correspond
# i.e. scenario 1 is column 1

dike_costs = {'Dike 1:500 +0.5m':np.loadtxt(r'./model/data/1 in 500.txt'), 
              'Dike 1:500 extr.':np.tile(np.loadtxt(r'./model/data/1 in 500.txt')[:, 28], (31, 1) ).T, 
              'Dike 1:1000':np.loadtxt(r'./model/data/1 in 1000.txt'), 
              'Dike 1:1000 extr.':np.tile(np.loadtxt(r'./model/data/1 in 1000.txt')[:, 28], (31, 1) ).T, 
              'Dike 2nd Q x 1.5':np.loadtxt(r'./model/data/1-5 times extreme.txt')}

measure_costs = {'Dike Climate dikes':1000,
                 'Dike Wave resistant':125,
                 'RfR Side channel':50,
                 'RfR Small Scale':70,
                 'RfR Medium Scale':138,
                 'RfR Large Scale':269,
                 'Coop Small':0.03,
                 'Coop Medium':0.06,
                 'Coop Large':0.09,
                 'DC Floating':6.15,
                 'DC Dikes':600,
                 'DC Mounts':1006,
                 'DC Elevated':1000,
                 'Alarm Early':0.03,
                 'Alarm Late':0.03,
                 'Alarm Education':0.03,
                 'no policy': 0}
