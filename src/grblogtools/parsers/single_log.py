from grblogtools.parsers.continuous import ContinuousParser
from grblogtools.parsers.header import HeaderParser
from grblogtools.parsers.nodelog import NodeLogParser
from grblogtools.parsers.norel import NoRelParser
from grblogtools.parsers.presolve import PresolveParser
from grblogtools.parsers.termination import TerminationParser
from grblogtools.parsers.util import model_type


class SingleLogParser:
    """This class parses one single log file.

    It expects parse to be called once for each line in a log file.
    """

    def __init__(self):
        # Parsers in sequence
        self.header_parser = HeaderParser()
        self.presolve_parser = PresolveParser()
        self.norel_parser = NoRelParser()
        self.continuous_parser = ContinuousParser()
        self.nodelog_parser = NodeLogParser()
        self.termination_parser = TerminationParser()

        # State
        self.started = False
        self.current_parser = self.header_parser
        self.future_parsers = [
            self.presolve_parser,
            self.norel_parser,
            self.continuous_parser,
            self.nodelog_parser,
        ]

    def get_summary(self):
        """Return a summary dict, a merged result of the sub-parser results."""
        summary = {}
        summary.update(self.header_parser.get_summary())
        summary.update(self.presolve_parser.get_summary())
        summary.update(self.norel_parser.get_summary())
        summary.update(self.continuous_parser.get_summary())
        summary.update(self.nodelog_parser.get_summary())
        summary.update(self.termination_parser.get_summary())
        summary["ModelType"] = model_type(
            discrete_vars=summary.get("PresolvedNumBinVars", 0)
            + summary.get("PresolvedNumIntVars", 0)
            + summary.get("PresolvedNumSemiContVars", 0)
            + summary.get("PresolvedNumSemiIntVars", 0),
            quad_nonzeros=summary.get("NumQNZs", 0),
            quad_constrs=summary.get("NumQConstrs", 0),
        )
        return summary

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate the component parsers in sequence.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        # Initially, only check the header parser until started
        if not self.started:
            assert self.current_parser is self.header_parser
            matched = self.current_parser.parse(line)
            if matched:
                self.started = True
            return matched

        # First try the current parser
        assert self.current_parser not in self.future_parsers
        if self.current_parser.parse(line):
            return True

        # Check if any future parsers should take over
        for i, parser in enumerate(self.future_parsers):
            if parser.parse(line):
                self.current_parser = parser
                self.future_parsers = self.future_parsers[i + 1 :]
                return True

        # Check if the line matches any pattern of the termination parser
        if self.termination_parser.parse(line):
            return True

        # Nothing matched
        return False
