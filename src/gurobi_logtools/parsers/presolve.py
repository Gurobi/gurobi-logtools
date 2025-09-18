import re
from typing import Any, Dict

from gurobi_logtools.parsers.pretree_solutions import PreTreeSolutionParser
from gurobi_logtools.parsers.util import (
    Parser,
    model_type,
    typeconvert_groupdict,
    DummyParser,
    ParseResult,
)


class PresolveParser(Parser):
    # The pattern indicating the initialization of the parser
    presolve_start_pattern = re.compile(
        r"Optimize a model with (?P<NumConstrs>\d+) (R|r)ows, (?P<NumVars>\d+) (C|c)olumns and (?P<NumNZs>\d+) (N|n)on(Z|z)ero(e?)s",
    )

    # Possible intermediate patterns to be parsed
    model_stat_patterns = [
        re.compile(r"Model fingerprint: (?P<Fingerprint>.*)$"),
        re.compile(  # dev log
            r"Variable types: (?P<PresolvedNumBinVars>\d+) bin/(?P<PresolvedNumIntVars>\d+) gen[^/]*/(?P<PresolvedNumConVars>\d+) continuous",
        ),
        re.compile(
            r"Semi-Variable types: (?P<NumSemiContVars>\d+) continuous, (?P<NumSemiIntVars>\d+) integer$",
        ),
        re.compile(
            r"\s*QMatrix range\s*\[(?P<MinQCCoeff>[^,]+),\s*(?P<MaxQCCoeff>[^\]]+)\]",
        ),
        re.compile(
            r"\s*QLMatrix range\s*\[(?P<MinQCLCoeff>[^,]+),\s*(?P<MaxQCLCoeff>[^\]]+)\]",
        ),
        re.compile(
            r"\s*Matrix range\s*\[(?P<MinCoeff>[^,]+),\s*(?P<MaxCoeff>[^\]]+)\]",
        ),
        re.compile(
            r"\s*QObjective range\s*\[(?P<MinQObjCoeff>[^,]+),\s*(?P<MaxQObjCoeff>[^\]]+)\]",
        ),
        re.compile(
            r"\s*Objective range\s*\[(?P<MinObjCoeff>[^,]+),\s*(?P<MaxObjCoeff>[^\]]+)\]",
        ),
        re.compile(
            r"\s*Bounds range\s*\[(?P<MinBound>[^,]+),\s*(?P<MaxBound>[^\]]+)\]",
        ),
        re.compile(r"\s*RHS range\s*\[(?P<MinRHS>[^,]+),\s*(?P<MaxRHS>[^\]]+)\]"),
        re.compile(r"\s*QRHS range\s*\[(?P<MinQCRHS>[^,]+),\s*(?P<MaxQCRHS>[^\]]+)\]"),
        re.compile(r"Model has (?P<NumQNZs>\d+) quadratic objective terms?"),
        re.compile(r"Model has (?P<NumQConstrs>\d+) quadratic constraints?"),
        re.compile(r"Model has (?P<NumSOS>\d+) SOS constraints?"),
        re.compile(
            r"Model has (?P<NumPWLObjVars>\d+) piecewise-linear objective terms?",
        ),
        re.compile(r"Model has (?P<NumGenConstrs>\d+) general constraints?"),
        re.compile(r"Distributed MIP job count: (?P<DistributedMIPJobs>\d+)"),
        re.compile(r"Concurrent MIP job count: (?P<ConcurrentJobs>\d+)"),
        re.compile(
            r"Concurrent MIP optimizer: (?P<ConcurrentJobs>\d+) concurrent instances \(\d+ threads per instance\)",
        ),
    ]

    presolve_intermediate_patterns = [
        re.compile(
            r"Presolved: (?P<PresolvedNumConstrs>\d+) (R|r)ows, (?P<PresolvedNumVars>\d+) (C|c)olumns, (?P<PresolvedNumNZs>\d+) (N|n)on(Z|z)ero(e?)s",
        ),
        re.compile(r"Presolved model has (?P<PresolvedNumSOS>\d+) SOS constraint(s)\n"),
        re.compile(
            r"Presolved model has (?P<PresolvedNumQNZs>\d+) quadratic objective terms",
        ),
        re.compile(r"Presolve time: (?P<PresolveTime>[\d\.]+)s"),
    ]

    # Special case
    variable_types = re.compile(
        r"Variable types: (?P<NumConVars>\d+) continuous, (?P<NumIntVars>\d+) integer \((?P<NumBinVars>\d+) binary\)$",
    )

    # Special case: model solved by presolve
    presolve_all_removed = re.compile(r"Presolve: All rows and columns removed")

    def __init__(
        self,
        pretree_solution_parser: PreTreeSolutionParser | DummyParser = DummyParser(),
    ):
        """Initialize the Presolve parser.

        The PresolveParser extends beyond the lines associated with the presolved
        model. Specifically, it includes information for all lines appearing between
        the HeaderParser and the NoRelParser or the RelaxationParser.
        """
        self._summary: Dict[str, Any] = {}
        self._started = False
        self._post_presolve = False
        self._pretree_solution_parser: PreTreeSolutionParser | DummyParser = (
            pretree_solution_parser
        )

    def parse(self, line: str) -> ParseResult:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
           Dict[str, Any]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.

        """

        if parse_result := self._pretree_solution_parser.parse(line):
            return parse_result

        for pattern in [
            self.presolve_start_pattern,
            *PresolveParser.model_stat_patterns,
        ]:
            match = pattern.match(line)
            if match:
                parse_result_dict = typeconvert_groupdict(match)
                self._summary.update(parse_result_dict)
                return ParseResult(parse_result_dict)

        for pattern in PresolveParser.presolve_intermediate_patterns:
            match = pattern.match(line)
            if match:
                self._post_presolve = True
                parse_result_dict = typeconvert_groupdict(match)
                self._summary.update(parse_result_dict)
                return ParseResult(parse_result_dict)

        if match := self.variable_types.match(line):
            parse_result_dict = typeconvert_groupdict(match)
            if self._post_presolve:
                parse_result_dict = {
                    "PresolvedNumConVars": parse_result_dict["NumConVars"],
                    "PresolvedNumIntVars": parse_result_dict["NumIntVars"],
                    "PresolvedNumBinVars": parse_result_dict["NumBinVars"],
                }
            self._summary.update(parse_result_dict)
            return ParseResult(parse_result_dict)

        match = PresolveParser.presolve_all_removed.match(line)
        if match:
            self._summary.update(
                {
                    "PresolvedNumConstrs": 0,
                    "PresolvedNumVars": 0,
                    "PresolvedNumNZs": 0,
                },
            )
            return ParseResult(self._summary)

        return ParseResult(matched=False)

    def get_summary(self, add_model_type=True) -> Dict:
        """Return the current parsed summary."""
        summary = self._summary.copy()
        if add_model_type:
            # we don't want to add ModelType if this parsing presolve data from one
            # of the solves in a multiobjective model.  It is too complicated to get
            # it right and also not necessary since the ModelType will be recorded
            # in the "main summary".
            summary["ModelType"] = model_type(
                discrete_vars=sum(
                    summary.get(k, 0)
                    for k in (
                        "NumBinVars",
                        "NumIntVars",
                        "NumSemiContVars",
                        "NumSemiIntVars",
                    )
                ),
                quad_nonzeros=summary.get("NumQNZs", 0),
                quad_constrs=summary.get("NumQConstrs", 0),
            )
        return summary
