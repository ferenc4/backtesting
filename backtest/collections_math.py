from typing import Iterator


def cumulative(iter: Iterator):
    running_sum = 0
    for elem in iter:
        if elem is None:
            yield None
        else:
            running_sum += elem
            yield running_sum


def derive_percentage(iter: Iterator, max_: float = None):
    previous = None
    iter_ = iter
    if max_ is None:
        iter_ = list(iter_)
        max_ = max([entry for entry in iter_ if entry is not None])
    for current in iter_:
        if current is None:
            percentage = None
        elif previous is None:
            percentage = 0
        else:
            diff = current - previous
            percentage = diff / max_
        previous = current
        yield percentage


def multiply(iter1: Iterator, iter2: Iterator):
    for v1, v2 in zip(iter1, iter2):
        if v1 is not None and v2 is None:
            result = v1
        elif v1 is None and v2 is not None:
            result = v2
        elif v1 is None and v2 is None:
            result = None
        else:
            result = v1 * v2
        yield result


def divide_by_number(iter1: Iterator, number: int):
    for val in iter1:
        if val is None:
            result = None
        else:
            result = val / number
        yield result


def subtract(iter1: Iterator, iter2: Iterator):
    for v1, v2 in zip(iter1, iter2):
        if v1 is not None and v2 is None:
            result = v1
        elif v1 is None and v2 is not None:
            result = -v2
        elif v1 is None and v2 is None:
            result = None
        else:
            result = v1 - v2
        yield result


def add(iter1: Iterator, iter2: Iterator):
    for v1, v2 in zip(iter1, iter2):
        if v1 is not None and v2 is None:
            result = v1
        elif v1 is None and v2 is not None:
            result = v2
        elif v1 is None and v2 is None:
            result = None
        else:
            result = v1 + v2
        yield result


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
        if v is None:
            result = None
        else:
            result = (v - min_) / range_
        yield result
