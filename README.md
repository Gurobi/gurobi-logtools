# gurobi-logtools

[![PyPI](https://img.shields.io/pypi/v/gurobi-logtools?label=PyPI)](https://pypi.python.org/pypi/gurobi-logtools)
[![License](https://img.shields.io/github/license/Gurobi/gurobi-logtools?color=blue&label=License)](https://github.com/Gurobi/gurobi-logtools/blob/master/LICENSE)
[![Test Python Package](https://github.com/Gurobi/gurobi-logtools/actions/workflows/python-tox.yml/badge.svg?branch=master)](https://github.com/Gurobi/gurobi-logtools/actions/workflows/python-tox.yml)

Extract information from Gurobi log files and generate [pandas DataFrames](https://pandas.pydata.org/) or Excel worksheets for further processing. Also includes a wrapper for out-of-the-box interactive visualizations using the plotting library [Plotly](https://plotly.com/python/).

> [!NOTE]
> We have renamed the project to `gurobi-logtools`, so please also adapt the import statement accordingly:
> 
> `import gurobi_logtools as glt`

![performance plot](https://github.com/Gurobi/gurobi-logtools/raw/master/assets/performance-plot.png)

# Installation

```
python -m pip install gurobi-logtools
```

It is recommended to prepend the `pip install` command with `python -m` to ensure that the package is installed using the correct Python version currently active in your environment.

See [CHANGELOG](https://github.com/Gurobi/gurobi-logtools/blob/master/CHANGELOG.md) for added, removed or fixed functionality.

# Usage

First, you need a set of Gurobi log files to compare, e.g.,
  - results from several model instances
  - comparisons of different parameter settings
  - performance variability experiments involving multiple random seed runs
  - ...

You may also use the provided [gurobi-logtools.ipynb notebook](https://github.com/Gurobi/gurobi-logtools/blob/master/gurobi-logtools.ipynb) with the [example data set](https://github.com/Gurobi/gurobi-logtools/tree/master/data) to get started.
Additionally, there is a [Gurobi TechTalk demonstrating how to use it (YouTube)](https://youtu.be/wbg4Zr_A1s8):

[![](https://github.com/Gurobi/gurobi-logtools/raw/master/assets/youtube-thumbnail.png)](https://youtu.be/wbg4Zr_A1s8)

## Pandas/Plotly
1. parse log files:
    ```Python
    import gurobi_logtools as glt

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
    glt.plot(results.progress("norel"), x="Time", y="Incumbent", color="Log", type="line")
    ```

    These are just examples using the [Plotly Python library](https://plotly.com/python/) - of course, any other plotting library of your choice can be used to work with these DataFrames.

## Excel
Convert your log files to Excel worksheets right on the command-line:

```
python -m gurobi_logtools myrun.xlsx data/*.log
```

List all available options and how to use the command-line tool:

```
python -m gurobi_logtools --help
```

## Rename log files
The command line tool can also rename log files according to the parameters set and model solved in a given run. This is useful if your log files do not have a consistent naming scheme, or if multiple runs are logged per file and you want to extract the individual runs.

For example:

```
python -m gurobi_logtools --write-to-dir nicenames summary.xlsx tests/assets/combined/*.log
```

separates logs for individual runs in the input files and writes copies to the 'nicenames' folder with a consistent naming scheme:

```
> ls nicenames
912-MIPFocus1-Presolve1-TimeLimit600-glass4-0.log
912-MIPFocus1-Presolve1-TimeLimit600-glass4-1.log
912-MIPFocus1-Presolve1-TimeLimit600-glass4-2.log
912-MIPFocus2-Presolve1-TimeLimit600-glass4-0.log
912-MIPFocus2-Presolve1-TimeLimit600-glass4-1.log
912-MIPFocus2-Presolve1-TimeLimit600-glass4-2.log
912-Presolve1-TimeLimit600-glass4-0.log
912-Presolve1-TimeLimit600-glass4-1.log
912-Presolve1-TimeLimit600-glass4-2.log
```
