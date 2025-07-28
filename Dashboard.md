# Gurobi-logtools plotting dashboard

![dashboard map](https://github.com/Gurobi/gurobi-logtools/blob/master/assets/dashboard_map.svg)


## 1) x, y, color

These fields are used to indicate which columns of the DataFrame are used for the x-axis, y-axis, and color respectively.  If the color field is used then the legend will appear when the relavant checkbox is toggled on.

These fields will be sorted by alphabetical order (case-insensitive) with the exception of "None" which appears at the bottom.  Note that if graphing an ECDF then the "y" field will be disabled since the y-axis is fixed to represent the interval [0,1]  as a percentage.

These fields can be prepopulated in the plot function with keyword arguments `x`, `y` and `color`.

## 2) type, points, barmode, symbol

The type field will switch the chart between box plots, bar plots, scatter plots, line plots and ECDF (Empirical Cumulative Distribution Function) plots.  Depending on the plot type, several dropdowns are either activated or deactivated:

- When using box plots, the "points" field becomes available and corresponds to the parameter of the same name in [`plotly.express.box`](https://plotly.com/python-api-reference/generated/plotly.express.box.html).

- When using bar plots, , the "barmode" field becomes available and corresponds to the parameter of the same name in [`plotly.express.bar`](https://plotly.com/python-api-reference/generated/plotly.express.bar.html).

- When using scatter or line plots, the "symbol" field becomes available and corresponds to the parameter of the same name in [plotly.express.scatter](https://plotly.com/python-api-reference/generated/plotly.express.scatter.html) and [plotly.express.line](https://plotly.com/python-api-reference/generated/plotly.express.line.html)

Please see the documentation for this parameter in this link for more details.

These fields can be prepopulated in the plot function with keyword arguments `type`, `points`, `barmode` and `symbol`.


## 3) title, y axis label, x axis label

These optional fields are used to overwrite any settings for the chart title and axes labels.

These fields can be prepopulated in the plot function with keyword arguments `title`, `y_axis_label` and `x_axis_label`.

## 4) height, width

These fields are used to set the height and width of the chart.  The default values for these fields are zero - which indicate that Plotly should automatically size the chart.  Please note the smallest value these fields can take (other than 0) is 10.

These fields can be prepopulated in the plot function with keyword arguments `height` and `width`.

## 5) sort field, sort metric, sort axis

These fields are used to sort either the x or y axis.  The "sort field" will indicate which column of the DataFrame will be used to sort the data, the sort metric will apply one of the available functions (mean, median, minimum, maximum, standard deviation) when aggregating the data across the sort field, and the buttons will indicate which axes to sort.

These fields can be prepopulated in the plot function with keyword arguments `sort_field`, `sort_metric` and `sort_axis` ("x" or "y").

Notes:

- if the sort metric is None then sorting will not apply
- sorting is applied after any filtering is applied before the "DataFrame query string"


## 6) toggles

There are several checkboxes which affect the chart:

- **boxplot: show means** -  the solid line in the middle of each box is the median.  Selecting this checkbox will additionally display the mean as a dotted line.
​
- **boxplot: notched** -  if toggled then notches will be added to each box to represent a rough 95% confidence interval of the median. If the notches of two boxes do not overlap, it suggests a statistically significant difference between the medians.  Note that notches will only be appropriate when using a a reasonable number of data points for each box plot.
​
- **reverse ecdf** - by default a point (x,y) on the ECDF plot indicates that y percentage of data points have a value less than or equal to x.  When this checkbox is toggled the ECDF will be plotted so that (x, y) indicates that y percentage of data points have a value greater than x.
​
- **legend** - toggles the visibility of the legend on or off
​
- **log(x)** - applies a log scale to the x-axis
​
- **log(y)** - applies a log scale to the y-axis

These toggles can be prepopulated in the plot function with True/False values for keyword arguments `boxmean`, `notched`, `reverse_ecdf`, `legend`, `log_x` and `log_y`.


## 7) swap axes

The button will swap the x and y axes of the chart.  The following fields will switch as a result:

- x <- > y
- log_x <- > log_y
- x_axis_label <- > y_axis_label

Keyword arguments for the plot function are not applicable.


## 8) save/load config

The save config and load config buttons enable a single config - i.e. widget values - and load them again later.  This is particularly useful if you need to run the plot function again after styling the plot.

Keyword arguments for the plot function are not applicable.

## 9) palette type, palette name

Plotly groups its palettes into 3 categories: Qualitative, Sequential, Diverging.  Select from these groups using the "palette type" dropdown and then select the palette from the resulting values in the "palette name" dropdown.

A fourth palette group, "Gurobi", is added to enable coloring the chart with permutations of the Gurobi brand palette.

A fifth palette group, "Custom", is used to enable custom palettes to be added (via the `register_custom_palette` function).

These fields can be prepopulated in the plot function with keyword arguments `palette_type`, and `palette_name`.


## 10) color scale (discrete/continuous), categorical color

All the Plotly functions currently supported (box, line, ecdf, bar, scatter) take a keyword parameter `color_discrete_sequence` which is used when the data used to color the chart is not numeric.  Additionally, bar and scatter plots have a keyword parameter `color_continuous_scale`, intended for use when coloring the chart according to numeric data.  For discrete data the qualitative palette type is generally more appriopriate, and for numerical data the sequential and diverging palette types are recommended.

The color scale buttons - "discrete" and "continuous" - are used to switch between which plotly parameter is used.  If the data is discrete and the continuous button is selected then there will be no observable effect from changing the palette.  Likewise, if the data is continuous then selecting the discrete button will mean the palette selected will not be applied.

The categorical color checkbox is used when you have numeric data that you would like to be interpreted as discrete data, such as "Seed".

These fields can be prepopulated in the plot function with keyword arguments `color_scale` ("discrete" or "continuous"), and `color_categorical` (True or False).

## 11) DataFrame query string

This field is used as an argument to the [query](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html) method on pandas DataFrames.  You can use this to filter the data that generates the plot "live", without needing to re-call the plot function.

This field can be prepopulated in the plot function with the keyword argument `query`.


## 12) parameters to ignore

This field is used to affect the "Parameters" column that is inserted into the DataFrame when there is a "ChangedParams" column (such as the returned by the ).  The value of this field should be a list of parameters, separated by commas or spaces.  Any column name listed will be removed from the values in the Parameters column.  There are a few use cases for this:

i) Removing parameter values that are common to all parameter sets (decluttering the Parameters label) - perhaps these parameters would be better belonging to the chart title.
ii) Removing irrelevant parameters that have different, such as TimeLimit when the time limit was never reached (aggregating the data to important parameters only).
iii) Removing parameters that you want to use for the color field with the intention of displaying a legend.
