import re

from grblogtools.helpers import typeconvert_groupdict


class PresolveParser:
    # The pattern indicating the initialization of the parser
    presolve_start_pattern = re.compile(
        "Optimize a model with (?P<NumConstrs>\d+) (R|r)ows, (?P<NumVars>\d+) (C|c)olumns and (?P<NumNZs>\d+) (N|n)on(Z|z)ero(e?)s"
    )

    # Possible intermediate patterns to be parsed
    presolve_intermediate_patterns = [
        re.compile("Model fingerprint: (?P<Fingerprint>.*)$"),
        re.compile(
            "Variable types: (?P<PresolvedNumConVars>\d+) continuous, (?P<PresolvedNumIntVars>\d+) integer \((?P<PresolvedNumBinVars>\d+) binary\)$"
        ),
        re.compile(
            "Variable types: (?P<PresolvedNumBinVars>\d+) bin/(?P<PresolvedNumIntVars>\d+) gen[^/]*/(?P<PresolvedNumConVars>\d+) continuous"
        ),
        re.compile(
            "Semi-Variable types: (?P<PresolvedNumSemiContVars>\d+) continuous, (?P<PresolvedNumSemiIntVars>\d+) integer$"
        ),
        re.compile(
            "\s*QMatrix range\s*\[(?P<MinQCCoeff>[^,]+),\s*(?P<MaxQCCoeff>[^\]]+)\]"
        ),
        re.compile(
            "\s*QLMatrix range\s*\[(?P<MinQCLCoeff>[^,]+),\s*(?P<MaxQCLCoeff>[^\]]+)\]"
        ),
        re.compile("\s*Matrix range\s*\[(?P<MinCoeff>[^,]+),\s*(?P<MaxCoeff>[^\]]+)\]"),
        re.compile(
            "\s*QObjective range\s*\[(?P<MinQObjCoeff>[^,]+),\s*(?P<MaxQObjCoeff>[^\]]+)\]"
        ),
        re.compile(
            "\s*Objective range\s*\[(?P<MinObjCoeff>[^,]+),\s*(?P<MaxObjCoeff>[^\]]+)\]"
        ),
        re.compile("\s*Bounds range\s*\[(?P<MinBound>[^,]+),\s*(?P<MaxBound>[^\]]+)\]"),
        re.compile("\s*RHS range\s*\[(?P<MinRHS>[^,]+),\s*(?P<MaxRHS>[^\]]+)\]"),
        re.compile("\s*QRHS range\s*\[(?P<MinQCRHS>[^,]+),\s*(?P<MaxQCRHS>[^\]]+)\]"),
        re.compile("Model has (?P<NumQNZs>\d+) quadratic objective terms?"),
        re.compile("Model has (?P<NumQConstrs>\d+) quadratic constraints?"),
        re.compile("Model has (?P<NumSOS>\d+) SOS constraints?"),
        re.compile(
            "Model has (?P<NumPWLObjVars>\d+) piecewise-linear objective terms?"
        ),
        re.compile("Model has (?P<NumGenConstrs>\d+) general constraints?"),
        re.compile("Distributed MIP job count: (?P<DistributedMIPJobs>\d+)"),
        re.compile("Concurrent MIP job count: (?P<ConcurrentJobs>\d+)"),
        re.compile(
            "Concurrent MIP optimizer: (?P<ConcurrentJobs>\d+) concurrent instances \(\d+ threads per instance\)"
        ),
        re.compile(
            "Presolved: (?P<PresolvedNumConstrs>\d+) (R|r)ows, (?P<PresolvedNumVars>\d+) (C|c)olumns, (?P<PresolvedNumNZs>\d+) (N|n)on(Z|z)ero(e?)s"
        ),
        re.compile("Presolve: All rows and columns removed"),
        re.compile("Presolved model has (?P<PresolvedNumSOS>\d+) SOS constraint(s)\n"),
        re.compile(
            "Presolved model has (?P<PresolvedNumQNZs>\d+) quadratic objective terms"
        ),
        re.compile("Presolve time: (?P<PresolveTime>[\d\.]+)s"),
    ]

    def __init__(self):
        """Initialize the Presolve parser.

        The PresolveParser extends beyond the lines associated with the presolved model.
        Specifically, it includes information for all lines appearing between the
        HeaderParser and the NoRelParser or the RelaxationParser.
        """
        self._summary = {}

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line matches the parser start pattern.
        """
        match = PresolveParser.presolve_start_pattern.match(line)
        if match:
            # The start line encodes information that should be stored
            self._summary.update(typeconvert_groupdict(match))
            return True
        return False

    def continue_parsing(self, line: str) -> bool:
        """Parse the given line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True.
        """
        # If an empty line, return True
        if not line.strip():
            return True

        for pattern in PresolveParser.presolve_intermediate_patterns:
            match = pattern.match(line)
            if match:
                if match.string == "Presolve: All rows and columns removed":
                    self._summary.update(
                        {
                            "PresolvedNumConstrs": 0,
                            "PresolvedNumVars": 0,
                            "PresolvedNumNZs": 0,
                        }
                    )
                else:
                    self._summary.update(typeconvert_groupdict(match))
                break
        return True

    def get_summary(self) -> dict:
        """Return the current parsed summary.

        It returns an empty dictionary if the parser is not initialized yet.
        """
        return self._summary
