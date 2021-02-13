import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QMainWindow, QDoubleSpinBox, QComboBox, \
    QHBoxLayout, QLabel
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import matplotlib.axes._axes as axes

from Tools.CalculationTools import *
from Tools.DataTools import *
from Tools.MessagingTools import *
from Tools.PlottingTools import *
from Tools.UITools import set_controls_enabled


class Window(QDialog, QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        Window.resize(self, 1600, 900)
        Window.setWindowTitle(self, "Outlier Assistant")
        Window.setWindowIcon(self, QtGui.QIcon(r'Resources\icon.ico'))
        matplotlib.use('Agg')
        self.figure = plt.figure()

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.spn_stddev_multiplier = QDoubleSpinBox(self)
        self.spn_stddev_multiplier.setSingleStep(0.05)
        self.spn_stddev_multiplier.setValue(0.9)

        self.spn_kth_nn = QDoubleSpinBox(self)
        self.spn_kth_nn.setSingleStep(1)
        self.spn_kth_nn.setValue(3)
        self.spn_kth_nn.setMinimum(1)
        self.spn_kth_nn.setMaximum(10)

        self.spn_Percentile = QDoubleSpinBox(self)
        self.spn_Percentile.setSingleStep(1)
        self.spn_Percentile.setValue(5)
        self.spn_Percentile.setMinimum(1)
        self.spn_Percentile.setMaximum(20)

        self.lbl_std_dev = QLabel("STDDEV multiplier:")
        self.lbl_plot_info = QLabel("Plot Info:")
        self.lbl_kth_nn = QLabel("Kth Neighbor:")
        self.lbl_percentile = QLabel("Top Outliers Percentile:")

        self.lbl_plot_info.setMaximumHeight(20)

        self.btn_plot = QPushButton('Plot')
        self._ =QLabel('')
        self.btn_plot.clicked.connect(lambda: self.plot(self.cb_cases.currentText()))

        self.cb_cases = QComboBox(self)
        for f in get_csv_files():
            self.cb_cases.addItem(f)
        self.cb_cases.setCurrentIndex(0)
        self.cb_cases.currentIndexChanged.connect(lambda: self.plot(self.cb_cases.currentText()))

        self.cb_method = QComboBox(self)
        self.cb_method.addItem('MJ Method (StdDev Multiplier)')
        self.cb_method.addItem('MJ Method (Top Outliers Percentile)')
        self.cb_method.addItem('KNN Method')
        self.cb_method.currentIndexChanged.connect(lambda: self.plot(self.cb_cases.currentText()))

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.toolbar)

        v_layout.addWidget(self.cb_method)
        v_layout.addWidget(self.cb_cases)
        v_layout.addWidget(self.lbl_plot_info)
        v_layout.addWidget(self.canvas)

        h_layout_stddevmult = QHBoxLayout()
        h_layout_stddevmult.addWidget(self.lbl_std_dev)
        h_layout_stddevmult.addWidget(self.spn_stddev_multiplier)

        h_layout_nn_1 = QHBoxLayout()
        h_layout_nn_1.addWidget(self.lbl_percentile)
        h_layout_nn_1.addWidget(self.spn_Percentile)

        h_layout_nn_2 = QHBoxLayout()
        h_layout_nn_2.addWidget(self.lbl_kth_nn)
        h_layout_nn_2.addWidget(self.spn_kth_nn)

        h_layout_btn = QHBoxLayout()
        h_layout_btn.addWidget(self._)
        h_layout_btn.addWidget(self.btn_plot)

        v_layout.addLayout(h_layout_stddevmult, 1)
        v_layout.addLayout(h_layout_nn_1, 1)
        v_layout.addLayout(h_layout_nn_2, 1)
        v_layout.addLayout(h_layout_btn, 1)
        # v_layout.addWidget(self.btn_plot)

        self.setLayout(v_layout)
        self.plot(self.cb_cases.currentText())

    def plot(self, sample_name):
        raw_data = read_csv_file(sample_name)

        self.figure.clear()
        self.update_ui_controls()

        t_initial = time.time()

        std_dev_multiplier = self.spn_stddev_multiplier.value()
        top_outliers_percentage = self.spn_Percentile.value()
        kth_neighbour = self.spn_kth_nn.value()

        if self.cb_method.currentIndex() == 2:
            data_dist = \
                [kth_nearest_distances(raw_data, (raw_data['time'][i], raw_data['rate'][i]), kth_neighbour,
                                       restrict_neighbours=True) for i in range(len(raw_data))]
        else:
            data_dist = [0, 0, 0] + [average_neighbours_difference(raw_data, i) for i in
                                     range(3, len(raw_data) - 3)] + [0, 0, 0]

        raw_data['dist'] = data_dist / (np.ones(len(data_dist)) * max(data_dist))

        if self.cb_method.currentIndex() == 0:
            outliers_data = get_outliers_by_stddev_multiplier(raw_data, std_dev_multiplier)
        else:
            outliers_data = get_outliers_by_percentile(raw_data, top_outliers_percentage)

        pruned_data = pd.DataFrame({'time': [], 'rate': []})
        for d in raw_data.values:
            if d not in outliers_data.values:
                pruned_data = pruned_data.append({'time': d[0], 'rate': d[1]}, ignore_index=True)

        calc_time = time.time() - t_initial
        show_statistics(raw_data, sample_name)

        self.figure.clear()
        [[axis1, axis2], [axis3, axis4]] = self.figure.subplots(2, 2)

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

        axis4.plot(pruned_data['time'], pruned_data['rate'], label='Production Data Without Outliers')
        axis4.scatter(outliers_data['time'], outliers_data['rate'], color='red',
                      label=f"Outliers ({len(outliers_data)}/{len(raw_data)})",
                      marker='+',
                      s=outliers_data['dist'] * 50)

        set_all_legends(self.figure)
        self.figure.tight_layout()
        self.canvas.draw()

        self.lbl_plot_info.setText(
            " | ".join([f"Case Name: {self.cb_cases.currentText()}",
                        f"STDDEV Multiplier: {self.spn_stddev_multiplier.text()}",
                        f"Selected Method: {self.cb_method.currentText()}"]))

        print_time_report(calc_time, t_initial)

    def update_ui_controls(self):
        controls = (
            self.lbl_std_dev, self.spn_stddev_multiplier, self.lbl_kth_nn, self.spn_kth_nn, self.lbl_percentile,
            self.spn_Percentile
        )

        set_controls_enabled(controls, False)

        if self.cb_method.currentIndex() == 0:
            set_controls_enabled((self.lbl_std_dev, self.spn_stddev_multiplier))
        elif self.cb_method.currentIndex() == 1:
            set_controls_enabled((self.lbl_percentile, self.spn_Percentile))
        elif self.cb_method.currentIndex() == 2:
            set_controls_enabled((self.lbl_percentile, self.spn_Percentile, self.lbl_kth_nn, self.spn_kth_nn))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())
