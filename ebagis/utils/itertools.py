from __future__ import absolute_import

from itertools import chain as itchain


def chain(*iterables):
    iterables = list(iterables)
    try:
        return itchain.from_iterable(iterables)
    except TypeError:
        for index, obj in enumerate(iterables):
            try:
                iter(obj)
            except TypeError:
                iterables[index] = [obj]
    return itchain.from_iterable(iterables)
