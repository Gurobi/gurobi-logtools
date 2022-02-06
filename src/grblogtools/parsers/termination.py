import re

from grblogtools.parsers.util import typeconvert_groupdict


class TerminationParser:
    # Termination patterns
    patterns = [
        re.compile(r"ERROR (?P<ErrorCode>[^:]+): (?P<ErrorMessage>.*)$"),
        re.compile(r"\[(?P<ErrorMessage>process terminated with exit code [^\\]]+)\]$"),
        re.compile(r"(?P<TIME_LIMIT>Time limit reached)"),
        re.compile(r"(?P<OPTIMAL>Optimal solution found)(?: \(tolerance .*\))"),
        re.compile(r"(?P<ITERATION_LIMIT>Iteration limit reached)"),
        re.compile(r"(?P<INF_OR_UNBD>Infeasible or unbounded model)"),
        re.compile(r"(?P<INF_OR_UNBD>Model is infeasible or unbounded)"),
        re.compile(r"(?P<UNBOUNDED>Unbounded model)"),
        re.compile(r"(?P<UNBOUNDED>Model is unbounded)"),
        re.compile(r"(?P<INFEASIBLE>Infeasible model)"),
        re.compile(r"(?P<INFEASIBLE>Model is infeasible)"),
        re.compile(r"(?P<SOLUTION_LIMIT>Solution limit reached)"),
        re.compile(r"(?P<NODE_LIMIT>Node limit reached)"),
        re.compile(r"(?P<NUMERIC>Numeric error)"),
        re.compile(r"(?P<NUMERIC>Numerical trouble encountered)"),
        re.compile(r"(?P<CUTOFF>Model objective exceeds cutoff)"),
        re.compile(r"(?P<CUTOFF>Objective cutoff exceeded)"),
        re.compile(r"(?P<USER_OBJ_LIMIT>Optimization achieved user objective limit)"),
        re.compile(
            r"(?P<INTERRUPTED>(Interrupt request received|Solve interrupted))(?: \\(error code (?P<ErrorCode>[^\\)]+)\\))?"
        ),
        re.compile(r"Solution count (?P<SolCount>\d+)"),
        re.compile(
            r"Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)"
        ),
    ]

    status = [
        "OPTIMAL",
        "TIME_LIMIT",
        "ITERATION_LIMIT",
        "INF_OR_UNBD",
        "UNBOUNDED",
        "INFEASIBLE",
        "SOLUTION_LIMIT",
        "NUMERIC",
        "CUTOFF",
        "USER_OBJ_LIMIT",
        "INTERRUPTED",
    ]

    def __init__(self):
        self._summary = {}

    def parse(self, line: str) -> bool:
        """Return True if the line is matched by some pattern.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        for pattern in TerminationParser.patterns:
            match = pattern.match(line)
            if match:
                for key, value in typeconvert_groupdict(match).items():
                    if key in TerminationParser.status:
                        self._summary.update({"Status": key})
                    else:
                        self._summary.update({key: value})
                return True
        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return self._summary
