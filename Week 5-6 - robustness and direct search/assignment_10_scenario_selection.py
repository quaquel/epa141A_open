"""
Scenario selection based on maximizing diversity as proposed in Eker & Kwakkel

This code is adapted from the source found in the github repository belonging to the paper. The first change
is to bring the code in line with the latest version of the workbench. The second change solves an inefficiency where
distances between given pairs was calculated more then once.

"""
import itertools

import numpy as np


def evaluate_diversity_single(indices, distances, weight=0.5):
    """
    takes the outcomes and selected scenario set (decision variables),
    returns a single 'diversity' value for the scenario set.

    Parameters
    ----------
    indices : ndarrray
    distances : ndarray
    weights : float
              weight given to the mean in the diversity metric. If 0, only minimum; if 1, only mean

    Returns
    -------
    list

    """
    i, j = [e for e in zip(*itertools.combinations(indices, 2))]
    subset_distances = distances[i, j]
    minimum = np.min(subset_distances)
    mean = np.mean(subset_distances)
    diversity = (1 - weight) * minimum + weight * mean

    return [diversity]


def find_maxdiverse_scenarios(distances, combinations):
    """

    Parameters
    ----------
    distances :
    combinations :

    Returns
    -------
    numpy array

    """
    scores = []
    for indices in combinations:
        diversity = evaluate_diversity_single(indices, distances)
        scores.append((diversity, indices))

    return scores