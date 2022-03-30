import datetime
import re
from typing import Iterable

int_regex = re.compile(r"[-+]?\d+$")
float_regex = re.compile(r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?$")
percentage_regex = re.compile(r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?%$")
date_time_regex = re.compile(r"\D+\s\D+\s\d+\s\d+:\d+:\d+\s\d{4}")


def convert_data_types(value):
    """Convert the given value string to the type it matches."""
    if value is None or value == "-":
        # Commonly used sentinel for a missing value in log tables
        return None
    elif int_regex.match(value):
        return int(value)
    elif float_regex.match(value):
        return float(value)
    elif percentage_regex.match(value):
        return float(value.rstrip("%")) / 100
    elif date_time_regex.match(value):
        return datetime.datetime.strptime(value, "%a %b %d %H:%M:%S %Y")
    else:
        return value


def typeconvert_groupdict(match: re.Match):
    """Return the groupdict of a regex match with type converted values."""
    return {k: convert_data_types(v) for k, v in match.groupdict().items()}


def parse_lines(parser, loglines: Iterable[str]):
    """Parse the given lines using the given parser object.

    This function is mainly used in the tests.
    """
    lines = iter(loglines)
    for line in lines:
        parser.parse(line)


def parse_block(parser, log):
    """Parse a multi-line block of text using the given parser object.

    This function is mainly used in the tests.
    """
    parse_lines(parser, log.strip().split("\n"))


def model_type(discrete_vars=0, quad_nonzeros=0, quad_constrs=0):
    """Return the type of the optimization model.

    The model type is MIP, QCP, QP, or LP.
    """
    mtype = ""
    if discrete_vars > 0:
        mtype += "MI"
    if quad_constrs > 0:
        mtype += "QC"
    elif quad_nonzeros > 0:
        mtype += "Q"
    if not mtype:
        return "LP"
    return mtype + "P"
