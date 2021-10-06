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
