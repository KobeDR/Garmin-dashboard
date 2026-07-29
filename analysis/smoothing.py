import numpy as np

from scipy.interpolate import UnivariateSpline


def smooth(x, y):

    s = len(y) * np.var(y)

    spline = UnivariateSpline(
        x,
        y,
        s=s
    )

    xs = np.linspace(min(x), max(x), 500)

    ys = spline(xs)

    return xs, ys