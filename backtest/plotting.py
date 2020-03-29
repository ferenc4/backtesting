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


class FilePlot(Plot):
    def __init__(self, file_path):
        self.x_dict, self.y_dict = None, None
        self.file_path = file_path
        self.reset()

    def plot(self, x, y, label, do_show=False):
        self.x_dict[label] = x
        self.y_dict[label] = y

        if do_show:
            self.show()

    def show(self):
        # todo save to file
        pass

    def reset(self):
        self.x_dict = dict()
        self.y_dict = dict()
