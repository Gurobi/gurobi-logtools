import re
from typing import Any, Dict

from gurobi_logtools.parsers.util import Parser, typeconvert_groupdict


class TerminationParser(Parser):
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
            r"(?P<INTERRUPTED>(Interrupt request received|Solve interrupted))(?: \\(error code (?P<ErrorCode>[^\\)]+)\\))?",
        ),
        re.compile(r"Solution count (?P<SolCount>\d+)"),
        re.compile(
            r"Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)",
        ),
        re.compile(r"(?P<WORK_LIMIT>Work limit reached)"),
        re.compile(r"(?P<MEM_LIMIT>Memory limit reached)"),
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
        "MEM_LIMIT",
        "WORK_LIMIT",
    ]

    def __init__(self):
        self._summary: Dict[str, Any] = {}

    def parse(self, line: str) -> Dict[str, Any]:
        """Return True if the line is matched by some pattern.

        Args:
            line (str): A line in the log file.

        Returns:
           Dict[str, Any]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.

        """
        for pattern in TerminationParser.patterns:
            match = pattern.match(line)
            if match:
                for key, value in typeconvert_groupdict(match).items():
                    if key in TerminationParser.status:
                        self._summary.update({"Status": key})
                    else:
                        self._summary.update({key: value})
                return self._summary.copy()
        return {}

    def get_summary(self) -> Dict:
        """Return the current parsed summary."""
        return self._summary
