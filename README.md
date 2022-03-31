# GRBlogtools

[![PyPI](https://img.shields.io/pypi/v/grblogtools?label=PyPI)](https://pypi.python.org/pypi/grblogtools)
[![License](https://img.shields.io/github/license/Gurobi/grblogtools?color=blue&label=License)](https://github.com/Gurobi/grblogtools/blob/master/LICENSE)
[![Test Python Package](https://github.com/Gurobi/grblogtools/actions/workflows/python-tox.yml/badge.svg?branch=master)](https://github.com/Gurobi/grblogtools/actions/workflows/python-tox.yml)

Extract information from Gurobi log files and generate [pandas DataFrames](https://pandas.pydata.org/) or Excel worksheets for further processing. Also includes a wrapper for out-of-the-box interactive visualizations using the plotting library [Plotly](https://plotly.com/python/).

![performance plot](https://github.com/Gurobi/grblogtools/raw/master/assets/performance-plot.png)

# Installation

```
python -m pip install grblogtools
```

It is recommended to prepend the `pip install` command with `python -m` to ensure that the package is installed using the correct Python version currently active in your environment.

See [CHANGELOG](https://github.com/Gurobi/grblogtools/blob/master/CHANGELOG.md) for added, removed or fixed functionality.

# Usage

First, you need a set of Gurobi log files to compare, e.g.,
  - results from several model instances
  - comparisons of different parameter settings
  - performance variability experiments involving multiple random seed runs
  - ...

You may also use the provided [grblogtools.ipynb notebook](https://github.com/Gurobi/grblogtools/blob/master/grblogtools.ipynb) with the [example data set](https://github.com/Gurobi/grblogtools/tree/master/data) to get started.
Additionally, there is a [Gurobi TechTalk demonstrating how to use grblogtools (YouTube)](https://youtu.be/wbg4Zr_A1s8):

[![](https://github.com/Gurobi/grblogtools/raw/master/assets/youtube-thumbnail.png)](https://youtu.be/wbg4Zr_A1s8)

## Pandas/Plotly
1. parse log files:
    ```Python
    import grblogtools as glt

    results = glt.parse(["run1/*.log", "run2/*.log"])
    summary = results.summary()
    nodelog_progress = results.progress("nodelog")
    ```
    Depending on your requirements, you may need to filter or modify the resulting DataFrames.

2. draw interactive charts, preferably in a [Jupyter Notebook](https://jupyter.org/):

    - final results from the individual runs:
    ```Python
    glt.plot(summary, type="box")
    ```

    - progress charts for the individual runs:
    ```Python
    glt.plot(nodelog_progress, y="Gap", color="Log", type="line")
    ```

    - progress of the norel heuristic (note, the time recorded here is since the start of norel, and does not include presolve + read time):
    ```Python
    glt.plot(result.progress("norel"), x="Time", y="Incumbent", color="Log", type="line")
    ```

    These are just examples using the [Plotly Python library](https://plotly.com/python/) - of course, any other plotting library of your choice can be used to work with these DataFrames.

## Excel
Convert your log files to Excel worksheets right on the command-line:

```
python -m grblogtools myrun.xlsx data/*.log
```

List all available options and how to use the command-line tool:

```
python -m grblogtools --help
```
