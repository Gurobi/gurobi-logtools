from typing import Iterable


class ParserLinesMixin:
    """Mixin class to help with integration with the current code. Can be
    removed down the line if a parser no longer needs to process lists of
    lines itself.

    Ultimately this would be moved into a testing helper and not used in
    the main code.
    """

    def parse_lines(self, loglines: Iterable[str]):
        """We would not use this method in the main code, just as a
        convenience for testing a class using generic logic."""
        it = iter(loglines)
        for line in it:
            if self.log_start(line):
                # Once the parser indicates start, pass to main method
                # until signalled to stop.
                for line in it:
                    continue_ = self.parse(line)
                    if not continue_:
                        return
