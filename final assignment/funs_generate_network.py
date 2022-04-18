from __future__ import division, unicode_literals, print_function

import numpy as np
import networkx as nx
import pandas as pd
from funs_dikes import Lookuplin  # @UnresolvedImport


def to_dict_dropna(data):
    return dict((str(k), v.dropna().to_dict())
                for k, v in data.iteritems())


def get_network(plann_steps_max=10):
    ''' Build network uploading crucial parameters '''

    # Upload dike info
    df = pd.read_excel('./data/dikeIjssel.xlsx', dtype=object)
    df = df.set_index('NodeName')

    nodes = df.to_dict('index')

    # Create network out of dike info
    G = nx.MultiDiGraph()
    for key, attr in nodes.items():
        G.add_node(key, **attr)

    # Select dike type nodes
    branches = df['branch'].dropna().unique()
    dike_list = df['type'][df['type'] == 'dike'].index.values
    dike_branches = {k: df[df['branch'] == k].index.values
                     for k in branches}

    # Upload fragility curves:
    frag_curves = pd.read_excel('./data/fragcurves/frag_curves.xlsx',
                                header=None, index_col=0).transpose()
    calibration_factors = pd.read_excel('./data/fragcurves/calfactors_pf1250.xlsx',
                                        index_col=0)

    # Upload room for the river projects:
    steps = np.array(range(plann_steps_max))
    
    projects = pd.read_excel('./data/rfr_strategies.xlsx', index_col=0,
                            names=['project name', 0, 1, 2, 3, 4])
    
    for n in steps:
        a = to_dict_dropna(projects)
        
        G.add_node('RfR_projects {}'.format(n), **a)
        G.nodes['RfR_projects {}'.format(n)]['type'] = 'measure'

        G.add_node('discount rate {}'.format(n), **{'value': 0})

    # Upload evacuation policies:
    G.add_node('EWS', **pd.read_excel('./data/EWS.xlsx').to_dict())
    G.nodes['EWS']['type'] = 'measure'

    # Upload muskingum params:
    Muskingum_params = pd.read_excel('./data/Muskingum/params.xlsx',
                                     index_col=0)

    # Fill network with crucial info:
    for dike in dike_list:
        # Assign fragility curves, assuming it's the same shape for every
        # location
        dikeid = 50001010
        G.nodes[dike]['f'] = np.column_stack((frag_curves.loc[:, 'wl'].values,
                                             frag_curves.loc[:, dikeid].values))
        # Adjust fragility curves
        G.nodes[dike]['f'][:, 0] += calibration_factors.loc[dike].values

        # Determine the level of the dike
        G.nodes[dike]['dikelevel'] = Lookuplin(G.nodes[dike]['f'], 1, 0, 0.5)

        # Assign stage-discharge relationships
        filename = './data/rating_curves/{}_ratingcurve_new.txt'.format(dike)
        G.nodes[dike]['r'] = np.loadtxt(filename)

        # Assign losses per location:
        name = './data/losses_tables/{}_lossestable.xlsx'.format(dike)
        G.nodes[dike]['table'] = pd.read_excel(name, index_col=0).values

        # Assign Muskingum paramters:
        G.nodes[dike]['C1'] = Muskingum_params.loc[G.nodes[dike]['prec_node'], 'C1']
        G.nodes[dike]['C2'] = Muskingum_params.loc[G.nodes[dike]['prec_node'], 'C2']
        G.nodes[dike]['C3'] = Muskingum_params.loc[G.nodes[dike]['prec_node'], 'C3']
            
    # The plausible 133 upstream wave-shapes:
    G.nodes['A.0']['Qevents_shape'] = pd.read_excel(
        './data/hydrology/wave_shapes.xls', index_col=0)

    return G, dike_list, dike_branches, steps
