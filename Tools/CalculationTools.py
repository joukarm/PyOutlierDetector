# -*- coding: utf-8 -*-
"""
Containing calculation methods and extraction methods used in Outlier Detection Process
"""

import statistics
import numpy as np
from math import sqrt


def average_neighbours_difference(dataset, index):
    """
    Calculates the average difference of a point with respect to two neighbours before and after the point

    :param dataset: data set containing raw (time, rate) data
    :param index: index of the point whose average_neighbours_difference should be calculated
    :return: average neighbours difference
    """
    err, t_current, q_current = 0, 0, 0

    t = dataset['time'][index]
    q = dataset['rate'][index]

    ns = 1
    for i in range(5):
        if i != 2:
            t_current = dataset['time'][index - 2 + i]
            q_current = dataset['rate'][index - 2 + i]
            err += abs((q_current - q) / (t_current - t))

        qim1 = dataset['rate'][index - 2 - 1]
        qip1 = dataset['rate'][index - 2 + 1]
        if (q_current - qim1) * (qip1 - q_current) < 0:
            ns = 1

    q_max = max(dataset['rate'][index - 2:index + 3])
    q_min = min(dataset['rate'][index - 2:index + 3])

    if q_current - q_min > q_max - q_current:
        multiplier = 1 + (q_current - q_min) / q_current
    else:
        multiplier = 1 + (q_max - q_current) / q_current

    return err * multiplier * ns


def get_outliers_by_stddev_multiplier(dataset, std_dev_multiplier):
    """
    Extracts outliers which lies out of valid range which is > (Mean + STDDEV*std_dev_multiplier)

    :param dataset: data set containing raw data with calculated dist column used to recognize outliers
    :param std_dev_multiplier: float value as STDDEV multiplier
    :return: collection of outlier points
    """
    error_margin = statistics.mean(dataset['dist']) + statistics.stdev(dataset['dist']) * std_dev_multiplier
    return dataset[dataset.dist > error_margin]


def get_outliers_by_percentile(dataset, top_outliers_percentage):
    """
    Extracts outliers in the top 'top_outliers_percentage' range

    :param dataset: data set containing raw data with calculated dist column used to recognize outliers
    :param top_outliers_percentage: float percentage value as top percentage
    :return: collection of outlier points
    """
    error_margin = np.percentile(a=dataset['dist'], q=100 - top_outliers_percentage)
    return dataset[dataset.dist > error_margin]


def kth_nearest_distances(dataset, datapoint, k=2, restrict_neighbours=True):
    """
    Calculates the k-th nearest neighbour of a point

    :param dataset: data set containing raw (time, rate) data
    :param datapoint: the point whose distance to neighbours should be surveyed
    :param k: determines k-th neighbour whose distance should be reported
    :param restrict_neighbours: if restrict_neighbours is True, the range of neighbours to be surveyed is restricted
    :return: the float value of k-th nearest distance of datapoint in the dataset
    """
    src = []
    range_multiplier = 0.1
    while len(src) <= k:

        if restrict_neighbours:
            delta_x = (max(dataset.time) - min(dataset.time)) * range_multiplier
            delta_y = (max(dataset.rate) - min(dataset.rate)) * range_multiplier
            src = dataset[((dataset.time > datapoint[0] - delta_x) & (dataset.time < datapoint[0] + delta_x)) & (
                    (dataset.rate > datapoint[1] - delta_y) & (dataset.rate < datapoint[1] + delta_y))]
            range_multiplier += 0.1
        else:
            src = dataset

    if len(src) == 0:
        src = dataset

    distances = [euclidean_distance(datapoint[0], datapoint[1], v[0], v[1]) for v in src.values]

    sorted_distances = sorted(distances)
    return sorted_distances[int(k)]


def euclidean_distance(x1, y1, x2, y2):
    """
    Calculates the Euclidean distance between (x1,y1) and (x2,y2) using sqrt(dx^2+dy^2)

    :param x1: x1
    :param y1: y1
    :param x2: x2
    :param y2: x2
    :return: Euclidean distance between (x1,y1) and (x2,y2)
    """
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
