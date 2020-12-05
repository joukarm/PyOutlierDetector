import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QMainWindow, QDoubleSpinBox, QComboBox, \
    QHBoxLayout, QLabel
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import matplotlib.axes._axes as axes
from src.outlier import *
import pandas as pd
import glob


class Window(QDialog, QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        Window.resize(self, 1600, 900)
        Window.setWindowTitle(self, "Outlier Assistant")
        Window.setWindowIcon(self, QtGui.QIcon(r'src\icon.ico'))
        matplotlib.use('Agg')
        self.figure = plt.figure()

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.spn_stddev_multiplier = QDoubleSpinBox(self)
        self.spn_stddev_multiplier.setSingleStep(0.05)
        self.spn_stddev_multiplier.setValue(0.9)
        # self.spinbtn.valueChanged.connect(
        #     lambda: self.my_outlier_plot(self.cbcases.currentText(), self.spinbtn.value()))

        self.label = QLabel("STDDEV multiplier:")
        self.plot_info = QLabel("Plot Info:")

        self.plot_info.setMaximumHeight(20)

        self.button = QPushButton('Plot')
        # self.button.clicked.connect(self.plot)
        self.button.clicked.connect(
            lambda: self.my_outlier_plot(self.cbcases.currentText(), self.spn_stddev_multiplier.value()))

        self.cbcases = QComboBox(self)
        for f in self.get_csv_files():
            self.cbcases.addItem(f)
        self.cbcases.setCurrentIndex(0)
        self.cbcases.currentIndexChanged.connect(
            lambda: self.my_outlier_plot(self.cbcases.currentText(), self.spn_stddev_multiplier.value()))

        # set the layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.toolbar)
        vlayout.addWidget(self.cbcases)
        vlayout.addWidget(self.plot_info)
        vlayout.addWidget(self.canvas)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.label)
        h_layout.addWidget(self.spn_stddev_multiplier)

        vlayout.addLayout(h_layout, 1)
        vlayout.addWidget(self.button)

        self.setLayout(vlayout)
        # self.plot()
        self.my_outlier_plot(self.cbcases.currentText(), self.spn_stddev_multiplier.value())
        # print(self.cbcases.currentText())

    @staticmethod
    def get_csv_files():
        return [f for f in glob.glob(r"data\*.csv")]

    def my_outlier_plot(self, sample_name, stddev_multiplier):
        # stdDevMultiplier = 0.1
        t_init = time.time()
        self.figure.clear()

        top_outliers_percentage = 15
        use_std_dev_multiplier = True

        df = read_my_data(''.join([sample_name]))

        df['kval'] = [0, 0, 0] + [AvgNeighbourDiffSlopeDependent(df, i) for i in range(3, len(df) - 3)] + [0, 0, 0]
        df['kval'] = df['kval'] / max(df['kval'])

        calc_time = time.time() - t_init
        show_statistics(df, sample_name)

        if use_std_dev_multiplier:
            dfnew = GetOutliersUsingStdDevMultiplier(df, stddev_multiplier)
        else:
            dfnew = GetOutliersUsingPercentile(df, top_outliers_percentage)

        df_no_outlier = pd.DataFrame({'time': [], 'rate': []})

        for d in df.values:
            if d not in dfnew.values:
                df_no_outlier = df_no_outlier.append({'time': d[0], 'rate': d[1]}, ignore_index=True)

        # instead of ax.hold(False)
        self.figure.clear()

        ax1 = self.figure.add_subplot(221)
        ax2 = self.figure.add_subplot(222)
        ax3 = self.figure.add_subplot(223)
        ax4 = self.figure.add_subplot(224)

        assert isinstance(ax1, axes.Axes)
        self.set_axes_labels((ax1, ax2, ax3, ax4))

        ax1.scatter(df['time'], df['rate'], color='green', s=5, label='All Production Data')
        ax1.scatter(dfnew['time'], dfnew['rate'], marker='o', c='red', alpha=0.4, s=dfnew['kval'] * 50)

        ax2.plot(df['time'], df['rate'], label='All Production Data')
        ax2.scatter(dfnew['time'], dfnew['rate'], label=f"Outliers ({len(dfnew)}/{len(df)})", marker='o', c='red',
                    alpha=0.4,
                    s=dfnew['kval'] * 50)

        ax3.scatter(df_no_outlier['time'], df_no_outlier['rate'], color='blue', marker='o', s=5,
                    label='Production Data Without Outliers')
        ax3.axes.set_ylim(ax2.axes.get_ylim())

        ax4.plot(df_no_outlier['time'], df_no_outlier['rate'], label='Production Data Without Outliers')
        ax4.scatter(dfnew['time'], dfnew['rate'], color='red', label=f"Outliers ({len(dfnew)}/{len(df)})", marker='+',
                    s=dfnew['kval'] * 50)

        self.canvas.draw()
        self.figure.tight_layout()

        set_all_legends(self.figure)
        self.figure.tight_layout()
        self.canvas.draw()

        self.canvas.set_window_title("Salam")
        self.plot_info.setText(
            " | ".join([f"Case Name: {self.cbcases.currentText()}",
                        f"STDDEV Multiplier: {self.spn_stddev_multiplier.text()}"]))
        # save_plot(f)
        self.print_time_report(calc_time, t_init)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())
