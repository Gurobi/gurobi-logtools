import re
from typing import Any, Dict

from grblogtools.helpers import convert_data_types, typeconvert_groupdict

float_pattern = r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?"


class NodeLogParser:
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
    tree_search_explored = re.compile(
        r"Explored (?P<NodeCount>\d+) nodes \((?P<IterCount>\d+) simplex iterations\) in (?P<Runtime>[^\s]+) seconds"
    )
    line_types = [
        # tree_search_full_log_line_regex
        re.compile(
            r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Obj>{0})\s+(?P<Depth>\d+)\s+(?P<IntInf>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}%))\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
                float_pattern
            )
        ),
        # tree_search_nodepruned_line_regex
        re.compile(
            r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Pruned>(cutoff|infeasible|postponed))\s+(?P<Depth>\d+)\s+(?P<Incumbent>(-|{0}))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}%))\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
                float_pattern
            )
        ),
        # tree_search_new_solution_heuristic_log_line_regex
        re.compile(
            r"(?P<NewSolution>H)\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>{0}%)\s+(?P<ItPerNode>(-|{0}))\s+(?P<Time>\d+)s".format(
                float_pattern
            )
        ),
        # tree_search_new_solution_branching_log_line_regex
        re.compile(
            r"(?P<NewSolution>\*)\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Depth>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>{0}%)\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
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
    cut_report_start = re.compile(r"Cutting planes:")
    cut_report_line = re.compile(r"  (?P<Name>[\w ]+): (?P<Count>\d+)")

    def __init__(self):
        self._summary = {}
        self._cuts = {}
        self.timeline = []
        self.ignored_lines = 0
        self._complete = False
        self._in_cut_report = False

    def get_summary(self) -> Dict[str, Any]:
        summary = self._summary
        summary.update({f"Cuts: {name}": count for name, count in self._cuts.items()})
        return summary

    def start_parsing(self, line: str) -> bool:
        return bool(self.tree_search_log_start.match(line))

    def continue_parsing(self, line: str) -> bool:
        """Match against all log line formats, exiting on the first match. If
        no match, check for the end line or record an ignored line."""
        for regex in self.line_types:
            match = regex.match(line)
            if match:
                self.timeline.append(typeconvert_groupdict(match))
                return True
        match = self.tree_search_explored.match(line)
        if match:
            self._summary.update(typeconvert_groupdict(match))
            self._complete = True
            self._in_cut_report = False
            return True
        match = self.cut_report_start.match(line)
        if match:
            self._in_cut_report = True
            return True
        if self._in_cut_report:
            match = self.cut_report_line.match(line)
            if match:
                self._cuts[match.group("Name")] = convert_data_types(
                    match.group("Count")
                )
                return True
        if line.strip() and not self._complete:
            self.ignored_lines += 1
        return False
