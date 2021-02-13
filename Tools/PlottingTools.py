"""
Contains methods to handle plotting processes.
"""

import matplotlib.pyplot as plt


def close_all_figures(allow):
    if allow:
        for p in plt.get_fignums():
            plt.close(p)


def set_axes_labels(axes):
    for axis in axes:
        axis.set_xlabel('Time')
        axis.set_ylabel('Rate')


def set_legend_location(ax):
    ax.legend(loc="lower right")


def set_plot_window_props(figure, plot, sample_name):
    try:
        mng = plot.get_current_fig_manager()
        mng.window.showMaximized()
        mng.set_window_title(sample_name[:-4])
        # matplotlib.use('Agg')
        figure.tight_layout()
    except ValueError:
        print('Agg backend was used to create image files only.')


def set_all_legends(figure):
    for ax in figure.get_axes():
        set_legend_location(ax)


def save_plot(figure, file_name):
    figure.savefig("".join([file_name, '.pdf']), bbox_inches='tight')
    figure.savefig("".join([file_name, '.png']), dpi=200)


def figure_name(sample_name, parameter, value):
    suffix = f" - {parameter}= {value}"
    return "".join(['plots\\', sample_name[len('data\\'):-4], suffix])
