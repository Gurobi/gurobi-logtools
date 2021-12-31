from grblogtools.header_parser import HeaderParser
from grblogtools.nodelog import NodeLogParser
from grblogtools.norel import NoRelParser
from grblogtools.presolve_parser import PresolveParser


class SingleLogParser:
    def __init__(self):

        # Parsers in sequence.
        self.header_parser = HeaderParser()
        self.presolve_parser = PresolveParser()
        self.norel_parser = NoRelParser()
        # Add relaxation/continuous model parser here
        self.nodelog_parser = NodeLogParser()

        # State
        self.current_parser = self.header_parser
        self.future_parsers = [
            self.presolve_parser,
            self.norel_parser,
            self.nodelog_parser,
        ]

    def get_summary(self):
        summary = {}
        summary.update(self.header_parser.get_summary())
        summary.update(self.presolve_parser.get_summary())
        summary.update(self.norel_parser.get_summary())
        summary.update(self.nodelog_parser.get_summary())
        return summary

    def start_parsing(self, line: str) -> bool:
        """The start of a log is the start of the header, so that's all that
        needs to be checked."""
        assert self.current_parser is self.header_parser
        return self.current_parser.start_parsing(line)

    def continue_parsing(self, line: str) -> bool:
        assert self.current_parser not in self.future_parsers
        # First try the current parser.
        matched_line = self.current_parser.continue_parsing(line)
        if matched_line:
            return True
        # Check if any future parsers should take over.
        for i, parser in enumerate(self.future_parsers):
            if parser.start_parsing(line):
                self.current_parser = parser
                self.future_parsers = self.future_parsers[i + 1 :]
                return True
        return False
