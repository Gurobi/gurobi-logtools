import re

from grblogtools.helpers import convert_data_types


class PresolveParser:
    # Possible patterns indicating the initialization of the parser.
    presolve_start_patterns = [
        re.compile("Set parameter (?P<ParamName>[^\s]+) to value (?P<ParamValue>.*)$"),
        re.compile("Read (MPS|LP) format model from file (?P<ModelFilePath>.*)$"),
        re.compile(
            "Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)"
        ),
    ]
    # Possible intermediate patterns to be parsed
    presolve_intermediate_patterns = [
        re.compile("Set parameter (?P<ParamName>[^\s]+) to value (?P<ParamValue>.*)$"),
        re.compile("Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
        re.compile("Read (MPS|LP) format model from file (?P<ModelFilePath>.*)$"),
        re.compile("Reading time = (?P<ReadingTime>[\d\.]+) seconds"),
        re.compile(
            "Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)"
        ),
        re.compile(
            "Optimize a model with (?P<NumConstrs>\d+) (R|r)ows, (?P<NumVars>\d+) (C|c)olumns and (?P<NumNZs>\d+) (N|n)on(Z|z)ero(e?)s"
        ),
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
        self._log = {}

    def _update_log(self, match):
        # This can happend if all the rows and columns are removed by presolve
        dict_ = match.groupdict()
        if not dict_:
            self._log.update(
                {
                    "PresolvedNumConstrs": 0,
                    "PresolvedNumVars": 0,
                    "PresolvedNumNZs": 0,
                }
            )
        elif "ParamName" in dict_:
            # Add the keyword "Param" at the end of the ParamName to make
            # it clear it is a parameter
            self._log.update(
                {dict_["ParamName"] + "_Param": convert_data_types(dict_["ParamValue"])}
            )
        else:
            self._log.update(
                {
                    sub_match: convert_data_types(value)
                    for sub_match, value in dict_.items()
                }
            )

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line matches one of the parser's start
                patterns.
        """
        for possible_start in PresolveParser.presolve_start_patterns:
            match = possible_start.match(line)
            if match:
                # The start line encodes information that should to be stored
                self._update_log(match)
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
                self._update_log(match)
                break
        return True

    def get_log(self) -> dict:
        """Return the current parsed log.

        It returns an empty dictionary if the parser is not initialized yet.
        """
        return self._log
