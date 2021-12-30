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
        self.current_parser = None
        self.future_parsers = []

    def start_parsing(self, line: str) -> bool:
        """The start of a log is the start of the header, so that's all that
        needs to be checked."""
        if self.header_parser.start_parsing(line):
            self.current_parser = self.header_parser
            self.future_parsers = [
                self.presolve_parser,
                self.norel_parser,
                self.nodelog_parser,
            ]
            return True
        return False

    def continue_parsing(self, line: str) -> bool:
        # watch for log termination (or have a termination parser?)
        assert self.current_parser not in self.future_parsers
        # First check if any future parsers want to take over.
        for i, parser in enumerate(self.future_parsers):
            if parser.start_parsing(line):
                self.current_parser = parser
                trigger = i
                break
        else:
            trigger = None
        # If no-one took over, pass to the current parser.
        if trigger is None:
            # this assert can fail; just don't have a test for it yet
            assert self.current_parser is not None
            if not self.current_parser.continue_parsing(line):
                self.current_parser = None
                if not self.future_parsers:
                    return False
        # Control passed to a future parser. Shorten the list.
        else:
            self.future_parsers = self.future_parsers[i + 1 :]
        return True
