import csv
import os

import matplotlib
import matplotlib.pyplot as plt

_PLOT_MARGIN = 0.05
_DEFAULT_FILE_LOCATION = "public/reports"


def min_with_margin(min_: float, value_range: float):
    return min_ - value_range * _PLOT_MARGIN


def max_with_margin(max_: float, value_range: float):
    return max_ + value_range * _PLOT_MARGIN


def subplots():
    fig, ax = plt.subplots()
    return fig, ax,


class Plottable:
    def __init__(self, x: [], y: [], label: str):
        self.x, self.y, self.label = x, y, label


class Plot:
    def plot(self, x, y, label, do_show=False):
        raise NotImplementedError()

    def show(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()


class WindowPlot(Plot):
    def __init__(self):
        self.min_val, self.max_val = None, None
        self.fig, self.ax = None, None
        matplotlib.use('TkAgg')
        self.reset()

    def plot(self, x, y, label, do_show=False):
        y_min = min(y)
        y_max = max(y)
        self.min_val = y_min if self.min_val is None else min(self.min_val, y_min)
        self.max_val = y_max if self.max_val is None else max(self.max_val, y_max)
        self.ax.plot(x, y, label=label)
        self.ax.legend()

        self.ax.plot(x, [y[-1]] * len(x), label=label + "_END")
        # self.ax.hlines(y=y[-1], xmin=0, xmax=len(x), linestyles='--')
        if do_show:
            self.show()

    def show(self):
        val_range = abs(self.max_val - self.min_val)
        min_y = min_with_margin(self.min_val, val_range)
        max_y = max_with_margin(self.max_val, val_range)
        plt.ylim(min_y, max_y)
        plt.show()

    def reset(self):
        self.min_val, self.max_val = None, None
        self.fig, self.ax = subplots()


class CsvFilePlot(Plot):
    def __init__(self, folder_path=None):
        self.labelled_values = None
        self.folder_path = _DEFAULT_FILE_LOCATION if folder_path is None else folder_path
        self.reset()

    def plot(self, x, y, label, do_show=False):
        self.labelled_values[self._get_file_path(label)] = [[str(x_col), str(y_col)] for x_col, y_col in zip(x, y)]
        if do_show:
            self.show()

    def _get_file_path(self, label):
        return os.path.join(self.folder_path, f"{label}.csv")

    def show(self):
        for label, rows in self.labelled_values.items():
            with open(label, "w", newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for row in rows:
                    writer.writerow(row)

    def save(self):
        self.show()

    def reset(self):
        self.labelled_values = dict()
