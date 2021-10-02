import json
import pathlib
import re
from functools import lru_cache
from functools import partial


re_parameter_column = re.compile(r"(.*) \(Parameter\)")
defaults_dir = pathlib.Path(__file__).parent.joinpath("defaults")


@lru_cache()
def load_defaults(version):
    version_file = defaults_dir.joinpath(f"{version}.json")
    if not version_file.exists():
        # Fall back to 912 defaults.
        version_file = defaults_dir.joinpath("912.json")
    with version_file.open() as infile:
        return json.load(infile)


def fill_for_version(group, parameter_columns):
    parameter_defaults = load_defaults(
        version=group["Version"].iloc[0].replace(".", "")
    )
    for column in parameter_columns:
        default = parameter_defaults.get(re_parameter_column.match(column).group(1))
        if default is not None:
            group[column] = group[column].fillna(default).astype(type(default))
    return group


def fill_default_parameters(summary):
    """If we leave defaults for a parameter .assign(
            **{column: lambda df: dfas NaN, plotly seems to ignore these
    records in the plot. So we should fill these values with the actual default.
    """
    parameter_columns = [
        column
        for column, series in summary.items()
        if re_parameter_column.match(column) and series.isnull().any()
    ]
    # TODO test cases where there are different versions involved
    return summary.groupby("Version").apply(
        partial(fill_for_version, parameter_columns=parameter_columns)
    )


parameter_descriptions = {
    "Method": {
        -1: "-1: Default",
        0: "0: Primal Simplex",
        1: "1: Dual Simplex",
        2: "2: Barrier",
        3: "3: Nondeterministic Concurrent",
        4: "4: Det. Concurrent",
        5: "5: Det. Conc. Simplex",
    },
    "DegenMoves": {
        -1: "-1: Automatic",
        0: "0: Disabled",
    },
    "Presolve": {
        -1: "-1: Automatic",
        0: "0: Off",
        1: "1: Conservative",
        2: "2: Aggressive",
    },
}


def add_categorical_descriptions(summary):
    """Adds extra columns with informative labels for some columns.
    This is useful for things like 'method' where treating it as a number means
    (a) the plot is hard to read, and (b) there are unnecessary gaps in the plot
    if you use e.g. method = 1, 3, 5. Thus better to have a categorical column
    to play with here. Downside is the order is not guaranteed..."""
    parameters = [
        (parameter, column)
        for column in summary.columns
        if (match := re_parameter_column.match(column))
        and (parameter := match.group(1)) in parameter_descriptions
    ]
    for parameter, column in parameters:
        summary = summary.assign(
            **{
                parameter: lambda df: (
                    df[column].map(parameter_descriptions[parameter]).astype("category")
                )
            }
        )
    return summary
