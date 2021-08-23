# GRBlogtools

![PyPI](https://img.shields.io/pypi/v/grblogtools?color=blue&label=PyPI)

Extract information from Gurobi log files and generate [pandas DataFrames](https://pandas.pydata.org/) or Excel worksheets for further processing. Also includes a wrapper for out-of-the-box interactive visualizations using the plotting library [Plotly](https://plotly.com/python/).

![performance plot](https://github.com/Gurobi/grblogtools/raw/master/assets/performance-plot.png)

# Installation

```
pip install grblogtools
```

# Usage

First, you need a set of Gurobi log files to compare, e.g.,
  - results from several model instances
  - comparisons of different parameter settings
  - performance variability experiments involving multiple random seed runs
  - ...

## Pandas/Plotly
1. parse log files:
    ```Python
    import grblogtools as glt

    summary, timelines, rootlp = glt.get_dataframe(["run1/*.log", "run2/*.log"], timelines=True)
    ```
    Depending on your requirements, you may need to filter or modify the resulting DataFrames.

2. draw interactive charts, preferably in a [Jupyter Notebook](https://jupyter.org/):
    
    - final results from the individual runs:
    ```Python
    glt.plot(summary, type="box")
    ```
    
    - progress charts for the individual runs:
    ```Python
    glt.plot(timelines, y="Gap", color="Log", type="line")
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
