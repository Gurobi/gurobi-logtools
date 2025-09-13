import datetime
import re
import copy
from typing import Dict, Iterable, Optional, Protocol

float_pattern = r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?"

int_regex = re.compile(r"[-+]?\d+$")
float_regex = re.compile(r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?$")
percentage_regex = re.compile(r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?%$")
date_time_regex = re.compile(r"\D+\s\D+\s\d+\s\d+:\d+:\d+\s\d{4}")


class ParseResult:
    def __init__(self, result: Optional[Dict] = None, matched: bool = False):
        self.result: Optional[Dict] = copy.copy(result)
        if result is not None:
            matched = True
        self.matched: bool = matched

    def __bool__(self):
        return self.matched

    def copy(self):
        return ParseResult(self.result, self.matched)


def convert_data_types(value):
    """Convert the given value string to the type it matches."""
    if value is None or value == "-":
        # Commonly used sentinel for a missing value in log tables
        return None
    if int_regex.match(value):
        return int(value)
    if float_regex.match(value):
        return float(value)
    if percentage_regex.match(value):
        return float(value.rstrip("%")) / 100
    if date_time_regex.match(value):
        return datetime.datetime.strptime(value, "%a %b %d %H:%M:%S %Y")
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


class Parser(Protocol):
    def parse(self, line: str) -> ParseResult: ...
