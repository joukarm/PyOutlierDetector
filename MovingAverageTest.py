import time
import numpy as np
import pandas as pd
from matplotlib import axes
import matplotlib.pyplot as plt

from Tools.CalculationTools import kth_nearest_distances, average_neighbours_difference, \
    get_outliers_by_stddev_multiplier, get_outliers_by_percentile
from Tools.DataTools import read_csv_file
from Tools.MessagingTools import show_statistics, print_time_report
from Tools.PlottingTools import set_axes_labels, set_all_legends


def plot(sample_name):
    raw_data = read_csv_file(sample_name)

    # self.figure.clear()
    # self.update_ui_controls()

    t_initial = time.time()

    std_dev_multiplier = 1
    top_outliers_percentage = 5
    kth_neighbour = 3

    cb_method = 1

    if cb_method == 2:
        data_dist = \
            [kth_nearest_distances(raw_data, (raw_data['time'][i], raw_data['rate'][i]), kth_neighbour,
                                   restrict_neighbours=True) for i in range(len(raw_data))]
    else:
        data_dist = [0, 0, 0] + [average_neighbours_difference(raw_data, i) for i in
                                 range(3, len(raw_data) - 3)] + [0, 0, 0]

    raw_data['dist'] = data_dist / (np.ones(len(data_dist)) * max(data_dist))

    cb_method = 2
    if cb_method == 0:
        outliers_data = get_outliers_by_stddev_multiplier(raw_data, std_dev_multiplier)
    else:
        outliers_data = get_outliers_by_percentile(raw_data, top_outliers_percentage)

    pruned_data = pd.DataFrame({'time': [], 'rate': []})
    for d in raw_data.values:
        if d not in outliers_data.values:
            pruned_data = pruned_data.append({'time': d[0], 'rate': d[1]}, ignore_index=True)

    calc_time = time.time() - t_initial
    show_statistics(raw_data, sample_name)

    fig, ((axis1, axis2), (axis3, axis4)) = plt.subplots(2, 2)

    assert isinstance(axis1, axes.Axes)
    set_axes_labels((axis1, axis2, axis3, axis4))

    axis1.scatter(raw_data['time'], raw_data['rate'], color='green', s=5, label='All Production Data')
    axis1.scatter(outliers_data['time'], outliers_data['rate'], marker='o', c='red', alpha=0.4,
                  s=outliers_data['dist'] * 50)

    axis2.plot(raw_data['time'], raw_data['rate'], label='All Production Data')
    axis2.scatter(outliers_data['time'], outliers_data['rate'],
                  label=f"Outliers ({len(outliers_data)}/{len(raw_data)})", marker='o',
                  c='red',
                  alpha=0.4,
                  s=outliers_data['dist'] * 50)

    axis3.scatter(pruned_data['time'], pruned_data['rate'], color='blue', marker='o', s=5,
                  label='Production Data Without Outliers')
    axis3.axes.set_ylim(axis2.axes.get_ylim())

    axis3.scatter(raw_data['time'], raw_data.rate.rolling(5, min_periods=1).mean(), color='red', marker='+', s=5,
                  label='Production Data Without Outliers')

    axis4.plot(pruned_data['time'], pruned_data['rate'], label='Production Data Without Outliers')
    axis4.scatter(outliers_data['time'], outliers_data['rate'], color='red',
                  label=f"Outliers ({len(outliers_data)}/{len(raw_data)})",
                  marker='+',
                  s=outliers_data['dist'] * 50)

    # set_all_legends(self.figure)
    # self.figure.tight_layout()
    # self.canvas.draw()
    #
    # self.lbl_plot_info.setText(
    #     " | ".join([f"Case Name: {self.cb_cases.currentText()}",
    #                 f"STDDEV Multiplier: {self.spn_stddev_multiplier.text()}",
    #                 f"Selected Method: {self.cb_method.currentText()}"]))

    print_time_report(calc_time, t_initial)
    plt.show()


plot(r"Data\Sample02.csv")
