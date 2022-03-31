import re

from grblogtools.parsers.util import typeconvert_groupdict


class PresolveParser:
    # The pattern indicating the initialization of the parser
    presolve_start_pattern = re.compile(
        r"Optimize a model with (?P<NumConstrs>\d+) (R|r)ows, (?P<NumVars>\d+) (C|c)olumns and (?P<NumNZs>\d+) (N|n)on(Z|z)ero(e?)s"
    )

    # Possible intermediate patterns to be parsed
    presolve_intermediate_patterns = [
        re.compile(r"Model fingerprint: (?P<Fingerprint>.*)$"),
        re.compile(
            r"Variable types: (?P<PresolvedNumConVars>\d+) continuous, (?P<PresolvedNumIntVars>\d+) integer \((?P<PresolvedNumBinVars>\d+) binary\)$"
        ),
        re.compile(
            r"Variable types: (?P<PresolvedNumBinVars>\d+) bin/(?P<PresolvedNumIntVars>\d+) gen[^/]*/(?P<PresolvedNumConVars>\d+) continuous"
        ),
        re.compile(
            r"Semi-Variable types: (?P<PresolvedNumSemiContVars>\d+) continuous, (?P<PresolvedNumSemiIntVars>\d+) integer$"
        ),
        re.compile(
            r"\s*QMatrix range\s*\[(?P<MinQCCoeff>[^,]+),\s*(?P<MaxQCCoeff>[^\]]+)\]"
        ),
        re.compile(
            r"\s*QLMatrix range\s*\[(?P<MinQCLCoeff>[^,]+),\s*(?P<MaxQCLCoeff>[^\]]+)\]"
        ),
        re.compile(
            r"\s*Matrix range\s*\[(?P<MinCoeff>[^,]+),\s*(?P<MaxCoeff>[^\]]+)\]"
        ),
        re.compile(
            r"\s*QObjective range\s*\[(?P<MinQObjCoeff>[^,]+),\s*(?P<MaxQObjCoeff>[^\]]+)\]"
        ),
        re.compile(
            r"\s*Objective range\s*\[(?P<MinObjCoeff>[^,]+),\s*(?P<MaxObjCoeff>[^\]]+)\]"
        ),
        re.compile(
            r"\s*Bounds range\s*\[(?P<MinBound>[^,]+),\s*(?P<MaxBound>[^\]]+)\]"
        ),
        re.compile(r"\s*RHS range\s*\[(?P<MinRHS>[^,]+),\s*(?P<MaxRHS>[^\]]+)\]"),
        re.compile(r"\s*QRHS range\s*\[(?P<MinQCRHS>[^,]+),\s*(?P<MaxQCRHS>[^\]]+)\]"),
        re.compile(r"Model has (?P<NumQNZs>\d+) quadratic objective terms?"),
        re.compile(r"Model has (?P<NumQConstrs>\d+) quadratic constraints?"),
        re.compile(r"Model has (?P<NumSOS>\d+) SOS constraints?"),
        re.compile(
            r"Model has (?P<NumPWLObjVars>\d+) piecewise-linear objective terms?"
        ),
        re.compile(r"Model has (?P<NumGenConstrs>\d+) general constraints?"),
        re.compile(r"Distributed MIP job count: (?P<DistributedMIPJobs>\d+)"),
        re.compile(r"Concurrent MIP job count: (?P<ConcurrentJobs>\d+)"),
        re.compile(
            r"Concurrent MIP optimizer: (?P<ConcurrentJobs>\d+) concurrent instances \(\d+ threads per instance\)"
        ),
        re.compile(
            r"Presolved: (?P<PresolvedNumConstrs>\d+) (R|r)ows, (?P<PresolvedNumVars>\d+) (C|c)olumns, (?P<PresolvedNumNZs>\d+) (N|n)on(Z|z)ero(e?)s"
        ),
        re.compile(r"Presolved model has (?P<PresolvedNumSOS>\d+) SOS constraint(s)\n"),
        re.compile(
            r"Presolved model has (?P<PresolvedNumQNZs>\d+) quadratic objective terms"
        ),
        re.compile(r"Presolve time: (?P<PresolveTime>[\d\.]+)s"),
    ]

    # Special case: model solved by presolve
    presolve_all_removed = re.compile(r"Presolve: All rows and columns removed")

    def __init__(self):
        """Initialize the Presolve parser.

        The PresolveParser extends beyond the lines associated with the presolved
        model. Specifically, it includes information for all lines appearing between
        the HeaderParser and the NoRelParser or the RelaxationParser.
        """
        self._summary = {}
        self._started = False

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        if not self._started:
            match = PresolveParser.presolve_start_pattern.match(line)
            if match:
                # The start line encodes information that should be stored
                self._started = True
                self._summary.update(typeconvert_groupdict(match))
                return True
            return False

        for pattern in PresolveParser.presolve_intermediate_patterns:
            match = pattern.match(line)
            if match:
                self._summary.update(typeconvert_groupdict(match))
                return True

        match = PresolveParser.presolve_all_removed.match(line)
        if match:
            self._summary.update(
                {
                    "PresolvedNumConstrs": 0,
                    "PresolvedNumVars": 0,
                    "PresolvedNumNZs": 0,
                }
            )
            return True

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return self._summary
