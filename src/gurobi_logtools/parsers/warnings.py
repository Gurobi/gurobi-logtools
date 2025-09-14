import re
from warnings import warn

from gurobi_logtools.constants import StrEnum


class WarningAction(StrEnum):
    IGNORE = "ignore"
    WARN = "warn"
    RAISE = "raise"


class Warnings:
    warning_patterns = [
        re.compile(
            r"Version .* of attribute file unsupported$",
        ),
    ]

    def __init__(self, logfile: str, action: WarningAction = WarningAction.WARN):
        self.logfile = logfile
        self.action: WarningAction = action

    def handle_warning(self, line):
        if self.action == WarningAction.WARN:
            warn(f"\n    {self.logfile}:\n        {line}", RuntimeWarning)
        elif self.action == WarningAction.RAISE:
            raise RuntimeError(f"{self.logfile}:\n    {line}")

    def check(self, line: str) -> None:
        for pattern in self.warning_patterns:
            match = pattern.match(line)
            if match:
                self.handle_warning(line)
                return
