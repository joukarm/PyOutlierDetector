"""
Includes methods used for displaying results in console.
"""

import time
import statistics


def display_elapsed_time(start_time):
    print("*" * 30)
    print(f"Elapsed Time: {time.time() - start_time:.2f} Seconds.")
    print("*" * 30)


def show_statistics(data_frame, sample_name):
    print("*" * 30)
    print(time.ctime())
    print("sampleName: " + sample_name)
    print('dist STD DEV  Value: ' + str(statistics.stdev(data_frame['dist'])))
    print('dist  MEAN    Value: ' + str(statistics.mean(data_frame['dist'])))
    print("=" * 30 + "\n")


def print_time_report(calc_time, t_init):
    overall_time = time.time() - t_init
    print(
        f"Overall Time: {overall_time:.2f} Sec  |  Calculation Time: {calc_time:.2f} Sec "
        f"({calc_time / overall_time * 100:.0f}%)  |  Other: {overall_time - calc_time:.2f} Sec"
        f"\n"
    )
