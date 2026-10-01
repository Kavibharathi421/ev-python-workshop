import math


def check(value, name, minimum=0, maximum=None, positive=False):
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number.")
    if value < minimum or (positive and value == 0):
        raise ValueError(f"{name} must be {'greater than' if positive else 'at least'} {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} cannot exceed {maximum}.")
