import matplotlib
import matplotlib.pyplot as plt

_PLOT_MARGIN = 0.05


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
    def __init__(self, file_path):
        self.labelled_values = None
        self.file_path = file_path
        self.reset()

    def plot(self, x, y, label, do_show=False):
        for x_value, y_value in zip(x, y):
            self.plot_row(x_value, y_value, label)
        self.labelled_values[label] = x
        self.y_dict[label] = y

        if do_show:
            self.show()

    def plot_row(self, x_value, y_value, label):
        # self.labelled_values[label] =
        print(label, x_value, y_value)

    def show(self):
        for label_x, x_value in self.x_dict:
            y = self.y_dict[label_x]

    def save(self):
        self.show()

    def reset(self):
        self.x_dict = dict()
        self.y_dict = dict()
