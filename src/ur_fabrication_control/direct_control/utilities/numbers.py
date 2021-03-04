from __future__ import absolute_import

__all__ = [
    'sign',
    'argsort',
    'convert_float_to_int'
]


def sign(number):
    """Returns the sign of a number: +1 or -1.
    """
    return int(int((number) > 0) - int((number) < 0))


def argsort(numbers):
    """Returns the indices that would sort a list of numbers.
    """
    return [i for i, _v in sorted(enumerate(numbers), key=lambda x: x[1])]

def convert_float_to_int(float_value):
    int_value = int(float_value*10000)
    return int_value