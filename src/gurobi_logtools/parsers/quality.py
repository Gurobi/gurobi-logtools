import re

from gurobi_logtools.parsers.util import (
    float_pattern,
    ParseResult,
    Parser,
    typeconvert_groupdict,
)


class QualityParser(Parser):
    start_pattern = re.compile(r"Solution quality statistics.*")
    intermediate_pattern = re.compile(r"  Maximum violation.*")
    patterns = [
        re.compile(rf"    Bound\s+: (?P<BoundVio>{float_pattern}).*"),
        re.compile(rf"    Constraint\s+: (?P<ConstrVio>{float_pattern}).*"),
        re.compile(rf"    Dual\s+: (?P<DualVio>{float_pattern}).*"),
        re.compile(rf"    Complementarity\s+: (?P<ComplVio>{float_pattern}).*"),
        re.compile(rf"    Integrality\s+: (?P<IntVio>{float_pattern}).*"),
    ]

    def __init__(self):
        self._summary = {}
        self._started = False

    def parse(self, line) -> ParseResult:
        if not self._started:
            start_match = QualityParser.start_pattern.match(line)
            if start_match:
                self._started = True
                return ParseResult(matched=True)
            return ParseResult(matched=False)

        if QualityParser.intermediate_pattern.match(line):
            return ParseResult(matched=True)

        for pattern in QualityParser.patterns:
            match = pattern.match(line)
            if match:
                parse_result = typeconvert_groupdict(match)
                self._summary.update(parse_result)
                return ParseResult(parse_result)

        return ParseResult(matched=False)

    def get_summary(self):
        return self._summary
