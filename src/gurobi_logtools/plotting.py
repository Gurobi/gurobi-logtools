import ipywidgets as widgets
import pandas as pd
import plotly.express as px
from IPython.display import display

from dataclasses import dataclass, fields
from typing import Optional, Dict, Tuple, List


@dataclass
class InitialWidgetValues:
    x: str = "Runtime"
    y: str = "Parameters"
    color: str = "Parameters"
    type: str = "box"
    symbol: Optional[str] = None
    log_x: bool = False
    log_y: bool = False


def _get_initial_widget_values(user_kwargs: Dict):
    field_names = {f.name for f in fields(InitialWidgetValues)}
    user_kwargs = {k: v for k, v in user_kwargs.items() if k in field_names}
    if user_kwargs:
        return InitialWidgetValues(
            {k: v for k, v in user_kwargs.items() if k in field_names}
        )
    return InitialWidgetValues()


def _make_widgets(options: List, user_kwargs: Dict) -> Dict:
    widget_defaults = _get_initial_widget_values(user_kwargs)

    # check wether selected keys are available in DataFrame
    widget_defaults.x = widget_defaults.x if widget_defaults.x in options else None
    widget_defaults.y = widget_defaults.y if widget_defaults.y in options else None
    widget_defaults.color = (
        widget_defaults.color if widget_defaults.color in options else None
    )

    options = sorted(options) + [None]

    widget_dict = dict(
        x=widgets.Dropdown(options=options, value=widget_defaults.x, description="x"),
        y=widgets.Dropdown(options=options, value=widget_defaults.y, description="y"),
        color=widgets.Dropdown(
            options=options, value=widget_defaults.color, description="color"
        ),
        type=widgets.Dropdown(
            options=["box", "bar", "scatter", "line"],
            value=widget_defaults.type,
            description="type",
        ),
        symbol=widgets.Dropdown(
            options=options,
            value=widget_defaults.symbol,
            description="symbol",
            disabled=widget_defaults.type not in ("scatter", "line"),
        ),
        log_x=widgets.Checkbox(value=widget_defaults.log_x, description="log(x)"),
        log_y=widgets.Checkbox(value=widget_defaults.log_y, description="log(y)"),
    )

    # used to disable one widget based on the value of another
    def type_change(change):
        widget_dict["symbol"].disabled = change["new"] not in ("scatter", "line")

    widget_dict["type"].observe(type_change, names="value")

    return widget_dict


def _add_pretty_param_labels(df: pd.DataFrame, ignored_params: Tuple) -> pd.DataFrame:
    pretty_params = (
        df["ChangedParams"]
        .map(
            lambda d: "<br>".join(
                [f"{k}={v}" for k, v in d.items() if k not in ignored_params]
            )
        )
        .replace("", "Defaults")
    )
    return df.assign(Parameters=pretty_params)


def _make_plot_function(df: pd.DataFrame, points, barmode, **kwargs):

    def _plot(
        x,
        y,
        color,
        type,
        symbol,
        log_x,
        log_y,
    ):
        common_kwargs = dict(
            x=x,
            y=y,
            color=color,
            log_x=log_x,
            log_y=log_y,
        )

        fig = None
        if type == "box":
            fig = px.box(df, **common_kwargs, points=points, **kwargs)
        elif type == "bar":
            fig = px.bar(df, **common_kwargs, barmode=barmode, **kwargs)
        elif type == "scatter":
            fig = px.scatter(df, **common_kwargs, symbol=symbol, **kwargs)
        elif type == "line":
            fig = px.line(df, **common_kwargs, symbol=symbol, **kwargs)
        if fig:
            fig.show()

    return _plot


def plot(
    df: pd.DataFrame,
    points="all",
    barmode="group",
    ignored_params=("TimeLimit", "SoftMemLimit"),
    **kwargs,
):
    """plot different chart types to compare performance and see performance variability across random seeds

    uses Plotly express; all available keyword arguments can be passed through to px.bar(), px.scatter(), etc.
    """
    df = _add_pretty_param_labels(df, ignored_params)

    widget_dict = _make_widgets(df.columns.tolist(), kwargs)

    ui = widgets.VBox(
        [
            widget_dict[key]
            for key in ("x", "y", "color", "type", "symbol", "log_x", "log_y")
        ]
    )

    output = widgets.interactive_output(
        _make_plot_function(df, points, barmode, **kwargs),
        widget_dict,
    )

    display(ui, output)
