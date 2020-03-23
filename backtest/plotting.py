import matplotlib.pyplot as plt

_PLOT_MARGIN = 0.05


def min_with_margin(min_: float, value_range: float):
    return min_ - value_range * _PLOT_MARGIN


def max_with_margin(max_: float, value_range: float):
    return max_ + value_range * _PLOT_MARGIN


def subplots():
    fig, ax = plt.subplots()
    return fig, ax,


def plot(df, x, y, floor=None, ceiling=None, label=None, do_show=False, ax=None):
    if label is None:
        label = ""
    min_val = df[y].min() if floor is None else floor
    max_val = df[y].max() if ceiling is None else ceiling

    val_range = abs(max_val - min_val)
    min_y = min_with_margin(min_val, val_range)
    max_y = max_with_margin(max_val, val_range)
    df.plot(x=x, y=y, ylim=(min_y, max_y), label=label, ax=ax, kind='line')
    if do_show:
        show()


def show():
    plt.show()
