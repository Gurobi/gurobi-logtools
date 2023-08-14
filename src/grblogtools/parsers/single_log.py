import pathlib

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

    def __init__(self, write_to_dir=None):
        # Parsers in sequence
        self.header_parser = HeaderParser()
        self.presolve_parser = PresolveParser()
        self.norel_parser = NoRelParser()
        self.continuous_parser = ContinuousParser()
        self.nodelog_parser = NodeLogParser()
        self.termination_parser = TerminationParser()

        # State
        self.started = False
        self.closed = False
        self.current_parser = self.header_parser
        self.future_parsers = [
            self.presolve_parser,
            self.norel_parser,
            self.continuous_parser,
            self.nodelog_parser,
        ]

        # Capture lines *if* we plan to write them elsewhere
        self.write_to_dir = pathlib.Path(write_to_dir) if write_to_dir else None
        self.lines = [] if self.write_to_dir else None

    def close(self):
        if self.write_to_dir:
            paramstr = "-".join(
                f"{k}{v}"
                for k, v in sorted(self.header_parser.changed_params().items())
            )
            version = self.header_parser.get_summary().get("Version").replace(".", "")
            model_name = self.header_parser.get_summary().get("ModelName", "unknown")
            seed = self.header_parser.get_parameters().get("Seed", 0)
            if paramstr:
                file_name = f"{version}-{paramstr}-{model_name}-{seed}.log"
            else:
                file_name = f"{version}-{model_name}-s{seed}.log"
            with self.write_to_dir.joinpath(file_name).open("w") as outfile:
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
        summary["ChangedParams"] = self.header_parser.changed_params()
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
                if self.write_to_dir:
                    self.lines.append(line)
            return matched

        if self.write_to_dir:
            self.lines.append(line)

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
