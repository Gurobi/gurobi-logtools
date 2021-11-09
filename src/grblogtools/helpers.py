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


PARAMETER_DESCRIPTIONS = {
    "Method (Parameter)": {
        -1: "-1: Default",
        0: "0: Primal Simplex",
        1: "1: Dual Simplex",
        2: "2: Barrier",
        3: "3: Nondeterministic Concurrent",
        4: "4: Deterministic Concurrent",
        5: "5: Deterministic Concurrent Simplex",
    },
    "Presolve (Parameter)": {
        -1: "-1: Automatic",
        0: "0: Off",
        1: "1: Conservative",
        2: "2: Aggressive",
    },
    "Cuts (Parameter)": {
        -1: "-1: Automatic",
        0: "0: Off",
        1: "1: Moderate",
        2: "2: Aggressive",
        3: "3: Very aggressive",
    },
    "MIPFocus (Parameter)": {
        0: "0: Balanced",
        1: "1: Feasibility",
        2: "2: Optimality",
        3: "3: Bound",
    },
}


def add_categorical_descriptions(summary):
    """Replace some columns with categorical descriptions if available in the
    PARAMETER_DESCRIPTIONS dictionary. Modifies :summary in place."""
    parameter_columns = [
        column for column in summary.columns if column in PARAMETER_DESCRIPTIONS
    ]
    for column in parameter_columns:
        summary[column] = (
            summary[column].map(PARAMETER_DESCRIPTIONS[column]).astype("category")
        )
    return summary
