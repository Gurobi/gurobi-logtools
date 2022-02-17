import re
from functools import partial
from pathlib import Path

from grblogtools.parameters import load_defaults, load_descriptions

re_parameter_column = re.compile(r"(.*) \(Parameter\)")


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
    """Fill NaN parameter values with the actual default value."""
    parameter_columns = [
        column
        for column, series in summary.items()
        if re_parameter_column.match(column) and series.isnull().any()
    ]
    # TODO test cases where there are different versions involved
    return summary.groupby("Version").apply(
        partial(fill_for_version, parameter_columns=parameter_columns)
    )


def fill_for_version_nosuffix(group):
    parameter_defaults = load_defaults(
        version=group["Version"].iloc[0].replace(".", "")
    )
    for parameter in group.columns:
        default = parameter_defaults.get(parameter)
        if default is not None:
            group[parameter] = group[parameter].fillna(default).astype(type(default))
    return group


def fill_default_parameters_nosuffix(parameters):
    """Fill defaults for Version and parameter cols with no (Parameter) suffix."""
    return parameters.groupby("Version").apply(fill_for_version_nosuffix)


def add_categorical_descriptions(summary):
    """Replace some columns with categorical descriptions if available.

    It modifies the summary dict in place.
    """
    descriptions = load_descriptions()
    parameter_columns = [column for column in summary.columns if column in descriptions]
    for column in parameter_columns:
        summary[column] = summary[column].map(descriptions[column]).astype("category")
    return summary


def strip_model_and_seed(row):
    """Return the Log name.

    If the log path contains the model name, return everything to the left.
    Otherwise, just return the log stem.

    i.e. with Model = 'glass4'
        data/912-Cuts0-glass4-0.log -> 912-Cuts0
        data/some-log.log -> some-log
    """
    if row["Model"] is None:
        return None
    log_stem = Path(row["LogFilePath"]).stem
    run, mid, _ = log_stem.partition(row["Model"])
    if mid and run:
        return run.rstrip("-")
    return log_stem
