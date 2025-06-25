import contextlib
from dataclasses import dataclass, fields
from typing import Dict, List, Optional

import ipywidgets as widgets
import pandas as pd
import plotly.express as px
from IPython.display import display

from gurobi_logtools import constants
from gurobi_logtools.colors import _get_default_palette, _get_palette, _get_palettes


@dataclass
class WidgetValues:
    """
    This class is used to both define default values for widgets, and enable load/save functionality.
    """

    x: str = "Runtime"
    y: str = "Parameters"
    color: str = "Parameters"
    type: constants.PlotType = constants.PlotType.BOX.value
    symbol: Optional[str] = None
    log_x: bool = False
    log_y: bool = False
    points: constants.Points = constants.Points.ALL.value
    barmode: constants.BarMode = constants.BarMode.GROUP.value
    title: str = ""
    x_axis_label: str = ""
    y_axis_label: str = ""
    height: int = 0
    width: int = 0
    show_legend: bool = False
    sort_metric: Optional[constants.SortMetric] = constants.SortMetric.NONE.value
    sort_field: Optional[str] = None
    sort_axis: constants.SortAxis = constants.SortAxis.SORT_Y
    boxmean: bool = False
    notched: bool = False
    reverse_ecdf: bool = False
    palette_type: constants.PaletteType = constants.PaletteType.QUALITATIVE.value
    palette_name: str = None
    color_scale: constants.ColorScale = constants.ColorScale.DISCRETE.value
    color_categorical: bool = False
    ignore_params: str = "SoftMemLimit TimeLimit"
    query: str = ""


# global variable used to hold a single instance of
_saved_widget_values: Optional[WidgetValues] = None


def _get_initial_widget_values(user_kwargs: Dict):
    field_names = {f.name for f in fields(WidgetValues)}
    init_user_kwargs = {k: v for k, v in user_kwargs.items() if k in field_names}

    # remove any used keyword args from the original dictionary, otherwise we will run into an error
    for k in init_user_kwargs.keys():
        user_kwargs.pop(k)

    return WidgetValues(**init_user_kwargs)


def _make_widgets(column_names: List, user_kwargs: Dict) -> Dict:
    widget_defaults = _get_initial_widget_values(user_kwargs)

    # 'Parameters' will be a special column available from the plot UI.
    #  It is intended for use as an 'aesthetic' label.  It needs to be manually added
    #  here so that the defaults can use it.  We then sort by lower case alphabetical order.
    column_names = sorted(column_names + ["Parameters"], key=str.lower) + [None]

    # check wether selected keys are available in DataFrame
    widget_defaults.x = widget_defaults.x if widget_defaults.x in column_names else None
    widget_defaults.y = widget_defaults.y if widget_defaults.y in column_names else None
    widget_defaults.color = (
        widget_defaults.color if widget_defaults.color in column_names else None
    )

    discrete_color_scale_plot_types = (
        constants.PlotType.BOX,
        constants.PlotType.LINE,
        constants.PlotType.ECDF,
    )

    # This dictionary of widgets makes it easy to retrieve widgets later.
    # Some of these widgets will have values that feed into the plot function,
    # some do not (such as swap_axes, or save_config).
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
        swap_axes=widgets.Button(
            description="Swap axes",
            disabled=False,
        ),
        save_config=widgets.Button(
            description="Save config",
            disabled=False,
            style={"button_width": "auto"},
        ),
        load_config=widgets.Button(
            description="Load config",
            disabled=False,
            style={"button_width": "auto"},
        ),
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
        title=widgets.Text(value=widget_defaults.title, description="title"),
        y_axis_label=widgets.Text(
            value=widget_defaults.y_axis_label, description="y axis label"
        ),
        x_axis_label=widgets.Text(
            value=widget_defaults.x_axis_label, description="x axis label"
        ),
        height=widgets.BoundedIntText(
            value=widget_defaults.height,  # default
            min=0,
            max=5000,
            step=10,
            description="Height:",
        ),
        width=widgets.BoundedIntText(
            value=widget_defaults.width,  # default
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
        sort_field=widgets.Dropdown(
            options=column_names, value=widget_defaults.x, description="sort field"
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
            value=widget_defaults.color_scale,
            disabled=widget_defaults.type in discrete_color_scale_plot_types,
            style={"button_width": "auto"},
        ),
        color_categorical=widgets.Checkbox(
            value=widget_defaults.color_categorical, description="Categorical color?"
        ),
        query=widgets.Textarea(
            description="", disabled=False, rows=1, layout=widgets.Layout(padding="0em")
        ),
        ignore_params=widgets.Textarea(
            description="",
            value=widget_defaults.ignore_params,
            disabled=False,
            rows=1,
        ),
    )

    def type_change(change):
        # This function is a callback used to disable one widget based on the value of another
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
        widget_dict["sort_field"].disabled = change["new"] == constants.PlotType.ECDF

    widget_dict["type"].observe(type_change, names="value")

    def palette_type_change(change):
        # This function changes the palettes available in the dropdown when the palette type changes
        widget_dict["palette_name"].options = _get_palettes(change["new"])

    widget_dict["palette_type"].observe(palette_type_change, names="value")

    def swap_axes_press(button_instance):
        # Switches necessary widget values to swap axes.  button_instance is ignored but
        # necessary for signature of function used in on_click.

        def _swap(s1, s2):
            w = widget_dict
            w[s1].value, w[s2].value = w[s2].value, w[s1].value

        _swap("x", "y")
        _swap("log_x", "log_y")
        _swap("x_axis_label", "y_axis_label")

        widget_dict["sort_axis"].value = (
            constants.SortAxis.SORT_X
            if widget_dict["sort_axis"].value == constants.SortAxis.SORT_Y
            else constants.SortAxis.SORT_Y
        )

    widget_dict["swap_axes"].on_click(swap_axes_press)

    def save_widget_values(button_instance):
        # button_instance is ignored but necessary for signature of function used in on_click
        global _saved_widget_values
        _saved_widget_values = WidgetValues(
            **{f.name: widget_dict[f.name].value for f in fields(WidgetValues)}
        )

    widget_dict["save_config"].on_click(save_widget_values)

    def load_widget_values(button_instance):
        global _saved_widget_values

        if _saved_widget_values is None:
            return

        field_names = {f.name for f in fields(WidgetValues) if f.name != "palette_name"}
        for name in field_names:
            widget_dict[name].value = getattr(_saved_widget_values, name)
        widget_dict["palette_name"].value = _saved_widget_values.palette_name

    widget_dict["load_config"].on_click(load_widget_values)

    return widget_dict


def _add_pretty_param_labels(df: pd.DataFrame, ignored_params: str) -> pd.DataFrame:
    # 'Parameters' will be a special column available from the plot UI.
    #  It is derived from ChangedParams and is intended for use as an 'aesthetic' label.

    if "ChangedParams" not in df.columns:
        # the fact we return a copy is important here.  It is not ideal, but it is convenient.
        return df.copy()
    ignored_params = ignored_params.lower().replace("\n", " ").replace(",", " ").split()
    pretty_params = (
        df["ChangedParams"]
        .map(
            lambda d: "<br>".join(
                [f"{k}={v}" for k, v in d.items() if k.lower() not in ignored_params]
            )
        )
        .replace("", "Defaults")
    )
    return df.assign(Parameters=pretty_params)


# Global variable used to keep track of figure related to the last plot
_fig = None


def get_plotly_fig():
    return _fig


def save_plot(filepath: str) -> None:
    """Will save plot to file.  Filetype inferred from extension.

    A variety of filetypes are supported, including png, svg, pdf and html.
    Requires `kaleido` Python package and Chrome.  See https://plotly.com/python/static-image-export/

    Parameters
    ----------
    filepath : str
    """
    temp = filepath.split(".")
    if len(temp) <= 1:
        raise ValueError("filepath needs a file extension")
    if temp[-1] == "html":
        get_plotly_fig().write_html(filepath)
    else:
        get_plotly_fig().write_image(filepath)


def _get_category_orders(df, x, y, sort_axis, sort_metric, sort_field):
    # the return value of this function will be used as an argument to the `category_orders` parameter
    # in plotly functions, e.g. https://plotly.com/python-api-reference/generated/plotly.express.box.html#plotly.express.box
    assert sort_metric is not None
    if sort_field is None:
        group_col, value_col = (
            (x, y) if sort_axis == constants.SortAxis.SORT_X else (y, x)
        )
    else:
        group_col, value_col = (
            (x, sort_field)
            if sort_axis == constants.SortAxis.SORT_X
            else (y, sort_field)
        )

    return {
        group_col: df.groupby(group_col)[value_col]
        .apply(sort_metric)
        .sort_values()
        .index.to_list()
    }


def _make_plot_function(df: pd.DataFrame, **kwargs):
    # using closure so that dataframe and user key word arguments are captured in the plotting function
    def _plot(
        x,
        y,
        color,
        type,
        symbol,
        log_x,
        log_y,
        title,
        x_axis_label,
        y_axis_label,
        points,
        barmode,
        height,
        width,
        sort_axis,
        sort_metric,
        sort_field,
        show_legend,
        boxmean,
        notched,
        reverse_ecdf,
        palette_type,
        palette_name,
        color_scale,
        color_categorical,
        query,
        ignore_params,
    ):
        global _fig

        palette = _get_palette(palette_type, palette_name)

        # common keyword arguments to all plotly.express plotting functions (eg. box, scatter, line etc)
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

        # possibly add the Parameters column here
        # In any case `data` will be a copy which is important to avoid errors, and avoid changing
        # the original dataframe.
        data = _add_pretty_param_labels(df, ignore_params)

        with contextlib.suppress(Exception):
            # suppress the error, as we don't want an error while the user is creating their query string
            data = data.query(query)

        if color_categorical:
            # convert color column to a categorical type
            data[color] = pd.Categorical(
                data[color],
                categories=sorted(data[color].unique().tolist()),
                ordered=True,
            )
        if sort_metric:
            with contextlib.suppress(Exception):
                # some sort related values will not make sense, e.g. the mean of strings.
                # We prefer to just ignore this rather than cause errors, under assumption the user
                # is making multiple changes to reach something which does make sense.
                common_kwargs["category_orders"] = _get_category_orders(
                    data,
                    x,
                    y,
                    sort_axis,
                    sort_metric,
                    sort_field,
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
            if x_axis_label:
                updates["xaxis_title"] = x_axis_label
            if y_axis_label:
                updates["yaxis_title"] = y_axis_label
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
    **kwargs,
):
    """Plot different chart types to compare performance, and explore correlations.

    A major use case is to compare parameters vs runtime and assess performance variability across random seeds.

    This functionality is built upon Plotly express; all available keyword arguments can be passed through to px.bar(), px.scatter(), etc.

    Parameters
    ----------
    df : pd.DataFrame
    ** kwargs
        Key word arguments that can be used to either prepopulate widget values, e.g. y="ObjVal",
        or otherwise passed to the underlying Plotly express function.
    """

    widget_dict = _make_widgets(df.columns.tolist(), kwargs)

    def _make_heading(text):
        return widgets.HTML(
            f"<h3 style='text-align:left; padding-left: 5em;'>{text}</h3>"
        )

    parameters_header = _make_heading("Parameters")
    layout_header = _make_heading("Layout Controls")
    toggles_header = _make_heading("Toggles")
    palette_header = _make_heading("Palette")

    column_1_widgets = widgets.VBox(
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

    column_2_widgets = widgets.VBox(
        [
            layout_header,
            widget_dict["title"],
            widget_dict["y_axis_label"],
            widget_dict["x_axis_label"],
            widget_dict["height"],
            widget_dict["width"],
            widget_dict["sort_field"],
            widget_dict["sort_metric"],
            widgets.HBox(
                [widget_dict["sort_axis"]],
                layout=widgets.Layout(justify_content="center"),
            ),
        ]
    )

    columns_3_widgets = widgets.VBox(
        [
            toggles_header,
            widget_dict["boxmean"],
            widget_dict["notched"],
            widget_dict["reverse_ecdf"],
            widget_dict["show_legend"],
            widget_dict["log_x"],
            widget_dict["log_y"],
            widgets.HBox(
                [widget_dict["swap_axes"]],
                layout=widgets.Layout(
                    display="flex",
                    justify_content="center",
                ),
            ),
            widgets.HBox(
                [widget_dict["save_config"], widget_dict["load_config"]],
                layout=widgets.Layout(
                    width="100%",
                ),
            ),
        ]
    )

    columns_4_widgets = widgets.VBox(
        [
            palette_header,
            widget_dict["palette_type"],
            widget_dict["palette_name"],
            widgets.HBox(
                [widget_dict["color_scale"]],
                layout=widgets.Layout(display="flex", justify_content="center"),
            ),
            widget_dict["color_categorical"],
            widgets.HTML(
                f"<h4 style='text-align:left; margin: 0px; padding: 0px;'>DataFrame query string</h4>",
            ),
            widget_dict["query"],
            widgets.HTML(
                f"<h4 style='text-align:left;  margin: 0px; padding: 0px;'>Parameters to ignore</h4>",
            ),
            widget_dict["ignore_params"],
        ]
    )

    ui = widgets.HBox(
        [column_1_widgets, column_2_widgets, columns_3_widgets, columns_4_widgets],
        layout=widgets.Layout(
            display="flex",
            flex_flow="row wrap",  # key part: enables wrapping
            justify_content="center",
        ),
    )

    # these widgets don't correspond to plot arguments and need to be removed from
    # the widget dictionary before it is stitched with the plot function via interactive_output()
    widget_dict.pop("swap_axes")
    widget_dict.pop("save_config")
    widget_dict.pop("load_config")

    output = widgets.interactive_output(
        _make_plot_function(df, **kwargs),
        widget_dict,
    )

    # spacer is used to create a bit of space between plot and widgets.
    # This space could be used to dispay messages to the user in the future
    # if this seems useful.
    spacer = widgets.Box(layout=widgets.Layout(height="40px"))
    container = widgets.VBox(
        [
            ui,
            spacer,
            output,
        ],
    )

    display(container)
