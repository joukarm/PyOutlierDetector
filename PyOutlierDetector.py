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

        self.spn_kthNN = QDoubleSpinBox(self)
        self.spn_kthNN.setSingleStep(1)
        self.spn_kthNN.setValue(3)
        self.spn_kthNN.setMinimum(1)
        self.spn_kthNN.setMaximum(10)

        self.spn_Percentile = QDoubleSpinBox(self)
        self.spn_Percentile.setSingleStep(1)
        self.spn_Percentile.setValue(5)
        self.spn_Percentile.setMinimum(1)
        self.spn_Percentile.setMaximum(20)

        self.label = QLabel("STDDEV multiplier:")
        self.plot_info = QLabel("Plot Info:")
        self.lblNN = QLabel("Kth Neighbor:")
        self.lblpercentile = QLabel("Top Outliers Percentile:")

        self.plot_info.setMaximumHeight(20)

        self.button = QPushButton('Plot')
        self.empty = QLabel("")

        # self.button.clicked.connect(self.plot)
        self.button.clicked.connect(
            lambda: self.my_outlier_plot(self.cbcases.currentText()))

        self.cbcases = QComboBox(self)
        for f in self.get_csv_files():
            self.cbcases.addItem(f)
        self.cbcases.setCurrentIndex(0)
        self.cbcases.currentIndexChanged.connect(
            lambda: self.my_outlier_plot(self.cbcases.currentText()))

        self.cbmethod = QComboBox(self)
        self.cbmethod.addItem('MJ Method (StdDev Multiplier)')
        self.cbmethod.addItem('MJ Method (Top Outliers Percentile)')
        self.cbmethod.addItem('KNN Method')
        self.cbmethod.currentIndexChanged.connect(
            lambda: self.my_outlier_plot(self.cbcases.currentText()))

        # set the layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.toolbar)

        vlayout.addWidget(self.cbmethod)
        vlayout.addWidget(self.cbcases)
        vlayout.addWidget(self.plot_info)
        vlayout.addWidget(self.canvas)

        h_layout_stddevmult = QHBoxLayout()
        h_layout_stddevmult.addWidget(self.label)
        h_layout_stddevmult.addWidget(self.spn_stddev_multiplier)

        h_layout_NN2 = QHBoxLayout()
        h_layout_NN2.addWidget(self.lblNN)
        h_layout_NN2.addWidget(self.spn_kthNN)

        h_layout_NN1 = QHBoxLayout()
        h_layout_NN1.addWidget(self.lblpercentile)
        h_layout_NN1.addWidget(self.spn_Percentile)

        vlayout.addLayout(h_layout_stddevmult, 1)
        vlayout.addLayout(h_layout_NN1, 1)
        vlayout.addLayout(h_layout_NN2, 1)

        h_layout_button = QHBoxLayout()
        h_layout_button.addWidget(self.empty)
        h_layout_button.addWidget(self.button)
        vlayout.addLayout(h_layout_button, 1)

        # vlayout.addWidget(self.empty)
        # vlayout.addWidget(self.button)

        self.setLayout(vlayout)
        # self.plot()
        self.my_outlier_plot(self.cbcases.currentText())
        # print(self.cbcases.currentText())

    @staticmethod
    def get_csv_files():
        return [f for f in glob.glob(r"data\*.csv")]

    def my_outlier_plot(self, sample_name):
        df = read_my_data(''.join([sample_name]))

        self.figure.clear()
        self.Reaarange_UI()

        t_init = time.time()

        stdDevMultiplier = self.spn_stddev_multiplier.value()
        top_outliers_percentage = self.spn_Percentile.value()
        kth_neighbour = self.spn_kthNN.value()

        if self.cbmethod.currentIndex() == 2:
            df['dist'] = \
                [kth_nearest_distances(df, (df['time'][i], df['rate'][i]), kth_neighbour, restrict_neighbours=True) for i in
                 range(len(df))]
        else:
            df['dist'] = [0, 0, 0] + [AvgNeighbourDiffSlopeDependent(df, i) for i in range(3, len(df) - 3)] + [0, 0, 0]

        df['dist'] = df['dist'] / max(df['dist'])

        # use_std_dev_multiplier = True

        if self.cbmethod.currentIndex() == 0:
            dfnew = GetOutliersUsingStdDevMultiplier(df, stdDevMultiplier)
        else:
            dfnew = GetOutliersUsingPercentile(df, top_outliers_percentage)

        # if use_std_dev_multiplier:
        #     dfnew = GetOutliersUsingStdDevMultiplier(df, stddev_multiplier)
        # else:
        #     dfnew = GetOutliersUsingPercentile(df, top_outliers_percentage)

        df_no_outlier = pd.DataFrame({'time': [], 'rate': []})
        for d in df.values:
            if d not in dfnew.values:
                df_no_outlier = df_no_outlier.append({'time': d[0], 'rate': d[1]}, ignore_index=True)

        calc_time = time.time() - t_init
        show_statistics(df, sample_name)

        # instead of ax.hold(False)
        self.figure.clear()

        ax1 = self.figure.add_subplot(221)
        ax2 = self.figure.add_subplot(222)
        ax3 = self.figure.add_subplot(223)
        ax4 = self.figure.add_subplot(224)

        assert isinstance(ax1, axes.Axes)
        set_axes_labels((ax1, ax2, ax3, ax4))

        ax1.scatter(df['time'], df['rate'], color='green', s=5, label='All Production Data')
        ax1.scatter(dfnew['time'], dfnew['rate'], marker='o', c='red', alpha=0.4, s=dfnew['dist'] * 50)

        ax2.plot(df['time'], df['rate'], label='All Production Data')
        ax2.scatter(dfnew['time'], dfnew['rate'], label=f"Outliers ({len(dfnew)}/{len(df)})", marker='o', c='red',
                    alpha=0.4,
                    s=dfnew['dist'] * 50)

        ax3.scatter(df_no_outlier['time'], df_no_outlier['rate'], color='blue', marker='o', s=5,
                    label='Production Data Without Outliers')
        ax3.axes.set_ylim(ax2.axes.get_ylim())

        ax4.plot(df_no_outlier['time'], df_no_outlier['rate'], label='Production Data Without Outliers')
        ax4.scatter(dfnew['time'], dfnew['rate'], color='red', label=f"Outliers ({len(dfnew)}/{len(df)})", marker='+',
                    s=dfnew['dist'] * 50)

        self.canvas.draw()
        self.figure.tight_layout()

        set_all_legends(self.figure)
        self.figure.tight_layout()
        self.canvas.draw()

        self.canvas.set_window_title("Salam")
        self.plot_info.setText(
            " | ".join([f"Case Name: {self.cbcases.currentText()}",
                        f"STDDEV Multiplier: {self.spn_stddev_multiplier.text()}",
                        f"Selected Method: {self.cbmethod.currentText()}"]))
        # save_plot(f)
        print_time_report(calc_time, t_init)

    def Reaarange_UI(self):
        controls = (
            self.label, self.spn_stddev_multiplier, self.lblNN, self.spn_kthNN, self.lblpercentile,
            self.spn_Percentile
        )
        for c in controls:
            c.setEnabled(False)

        if self.cbmethod.currentIndex() == 0:
            self.set_controls_enabled((self.label, self.spn_stddev_multiplier))
        elif self.cbmethod.currentIndex() == 1:
            self.set_controls_enabled((self.lblpercentile, self.spn_Percentile))
        elif self.cbmethod.currentIndex() == 2:
            self.set_controls_enabled((self.lblpercentile, self.spn_Percentile, self.lblNN, self.spn_kthNN))

    def set_controls_enabled(self, controls):
        for c in controls:
            c.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())
