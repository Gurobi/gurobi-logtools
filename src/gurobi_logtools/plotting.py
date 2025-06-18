import contextlib
from dataclasses import dataclass, fields
from typing import Dict, List, Optional, Tuple

import ipywidgets as widgets
import pandas as pd
import plotly.express as px
from IPython.display import display

from gurobi_logtools import constants
from gurobi_logtools.colors import (  # _diverging_plotly_palettes,; _qualitative_plotly_palettes,; _sequential_plotly_palettes,
    _get_default_palette,
    _get_palette,
    _get_palettes,
)


@dataclass
class InitialWidgetValues:
    x: str = "Runtime"
    y: str = "Parameters"
    color: str = "Parameters"
    type: constants.PlotType = constants.PlotType.BOX.value
    symbol: Optional[str] = None
    log_x: bool = False
    log_y: bool = False
    points: constants.Points = constants.Points.ALL.value
    barmode: constants.BarMode = constants.BarMode.GROUP.value
    show_legend: bool = False
    sort_metric: Optional[constants.SortMetric] = constants.SortMetric.NONE.value
    boxmean: bool = False
    notched: bool = False
    reverse_ecdf: bool = False
    palette_type: constants.PaletteType = constants.PaletteType.QUALITATIVE.value


def _get_initial_widget_values(user_kwargs: Dict):
    field_names = {f.name for f in fields(InitialWidgetValues)}
    init_user_kwargs = {k: v for k, v in user_kwargs.items() if k in field_names}

    # remove any used keyword args from the original dictionary, otherwise we will run into an error
    for k in init_user_kwargs.keys():
        user_kwargs.pop(k)

    return InitialWidgetValues(**init_user_kwargs)


def _make_widgets(column_names: List, user_kwargs: Dict) -> Dict:
    widget_defaults = _get_initial_widget_values(user_kwargs)

    # check wether selected keys are available in DataFrame
    widget_defaults.x = widget_defaults.x if widget_defaults.x in column_names else None
    widget_defaults.y = widget_defaults.y if widget_defaults.y in column_names else None
    widget_defaults.color = (
        widget_defaults.color if widget_defaults.color in column_names else None
    )

    column_names = sorted(column_names) + [None]

    discrete_color_scale_plot_types = (
        constants.PlotType.BOX,
        constants.PlotType.LINE,
        constants.PlotType.ECDF,
    )

    widget_dict = dict(
        x=widgets.Dropdown(
            options=column_names, value=widget_defaults.x, description="x"
        ),
        y=widgets.Dropdown(
            options=column_names, value=widget_defaults.y, description="y"
        ),
        color=widgets.Dropdown(
            options=column_names, value=widget_defaults.color, description="color"
        ),
        type=widgets.Dropdown(
            options=[member.value for member in constants.PlotType],
            value=widget_defaults.type,
            description="type",
        ),
        boxmean=widgets.Checkbox(
            value=widget_defaults.boxmean, description="boxplot: show means"
        ),
        notched=widgets.Checkbox(
            value=widget_defaults.notched, description="boxplot: notched"
        ),
        symbol=widgets.Dropdown(
            options=column_names,
            value=widget_defaults.symbol,
            description="symbol",
            disabled=widget_defaults.type
            not in (constants.PlotType.SCATTER, constants.PlotType.LINE),
        ),
        log_x=widgets.Checkbox(value=widget_defaults.log_x, description="log(x)"),
        log_y=widgets.Checkbox(value=widget_defaults.log_y, description="log(y)"),
        points=widgets.Dropdown(
            options=[member.value for member in constants.Points],
            value=widget_defaults.points,
            description="points",
            disabled=widget_defaults.type != constants.PlotType.BOX,
        ),
        barmode=widgets.Dropdown(
            options=[member.value for member in constants.BarMode],
            value=widget_defaults.barmode,
            description="barmode",
            disabled=widget_defaults.type != constants.PlotType.BAR,
        ),
        title=widgets.Text(value="", description="title"),
        y_axis_title=widgets.Text(value="", description="y axis label"),
        x_axis_title=widgets.Text(value="", description="x axis label"),
        height=widgets.BoundedIntText(
            value=0,  # default
            min=0,
            max=5000,
            step=10,
            description="Height:",
        ),
        width=widgets.BoundedIntText(
            value=0,  # default
            min=0,
            max=3000,
            step=10,
            description="Width:",
        ),
        sort_axis=widgets.ToggleButtons(
            options=[member.value for member in constants.SortAxis],
            style={"button_width": "auto"},
        ),
        sort_metric=widgets.Dropdown(
            options=[member.value for member in constants.SortMetric],
            value=widget_defaults.sort_metric,
            description="sort metric",
        ),
        show_legend=widgets.Checkbox(
            value=widget_defaults.show_legend, description="legend"
        ),
        reverse_ecdf=widgets.Checkbox(
            value=widget_defaults.reverse_ecdf,
            disabled=widget_defaults.type != constants.PlotType.ECDF,
            description="reverse ecdf",
        ),
        palette_type=widgets.Dropdown(
            options=[member.value for member in constants.PaletteType],
            value=widget_defaults.palette_type,
            description="Palette type",
        ),
        palette_name=widgets.Dropdown(
            options=_get_palettes(widget_defaults.palette_type),
            value=_get_default_palette(widget_defaults.palette_type),
            description="Palette",
        ),
        color_scale=widgets.ToggleButtons(
            options=[member.value for member in constants.ColorScale],
            value=constants.ColorScale.DISCRETE,
            disabled=widget_defaults.type in discrete_color_scale_plot_types,
            style={"button_width": "auto"},
        ),
        color_categorical=widgets.Checkbox(
            value=False, description="Categorical color?"
        ),
    )

    # used to disable one widget based on the value of another
    def type_change(change):
        if change["new"] in discrete_color_scale_plot_types:
            widget_dict["color_scale"].value = constants.ColorScale.DISCRETE
        widget_dict["color_scale"].disabled = (
            change["new"] in discrete_color_scale_plot_types
        )
        widget_dict["symbol"].disabled = change["new"] not in (
            constants.PlotType.SCATTER,
            constants.PlotType.LINE,
        )
        widget_dict["points"].disabled = change["new"] != constants.PlotType.BOX
        widget_dict["barmode"].disabled = change["new"] != constants.PlotType.BAR
        widget_dict["boxmean"].disabled = change["new"] != constants.PlotType.BOX
        widget_dict["notched"].disabled = change["new"] != constants.PlotType.BOX
        widget_dict["reverse_ecdf"].disabled = change["new"] != constants.PlotType.ECDF
        widget_dict["y"].disabled = change["new"] == constants.PlotType.ECDF
        widget_dict["sort_axis"].disabled = change["new"] == constants.PlotType.ECDF
        widget_dict["sort_metric"].disabled = change["new"] == constants.PlotType.ECDF

    widget_dict["type"].observe(type_change, names="value")

    def palette_type_change(change):
        print("new val", change["new"], "first", _get_palettes(change["new"])[0])
        widget_dict["palette_name"].options = _get_palettes(change["new"])

    widget_dict["palette_type"].observe(palette_type_change, names="value")

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


_fig = None


def get_plotly_fig():
    return _fig


def _get_category_orders(df, x, y, sort_axis, sort_metric):
    group_col, value_col = (y, x) if sort_axis == constants.SortAxis.SORT_X else (x, y)
    return {
        group_col: df.groupby(group_col)[value_col]
        .apply(sort_metric)
        .sort_values()
        .index.to_list()
    }


def _make_plot_function(df: pd.DataFrame, **kwargs):
    def _plot(
        x,
        y,
        color,
        type,
        symbol,
        log_x,
        log_y,
        title,
        x_axis_title,
        y_axis_title,
        points,
        barmode,
        height,
        width,
        sort_axis,
        sort_metric,
        show_legend,
        boxmean,
        notched,
        reverse_ecdf,
        palette_type,
        palette_name,
        color_scale,
        color_categorical,
    ):
        global _fig

        palette = _get_palette(palette_type, palette_name)
        common_kwargs = dict(
            x=x,
            y=y,
            color=color,
            log_x=log_x,
            log_y=log_y,
            title=title,
        )
        if color_scale == constants.ColorScale.DISCRETE:
            common_kwargs["color_discrete_sequence"] = palette
        else:
            common_kwargs["color_continuous_scale"] = palette
        data = df.copy()
        if color_categorical:
            data[color] = pd.Categorical(
                data[color],
                categories=sorted(data[color].unique().tolist()),
                ordered=True,
            )
        if sort_metric:
            with contextlib.suppress(Exception):
                common_kwargs["category_orders"] = _get_category_orders(
                    data, x, y, sort_axis, sort_metric
                )

        _fig = None
        if type == "box":
            _fig = px.box(data, **common_kwargs, points=points, **kwargs)
            if boxmean:
                _fig.update_traces(boxmean=True)
            if notched:
                _fig.update_traces(notched=True)
        elif type == "bar":
            _fig = px.bar(data, **common_kwargs, barmode=barmode, **kwargs)
        elif type == "scatter":
            _fig = px.scatter(data, **common_kwargs, symbol=symbol, **kwargs)
        elif type == "line":
            _fig = px.line(data, **common_kwargs, symbol=symbol, **kwargs)
        elif type == "ecdf":
            common_kwargs.pop("y", None)
            ecdfmode = "complementary" if reverse_ecdf else "standard"
            _fig = px.ecdf(
                data, **common_kwargs, ecdfmode=ecdfmode, ecdfnorm="percent", **kwargs
            )
        if _fig:
            updates = {}
            if x_axis_title:
                updates["xaxis_title"] = x_axis_title
            if y_axis_title:
                updates["yaxis_title"] = y_axis_title
            if height:
                updates["height"] = height
            if width:
                updates["width"] = width
            updates["showlegend"] = show_legend
            updates["margin"] = {"t": 50}
            updates["title"] = {
                "x": 0.5,  # 0 = far left; 0.5 = center; 1 = far right
                "xanchor": "center",  # ensures text is centered around x=0.5
            }
            if updates:
                _fig.update_layout(updates)
            _fig.show()

    return _plot


def plot(
    df: pd.DataFrame,
    ignored_params=("TimeLimit", "SoftMemLimit"),
    **kwargs,
):
    """plot different chart types to compare performance and see performance variability across random seeds

    uses Plotly express; all available keyword arguments can be passed through to px.bar(), px.scatter(), etc.
    """
    with contextlib.suppress(Exception):
        df = _add_pretty_param_labels(df, ignored_params)

    widget_dict = _make_widgets(df.columns.tolist(), kwargs)

    def _make_heading(text):
        return widgets.HTML(
            f"<h3 style='text-align:left; padding-left: 5em;'>{text}</h3>"
        )

    parameters_header = _make_heading("Parameters")
    layout_header = _make_heading("Layout Controls")
    toggles_header = _make_heading("Toggles")
    palette_header = _make_heading("Palette")

    left_col_widgets = widgets.VBox(
        [
            parameters_header,
            widget_dict["x"],
            widget_dict["y"],
            widget_dict["color"],
            widget_dict["type"],
            widget_dict["points"],
            widget_dict["barmode"],
            widget_dict["symbol"],
        ]
    )

    centered_sort_axis_buttons = widgets.HBox(
        [widget_dict["sort_axis"]], layout=widgets.Layout(justify_content="center")
    )
    centered_color_scale_buttons = widgets.HBox(
        [widget_dict["color_scale"]], layout=widgets.Layout(justify_content="center")
    )

    right_col_widgets = widgets.VBox(
        [
            layout_header,
            widget_dict["title"],
            widget_dict["y_axis_title"],
            widget_dict["x_axis_title"],
            widget_dict["height"],
            widget_dict["width"],
            widget_dict["sort_metric"],
            centered_sort_axis_buttons,
        ]
    )

    toggle_widgets = widgets.VBox(
        [
            toggles_header,
            widget_dict["boxmean"],
            widget_dict["notched"],
            widget_dict["reverse_ecdf"],
            widget_dict["show_legend"],
            widget_dict["log_x"],
            widget_dict["log_y"],
        ]
    )

    palette_widgets = widgets.VBox(
        [
            palette_header,
            widget_dict["palette_type"],
            widget_dict["palette_name"],
            centered_color_scale_buttons,
            widget_dict["color_categorical"],
        ]
    )

    ui = widgets.HBox(
        [left_col_widgets, right_col_widgets, toggle_widgets, palette_widgets],
        layout=widgets.Layout(
            display="flex",
            flex_flow="row wrap",  # key part: enables wrapping
            justify_content="center",
        ),
    )

    output = widgets.interactive_output(
        _make_plot_function(df, **kwargs),
        widget_dict,
    )

    spacer = widgets.Box(layout=widgets.Layout(height="40px"))
    container = widgets.VBox(
        [
            ui,
            spacer,
            output,
        ],
    )

    display(container)
