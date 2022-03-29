import ipywidgets as widgets
import pandas as pd
import plotly.express as px
from ipywidgets import interact


def plot(df: pd.DataFrame, points="all", barmode="group", **kwargs):
    """plot different chart types to compare performance and see performance variability across random seeds

    uses Plotly express; all available keyword arguments can be passed through to px.bar(), px.scatter(), etc.
    """

    options = list(df.columns) + [None]

    if "Incumbent" in options:
        # read custom axis data or use common defaults for summary DataFrame
        x_default = kwargs.pop("x", "Time")
        y_default = kwargs.pop("y", "Incumbent")
        color_default = kwargs.pop("color", "Log")
    else:
        # read custom axis data or use common defaults for summary DataFrame
        x_default = kwargs.pop("x", "Log")
        y_default = kwargs.pop("y", "Runtime")
        color_default = kwargs.pop("color", "Seed")

    # set type to None to disable plotting until a type is selected
    type_default = kwargs.pop("type", None)

    # pop values for remaining widgets to avoid double inputs
    symbol_default = kwargs.pop("symbol", None)
    log_x_default = kwargs.pop("log_x", False)
    log_y_default = kwargs.pop("log_y", False)

    # check wether selected keys are available in DataFrame
    if x_default not in options:
        x_default = None
    if y_default not in options:
        y_default = None
    if color_default not in options:
        color_default = None

    switches = dict(
        x=widgets.Dropdown(options=options, value=x_default),
        y=widgets.Dropdown(options=options, value=y_default),
        color=widgets.Dropdown(options=options, value=color_default),
        type=widgets.Dropdown(
            options=["box", "bar", "scatter", "line"], value=type_default
        ),
        symbol=widgets.Dropdown(options=options, value=symbol_default),
        log_x=widgets.Checkbox(value=log_x_default),
        log_y=widgets.Checkbox(value=log_y_default),
    )

    @interact(**switches)
    def _(x, y, color, type, symbol, log_x, log_y):
        if type == "box":
            return px.box(
                df,
                x=x,
                y=y,
                color=color,
                points=points,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
        elif type == "bar":
            return px.bar(
                df,
                x=x,
                y=y,
                color=color,
                barmode=barmode,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
        elif type == "scatter":
            return px.scatter(
                df,
                x=x,
                y=y,
                color=color,
                symbol=symbol,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
        elif type == "line":
            return px.line(
                df,
                x=x,
                y=y,
                color=color,
                symbol=symbol,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
