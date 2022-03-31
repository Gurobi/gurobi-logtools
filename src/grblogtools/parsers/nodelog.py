import re

from grblogtools.parsers.util import convert_data_types, typeconvert_groupdict

float_pattern = r"[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?"


class NodeLogParser:
    tree_search_start = re.compile(r" Expl Unexpl(.*)It/Node Time$")

    tree_search_final_stats = [
        re.compile(
            r"Explored (?P<NodeCount>\d+) nodes \((?P<IterCount>\d+) simplex iterations\) in (?P<Runtime>[^\s]+) seconds"
        ),
        re.compile(
            r"Best objective (?P<ObjVal>[^,]+), best bound (?P<ObjBound>[^,]+), gap (?P<MIPGap>.*)$"
        ),
    ]

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
    ]
    cut_report_start = re.compile(r"Cutting planes:")
    cut_report_line = re.compile(r"  (?P<Name>[\w\- ]+): (?P<Count>\d+)")

    def __init__(self):
        """Initialize the NodeLog parser."""
        self._summary = {}
        self._cuts = {}
        self._progress = []
        self._in_cut_report = False
        self._started = False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        summary = self._summary
        summary.update({f"Cuts: {name}": count for name, count in self._cuts.items()})
        return summary

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """

        for regex in self.tree_search_final_stats:
            match = regex.match(line)
            if match:
                entry = typeconvert_groupdict(match)
                self._summary.update(entry)
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

        # Wait for the header before matching any log lines.
        if not self._started:
            match = self.tree_search_start.match(line)
            if match:
                self._started = True
                return True
            return False

        # Match log lines.
        for regex in self.line_types:
            match = regex.match(line)
            if match:
                self._progress.append(typeconvert_groupdict(match))
                return True

        return False

    def get_progress(self) -> list:
        """Return the progress of the search tree."""
        result = list(self._progress)
        if "Runtime" in self._summary:
            # Final statistics are added as a final tracked line.
            result.append(
                {
                    "Incumbent": self._summary.get("ObjVal"),
                    "BestBd": self._summary.get("ObjBound"),
                    "Gap": self._summary.get("MIPGap"),
                    "CurrentNode": self._summary.get("NodeCount"),
                    "Time": self._summary.get("Runtime"),
                }
            )
        return result
