from typing import Iterator


def cumulative(iter: Iterator):
    running_sum = 0
    for elem in iter:
        running_sum += elem
        yield running_sum


def derive_percentage(iter: Iterator, max_: float = None):
    previous = None
    iter_ = iter
    if max_ is None:
        iter_ = list(iter_)
        max_ = max(iter_)
    for current in iter_:
        if previous is None:
            percentage = 0
        else:
            diff = current - previous
            percentage = diff / max_
        previous = current
        yield percentage


def multiply(iter1: Iterator, iter2: Iterator):
    for v1, v2 in zip(iter1, iter2):
        yield v1 * v2


def subtract(iter1: Iterator, iter2: Iterator):
    for v1, v2 in zip(iter1, iter2):
        yield v1 - v2


def normalise(iter: Iterator, min_: float = None, max_: float = None):
    is_max_none = max_ is None
    is_min_none = min_ is None
    iter_ = iter
    if is_max_none or is_min_none:
        iter_ = list(iter_)
        if is_min_none:
            min_ = min(iter_)
        if is_max_none:
            max_ = max(iter_)
    range_ = max_ - min_
    for v in iter_:
        yield (v - min_) / range_
