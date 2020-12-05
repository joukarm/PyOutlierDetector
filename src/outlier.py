# -*- coding: utf-8 -*-
import glob
import os

import matplotlib.pyplot as plt
import pandas as pd
from src.ErrorCalculationModule import *
import time


def read_my_data(file_name):
    return pd.read_csv(file_name)


def close_all_figures(allow):
    if allow:
        for p in plt.get_fignums():
            plt.close(p)
            pass


def set_axes_labels(axes):
    for axis in axes:
        axis.set_xlabel('Time')
        axis.set_ylabel('Rate')


def set_legend_location(ax):
    ax.legend(loc="lower right")


def set_plot_window_props(figure, plot):
    try:
        mng = plot.get_current_fig_manager()
        mng.window.showMaximized()
        mng.set_window_title(sampleName[:-4])
        # matplotlib.use('Agg')
        figure.tight_layout()
    except:
        print('Agg backend was used to create image files only.')


def set_all_legends(figure):
    for ax in figure.get_axes():
        set_legend_location(ax)


def save_plot(figure):
    if UseSTDDevMultiplier:
        suffix = f" - STDDev Multiplier = {stdDevMultiplier}"
    else:
        suffix = f" - Top Outliers Percentage = {TopOutliersPercentageToRemove}"

    figure.savefig("".join(['plots\\', sampleName[len('data\\'):-4], suffix, '.pdf']), bbox_inches='tight')
    figure.savefig("".join(['plots\\', sampleName[len('data\\'):-4], suffix, '.png']), dpi=200)


def display_elapsed_time(start_time):
    end_time = time.time()
    print("*" * 30)
    print(f"Elapsed Time: {end_time - start_time:.2f} Seconds.")
    print("*" * 30)


def show_statistics(data_frame, sample_name):
    print("*" * 30)
    print(time.ctime())
    print("sampleName: " + sample_name)
    print('kval STD DEV : ' + str(statistics.stdev(data_frame['kval'])))
    print('kval MEAN Val: ' + str(statistics.mean(data_frame['kval'])))
    print("=" * 30 + "\n")


def print_time_report(calc_time, t_init):
    overall_time = time.time() - t_init
    print(
        f"Overall Time: {overall_time:.2f} Sec  |  Calculation Time: {calc_time:.2f} Sec "
        f"({calc_time / overall_time * 100:.0f}%)  |  Other: {overall_time - calc_time:.2f} Sec"
        f""
    )


if __name__ == "__main__":
    start_time = time.time()

    # os.chdir(r"data")
    csv_files = [file for file in glob.glob(r"data\*.csv")]

    # os.chdir(r"..\plots")
    plot_files = [file for file in glob.glob(r"plots\*.*")]
    for file in plot_files:
        os.remove(file)

    GoodSamplesList = ["sample2.csv", "sample5.csv", "sample6.csv", "sample8.csv"]
    Challenging = ["sample7.csv"]

    close_all_figures(True)
    stdDevMultiplier = 0.1
    TopOutliersPercentageToRemove = 15
    UseSTDDevMultiplier = False

    for sampleName in csv_files[1:2]:

        df = read_my_data(''.join([sampleName]))

        # df['kval'] = np.zeros(len(df))

        # for i in range(3, len(df) - 3):
        #     myval = AvgNeighbourDiffSlopeDependent(df, i)
        #     df['kval'][i] = myval
        df['kval'] = [0] * 3 + [AvgNeighbourDiffSlopeDependent(df, i) for i in range(3, len(df) - 3)] + [0] * 3
        df['kval'] = df['kval'] / max(df['kval'])

        show_statistics(df, sampleName)

        if UseSTDDevMultiplier:
            dfnew = GetOutliersUsingStdDevMultiplier(df, stdDevMultiplier)
        else:
            dfnew = GetOutliersUsingPercentile(df, TopOutliersPercentageToRemove)

        dfNoOutlier = pd.DataFrame({'time': [], 'rate': []})

        for d in df.values:
            if d not in dfnew.values:
                dfNoOutlier = dfNoOutlier.append({'time': d[0], 'rate': d[1]}, ignore_index=True)

        f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(1600 / 72, 900 / 72), dpi=72)

        set_plot_window_props(f, plt)

        ax1.scatter(df['time'], df['rate'], color='green', s=5, label='All Production Data')
        ax1.scatter(dfnew['time'], dfnew['rate'], marker='o', c='red', alpha=0.4, s=dfnew['kval'] * 50)

        ax2.plot(df['time'], df['rate'], label='All Production Data')
        ax2.scatter(dfnew['time'], dfnew['rate'], label=f"Outliers ({len(dfnew)}/{len(df)})", marker='o', c='red',
                    alpha=0.4,
                    s=dfnew['kval'] * 50)

        ax3.scatter(dfNoOutlier['time'], dfNoOutlier['rate'], color='blue', marker='o', s=5,
                    label='Production Data Without Outliers')
        ax3.axes.set_ylim(ax2.axes.get_ylim())

        ax4.plot(dfNoOutlier['time'], dfNoOutlier['rate'], label='Production Data Without Outliers')
        ax4.scatter(dfnew['time'], dfnew['rate'], color='red', label=f"Outliers ({len(dfnew)}/{len(df)})", marker='+',
                    s=dfnew['kval'] * 50)

        set_all_legends(f)
        save_plot(f)

        if False:
            ff, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)
            set_plot_window_props(ff, plt)

            ax1.set_title('Production Line Plot')
            ax1.plot(df['time'], df['rate'], label='All Production Data')

            ax2.set_title('Production Scatter Plot')
            ax2.scatter(df['time'], df['rate'], color='blue', label='All Production Data')

            ax3.set_title('Production Scatter Plot and Neighbour Error Values')
            ax3.scatter(dfnew['time'], dfnew['kval'], color='red', label='K-Error')
            ax32 = ax3.twinx()
            ax32.scatter(df['time'], df['rate'], color='green', label='Production Data')
            # ax3.legend(loc='upper left')
            # set_legend_location(ax32)

            ax4.set_title('Production Scatter Plot with Marker size Presenting The Error')
            ax4.scatter(df['time'], df['rate'], color='green', s=df['kval'] * 50, label='All Production Data')

            ax5.scatter(df['time'], df['rate'], color='green', s=5)
            ax5.scatter(dfnew['time'], dfnew['rate'], color='red', label='K-Error', s=dfnew['kval'] * 50)

            set_all_legends(ff)
        #######################################################################################################

    display_elapsed_time((start_time))
