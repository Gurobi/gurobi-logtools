from enum import Enum, StrEnum


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
    SORT_X = "Sort x"
    SORT_Y = "Sort y"


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


class ColorScale(StrEnum):
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"
