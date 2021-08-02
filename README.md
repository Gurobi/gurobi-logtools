# logextract

Extract information from Gurobi log files and generate Pandas DataFrames or Excel worksheets for further processing. Also includes a wrapper for out-of-the-box interactive visualizations using the plotting library Plot.ly.

# Usage

First, you need a set of Gurobi log files to compare, e.g.,
  - results from several model instances
  - comparisons of different parameter settings
  - performance variability experiments involving multiple random seed runs
  - ...

## Pandas/Plot.ly
1. parse log files:
    ```
    import logextract as lx

    summary, timelines, rootlp = lx.get_dataframe(["run1/*.log", "run2/*.log"], timelines=True)
    ```
    Depending on your requirements, you may need to filter or modify the resulting DataFrames.

2. draw interactive charts, preferrably in a Jupyter Notebook:
    
    - final results from the individual runs:
    ```
    lx.plot(summary, x="Settings", y="Runtime", color="Seed", type="box")
    ```
    
    - progress charts for the individual runs:
    ```
    lx.plot(timelines, x="Timestamp", y="Gap", color="Log", type="line")
    ```

    These are just examples using the Plot.ly library - of course, any other plotting library of your choice can be used to work with these DataFrames.

## Excel
Converting your log files to Excel worksheets works on the command-line:

```
python -m logextract --help
```

This will show the available options and how to use the library.
