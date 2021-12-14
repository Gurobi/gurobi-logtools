import re

from .parser_helpers import ParserLinesMixin

float_pattern = r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?"


def try_float(value):
    try:
        return float(value)
    except ValueError:
        return None


class NodeLogParser(ParserLinesMixin):
    """
    Methods:
        - log_start(line) -> parse a string, returing true if this string
          indicates the start of the norel section
        - parse(line) -> parse a string, return true if this parser should
          continue receiving future log lines

    Attributes:
        - timeline -> list of dicts for log timeline entries (incumbent, bound,
          time, depth, etc)
        - ignored_lines -> count of lines after the log start which were recieved
          but not parsed
    """

    tree_search_log_start = re.compile(r" Expl Unexpl(.*)It/Node Time$")
    tree_search_explored = re.compile(r"Explored \d+ nodes")
    line_types = [
        # tree_search_full_log_line_regex
        re.compile(
            r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Obj>{0})\s+(?P<Depth>\d+)\s+(?P<IntInf>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}))%\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
                float_pattern
            )
        ),
        # tree_search_nodepruned_line_regex
        re.compile(
            r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Pruned>(cutoff|infeasible|postponed))\s+(?P<Depth>\d+)\s+(?P<Incumbent>(-|{0}))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}))%\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
                float_pattern
            )
        ),
        # tree_search_new_solution_heuristic_log_line_regex
        re.compile(
            r"(?P<NewSolution>H)\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>{0})%\s+(?P<ItPerNode>(-|{0}))\s+(?P<Time>\d+)s".format(
                float_pattern
            )
        ),
        # tree_search_new_solution_branching_log_line_regex
        re.compile(
            r"(?P<NewSolution>\*)\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Depth>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>{0})%\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
                float_pattern
            )
        ),
        # tree_search_status_line_regex
        # not sure what this one is for, nothing in testing?
        # re.compile(
        #     r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Obj>-)\s+(?P<Depth>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}%))\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
        #         float_pattern
        #     )
        # ),
    ]

    def __init__(self):
        self.timeline = []
        self.ignored_lines = 0

    def log_start(self, line: str) -> bool:
        return bool(self.tree_search_log_start.match(line))

    def _timeline_entry(self, arg):
        """ Type convert and store log lines. """
        result = {}
        for k, v in arg.items():
            if k in ["CurrentNode", "RemainingNodes", "Depth", "IntInf"]:
                result[k] = int(v)
            elif k in ["BestBd", "Obj", "Time", "Incumbent", "ItPerNode"]:
                result[k] = try_float(v)
            elif k == "Gap":
                gap_value = try_float(v)
                if gap_value is not None:
                    # Record gap as e.g. 0.63 instead of 63%
                    gap_value = gap_value / 100
                result[k] = gap_value
            else:
                result[k] = v
        self.timeline.append(result)

    def parse(self, line: str) -> bool:
        """ Match against all log line formats, exiting on the first match. If
        no match, check for the end line or record an ignored line. """
        if not line.strip():
            return True  # continue
        for regex in self.line_types:
            if match := regex.match(line):
                self._timeline_entry(match.groupdict())
                return True  # continue
        if match := self.tree_search_explored.match(line):
            return False  # stop
        self.ignored_lines += 1
        return True  # continue
