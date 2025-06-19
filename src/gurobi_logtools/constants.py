from enum import Enum
import sys


class _StrEnum(str, Enum):
    """Back-port of :pyclass:`enum.StrEnum` (Python ≥ 3.11)"""

    def __new__(cls, value):
        if not isinstance(value, str):
            raise TypeError("StrEnum values must be str")
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    __module__ = __name__


if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    StrEnum = _StrEnum


class PlotType(StrEnum):
    BOX = "box"
    BAR = "bar"
    SCATTER = "scatter"
    LINE = "line"
    ECDF = "ecdf"


class Points(Enum):
    OUTLIERS = "outliers"
    SUSPECTEDOUTLIERS = "suspectedoutliers"
    ALL = "all"
    FALSE = False


class BarMode(StrEnum):
    GROUP = "group"
    OVERLAY = "overlay"
    RELATIVE = "relative"


class SortAxis(StrEnum):
    SORT_Y = "Sort y axis"
    SORT_X = "Sort x axis"


class SortMetric(Enum):
    NONE = None
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    STD = "std"


class PaletteType(StrEnum):
    QUALITATIVE = "Qualitative"
    SEQUENTIAL = "Sequential"
    DIVERGING = "Diverging"
    GUROBI = "Gurobi"


class ColorScale(StrEnum):
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"
