from typing import Dict
from gurobi_logtools.parsers.presolve import PresolveParser
from gurobi_logtools.parsers.single_log_base import SingleLogBase
from gurobi_logtools.parsers.util import (
    float_pattern,
    ParseResult,
    Parser,
    typeconvert_groupdict,
)
import re


class ObjNLogParser(SingleLogBase):
    """This class parses one single log file.

    It expects parse to be called once for each line in a log file.
    """

    _add_model_type = False

    def get_progress(self, section):
        progress = super().get_progress(section).copy()
        objn = self.header_parser._summary.get("ObjNPass", 0)
        for update in progress:
            update["ObjNPass"] = objn
        return progress


class InitialPresolveParser(PresolveParser):
    # The pattern indicating the initialization of the parser
    presolve_start_pattern = re.compile(
        r"Multi-objectives: applying initial presolve...",
    )

    # Possible intermediate patterns to be parsed
    presolve_intermediate_patterns = [
        re.compile(
            r"Presolved: (?P<PresolvedNumConstrs>\d+) (R|r)ows, (?P<PresolvedNumVars>\d+) (C|c)olumns, (?P<PresolvedNumNZs>\d+) (N|n)on(Z|z)ero(e?)s",
        ),
        re.compile(r"Presolve time: (?P<PresolveTime>[\d\.]+)s"),
    ]

    # Special case: model solved by presolve
    presolve_all_removed = re.compile(r"Presolve: All rows and columns removed")


class MultiObjParser(Parser):
    _InitialPresolveParser = InitialPresolveParser
    _ObjNLogParser = ObjNLogParser

    start_pattern = re.compile(
        r"Multi-objectives: starting optimization with (?P<NumObjPasses>\d+) objective.*$",
    )

    termination_pattern = re.compile(
        rf"Multi-objectives: (solved|stopped) in (?P<Runtime>{float_pattern}) seconds \((?P<Work>{float_pattern}) work units\), solution count (?P<SolCount>\d+)",
    )

    def __init__(self):
        # Parsers in sequence
        self.initial_presolve_parser = self._InitialPresolveParser()

        # State
        self._started = False
        self._terminated = False
        self._summary = {}
        self.parser: Parser = self.initial_presolve_parser
        self.subsequent: ObjNLogParser = self._ObjNLogParser()
        self.objn_parsers = []

    def parse(self, line: str) -> ParseResult:
        if self._terminated:
            return ParseResult(matched=False)

        if not self._started:
            match = self.start_pattern.match(line)
            if match:
                # The start line encodes information that should be stored
                self._started = True
                parse_result = typeconvert_groupdict(match)
                self._summary.update(parse_result)
                return ParseResult(parse_result)
            return ParseResult(matched=False)

        match = self.termination_pattern.match(line)
        if match:
            parse_result = typeconvert_groupdict(match)
            self._summary.update(parse_result)
            self._terminated = True
            return ParseResult(parse_result)

        if not (parse_result := self.parser.parse(line)):
            assert not self.subsequent.started
            if parse_result := self.subsequent.parse(line):
                # The current parser did not match but an empty parser
                # matched a header line.
                self.objn_parsers.append(self.subsequent)
                self.parser = self.subsequent
                self.subsequent = self._ObjNLogParser()

        return parse_result

    def get_summary(self) -> Dict:
        if not self._started:
            return {}
        return {
            **self._summary,
            **self.initial_presolve_parser.get_summary(add_model_type=False),
        }

    def get_objn_summaries(self):
        return [parser.get_summary() for parser in self.objn_parsers]

    def get_objn_progress(self, section):
        progress = []
        for parser in self.objn_parsers:
            objn_progress = parser.get_progress(section)
            progress.extend(objn_progress)
        return progress
