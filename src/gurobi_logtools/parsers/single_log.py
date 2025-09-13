import pathlib
from typing import List, Optional

from gurobi_logtools.parsers.continuous import ContinuousParser
from gurobi_logtools.parsers.header import HeaderParser
from gurobi_logtools.parsers.nodelog import NodeLogParser
from gurobi_logtools.parsers.norel import NoRelParser
from gurobi_logtools.parsers.presolve import PresolveParser
from gurobi_logtools.parsers.pretree_solutions import PreTreeSolutionParser
from gurobi_logtools.parsers.termination import TerminationParser
from gurobi_logtools.parsers.util import ParseResult, Parser


class SingleLogParser(Parser):
    """This class parses one single log file.

    It expects parse to be called once for each line in a log file.
    """

    _HeaderParser = HeaderParser
    _NoRelParser = NoRelParser
    _NodeLogParser = NodeLogParser
    _TerminationParser = TerminationParser
    _PreTreeSolutionParser = PreTreeSolutionParser

    def __init__(self, write_to_dir=None):
        self.pretree_solution_parser = self._PreTreeSolutionParser()

        # Parsers in sequence
        self.header_parser = self._HeaderParser()
        self.presolve_parser = PresolveParser(self.pretree_solution_parser)
        self.norel_parser = self._NoRelParser()
        self.continuous_parser = ContinuousParser(self.pretree_solution_parser)
        self.nodelog_parser = self._NodeLogParser()
        self.termination_parser = self._TerminationParser()

        # State
        self.started = False
        self.closed = False
        self.current_parser: Parser = self.header_parser
        self.future_parsers = [
            self.presolve_parser,
            self.norel_parser,
            self.continuous_parser,
            self.nodelog_parser,
        ]

        # Capture lines *if* we plan to write them elsewhere
        self.write_to_dir = pathlib.Path(write_to_dir) if write_to_dir else None
        self.lines: Optional[List[str]] = [] if self.write_to_dir else None

    def close(self):
        if self.write_to_dir:
            file_name = self.header_parser._make_file_name()
            with self.write_to_dir.joinpath(file_name).open("w") as outfile:
                if self.lines:
                    outfile.writelines(self.lines)

        self.write_to_dir = None
        self.lines = None
        self.closed = True

    def get_summary(self):
        """Return a summary dict, a merged result of the sub-parser results."""
        summary = {}
        summary.update(self.header_parser.get_summary())
        summary.update(self.presolve_parser.get_summary())
        summary.update(self.norel_parser.get_summary())
        summary.update(self.continuous_parser.get_summary())
        summary.update(self.pretree_solution_parser.get_summary())
        summary.update(self.nodelog_parser.get_summary())
        summary.update(self.termination_parser.get_summary())
        return summary

    def parse(self, line: str) -> ParseResult:
        """Parse the given log line to populate the component parsers in sequence.

        Args:
            line (str): A line in the log file.

        Returns:
           Dict[str, Any]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.

        """
        # Initially, only check the header parser until started
        if not self.started:
            assert self.current_parser is self.header_parser
            parse_result = self.current_parser.parse(line)
            if parse_result:
                self.started = True
                if self.lines is not None:  # i.e. write_to_dir = True
                    self.lines.append(line)
                return parse_result
            return ParseResult(matched=False)

        if self.lines is not None:  # i.e. write_to_dir = True
            self.lines.append(line)

        # First try the current parser
        assert self.current_parser not in self.future_parsers
        if parse_result := self.current_parser.parse(line):
            return parse_result

        # Check if any future parsers should take over
        for i, parser in enumerate(self.future_parsers):
            if parse_result := parser.parse(line):
                self.current_parser = parser
                self.future_parsers = self.future_parsers[i + 1 :]
                return parse_result

        # Check if the line matches any pattern of the termination parser
        if parse_result := self.termination_parser.parse(line):
            return parse_result

        # Nothing matched
        return ParseResult(matched=False)
