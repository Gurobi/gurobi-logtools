import glob
import os
import re
import ipywidgets as widgets
from ipywidgets import interact
import plotly.express as px
import pandas as pd
from numpy import nan

from grblogtools.helpers import fill_default_parameters
from grblogtools.helpers import add_categorical_descriptions

# Log Status Codes
class logstatus:
    FINISHED, INCOMPLETE, FAILED = range(3)

    def str(value):
        if value == logstatus.FINISHED:
            return "FINISHED"
        elif value == logstatus.INCOMPLETE:
            return "INCOMPLETE"
        elif value == logstatus.FAILED:
            return "FAILED"
        else:
            return "UNKNOWN"


class logpattern:

    # Log start indicator (all lines before last occcurence are discarded)
    headers = [
        re.compile(
            "Gurobi (?P<Version>\d{1,2}\.[^\s]+) \((?P<Platform>[^\)]+)\) logging started (?P<Time>.*)$"
        ),
        re.compile("Logging started (?P<Time>.*)$"),
        re.compile(
            "Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$"
        ),
        re.compile("Compute Server job ID: (?P<JobID>.*)$")
    ]

    # Parameter settings
    parameters = re.compile("Set parameter (?P<Name>[^\s]+) to value (?P<Value>.*)$")

    # Termination messsages
    termination_message = [
        re.compile(
            "(Solved|Stopped) in (?P<IterCount>[^\s]+) iterations and (?P<Runtime>[^\s]+) seconds"
        ),
        re.compile(
            "Best objective (?P<ObjVal>[^,]+), best bound (?P<ObjBound>[^,]+), gap (?P<MIPGap>.*)$"
        ),
        re.compile(
            "Barrier solved model in (?P<BarIterCount>[^\s]+) iterations and (?P<Runtime>[^\s]+) seconds"
        ),
        re.compile("ERROR (?P<ErrorCode>[^:]+): (?P<ErrorMessage>.*)$"),
        re.compile("\[(?P<ErrorMessage>process terminated with exit code [^\\]]+)\]$"),
    ]

    # Termination status
    termination_status = [
        re.compile("(?P<TIME_LIMIT>Time limit reached)"),
        re.compile("(?P<OPTIMAL>Optimal solution found)(?: \(tolerance .*\))"),
        re.compile("(?P<OPTIMAL>Optimal objective\s+(?P<ObjVal>.*))$"),
        re.compile("(?P<ITERATION_LIMIT>Iteration limit reached)"),
        re.compile("(?P<INF_OR_UNBD>Infeasible or unbounded model)"),
        re.compile("(?P<INF_OR_UNBD>Model is infeasible or unbounded)"),
        re.compile("(?P<UNBOUNDED>Unbounded model)"),
        re.compile("(?P<UNBOUNDED>Model is unbounded)"),
        re.compile("(?P<INFEASIBLE>Infeasible model)"),
        re.compile("(?P<INFEASIBLE>Model is infeasible)"),
        re.compile("(?P<SOLUTION_LIMIT>Solution limit reached)"),
        re.compile("(?P<NODE_LIMIT>Node limit reached)"),
        re.compile("(?P<NUMERIC>Numeric error)"),
        re.compile("(?P<NUMERIC>Numerical trouble encountered)"),
        re.compile(
            "(?P<SUBOPTIMAL>Sub-optimal termination)(?: - objective (P<ObjVal>.*))$"
        ),
        re.compile("(?P<CUTOFF>Model objective exceeds cutoff)"),
        re.compile("(?P<CUTOFF>Objective cutoff exceeded)"),
        re.compile("(?P<USER_OBJ_LIMIT>Optimization achieved user objective limit)"),
        re.compile(
            "(?P<INTERRUPTED>(Interrupt request received|Solve interrupted))(?: \\(error code (?P<ErrorCode>[^\\)]+)\\))?"
        ),
    ]

    # Coefficient statistics
    coefficients = [
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
    ]

    # Various pattern (last occurence is always taken)
    various = [
        re.compile(
            "Variable types: (?P<PresolvedNumConVars>\d+) continuous, (?P<PresolvedNumIntVars>\d+) integer \((?P<PresolvedNumBinVars>\d+) binary\)$"
        ),
        re.compile(
            "Variable types: (?P<PresolvedNumBinVars>\d+) bin/(?P<PresolvedNumIntVars>\d+) gen[^/]*/(?P<PresolvedNumConVars>\d+) continuous"
        ),
        re.compile(
            "Semi-Variable types: (?P<PresolvedNumSemiContVars>\d+) continuous, (?P<PresolvedNumSemiIntVars>\d+) integer$"
        ),
        re.compile("Optimal objective\s+(?P<ObjVal>.*)$"),
        re.compile(
            "Optimize a model with (?P<NumConstrs>\d+) (R|r)ows, (?P<NumVars>\d+) (C|c)olumns and (?P<NumNZs>\d+) (N|n)on(Z|z)ero(e?)s"
        ),
        re.compile("Presolve time: (?P<PresolveTime>[\d\.]+)s"),
        re.compile("Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)"),
        re.compile("Distributed MIP job count: (?P<DistributedMIPJobs>\d+)"),
        re.compile("Concurrent MIP job count: (?P<ConcurrentJobs>\d+)"),
        re.compile("Reading time = (?P<ReadTime>[\d\.]+) seconds"),
        re.compile("Ordering time: (?P<OrderingTime>[\d\.]+)s"),
        re.compile("Model has (?P<NumQNZs>\d+) quadratic objective terms?"),
        re.compile("Model has (?P<NumQConstrs>\d+) quadratic constraints?"),
        re.compile("Model has (?P<NumSOS>\d+) SOS constraints?"),
        re.compile(
            "Model has (?P<NumPWLObjVars>\d+) piecewise-linear objective terms?"
        ),
        re.compile("Model has (?P<NumGenConstrs>\d+) general constraints?"),
        re.compile("Loaded user MIP start with objective (?P<MIPStart>.*)$"),
        re.compile("Pool objective bound (?P<PoolObjBound>.*)$"),
        re.compile("Solution count (?P<SolCount>\d+)"),
        re.compile(
            "Root relaxation: objective (?P<RelaxObj>[^,]+), (?P<RelaxIterCount>\d+) iterations, (?P<RelaxTime>[^\s]+) seconds"
        ),
        re.compile(
            "Explored (?P<NodeCount>\d+) nodes \((?P<IterCount>\d+) simplex iterations\) in (?P<Runtime>[^\s]+) seconds"
        ),
        re.compile(
            "Barrier performed (?P<BarIterCount>\d+) iterations in [^\s]+ seconds"
        ),
        re.compile(
            "Barrier solved model in (?P<BarIterCount>\d+) iterations and [^\s]+ seconds"
        ),
        re.compile(
            "Push phase complete: Pinf (?P<PushPhasePInf>[^,]+), Dinf (?P<PushPhaseDInf>[^,]+)\s+(?P<PushPhaseEndTime>\d+)s"
        ),
        re.compile("Read (MPS|LP) format model from file (?P<ModelFilePath>.*)$"),
        re.compile(
            "(?!Presolved)(?P<Model>.*): \d+ (R|r)ows, \d+ (C|c)olumns, \d+ (N|n)on(Z|z)ero(e?)s"
        ),
        re.compile("Presolved model has (?P<PresolvedNumSOS>\d+) SOS constraint(s)\n"),
        re.compile(
            "Presolved model has (?P<PresolvedNumQNZs>\d+) quadratic objective terms"
        ),
        re.compile("Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
    ]

    # Patterns that come BEFORE any final termination message if found
    # This list is used to discard earlier termination messages (e.g. from MIP root node)
    pre_termination = [
        re.compile(re.escape(" Expl Unexpl |  Obj  Depth IntInf |")),
        re.compile("Root barrier log"),
        re.compile("Root simplex log"),
        re.compile("Root relaxation:"),
        re.compile("Crossover log"),
        re.compile("Total elapsed time = "),
    ]

    # Presolve information (only last occurence is taken)
    presolve = re.compile(
        "Presolved: (?P<PresolvedNumConstrs>\d+) (R|r)ows, (?P<PresolvedNumVars>\d+) (C|c)olumns, (?P<PresolvedNumNZs>\d+) (N|n)on(Z|z)ero(e?)s"
    )
    presolve_complete = re.compile("Presolve: All rows and columns removed")


def _regex_group_to_field_name(groupname):
    if groupname.startswith("_"):
        return groupname[1:] + " (Parameter)"
    else:
        return groupname


def _regex_matches(lines, regex_list, reverse=True, matchLimit=float("inf")):
    """(Reverse) iterate over a list of log lines, call match() for a list of regex and return first successful match as (lineNumber, groupDict) up to matchLimit lines."""

    # Check parameters
    if not isinstance(lines, list):
        raise TypeError()
    if isinstance(regex_list, type(re.compile("test"))):
        regex_list = [regex_list]
    if not isinstance(regex_list, list):
        raise TypeError()
    if any(not isinstance(regex, type(re.compile("test"))) for regex in regex_list):
        raise TypeError()
    if matchLimit < 1:
        raise ValueError()

    line_order = range(len(lines) - 1, -1, -1) if reverse else range(0, len(lines))

    matches = []
    for line in line_order:
        for regex in regex_list:
            result = regex.match(lines[line])
            if result:
                groupdict = {
                    _regex_group_to_field_name(key): value
                    for key, value in result.groupdict().items()
                }
                matches.append((line, groupdict))
                if len(matches) >= matchLimit:
                    return matches
                continue

    return matches


def _regex_first_match(lines, regex_list, reverse=True):
    """(Reverse) iterate over a list of log lines, call match() for a list of regex and return first successful match as (lineNumber, groupDict)."""

    # Check parameters
    if not isinstance(lines, list):
        raise TypeError()
    if isinstance(regex_list, type(re.compile("test"))):
        regex_list = [regex_list]
    if not isinstance(regex_list, list):
        raise TypeError()
    if any(not isinstance(regex, type(re.compile("test"))) for regex in regex_list):
        raise TypeError()

    line_order = range(len(lines) - 1, -1, -1) if reverse else range(0, len(lines))

    for line in line_order:
        for regex in regex_list:
            result = regex.match(lines[line])
            if result:
                groupdict = {
                    _regex_group_to_field_name(key): value
                    for key, value in result.groupdict().items()
                }
                return (line, groupdict)

    return (None, {})


def get_log_status(loglines):
    """Check if list of log lines contains a complete log"""

    if not isinstance(loglines, list):
        raise TypeError("Wrong log format")

    # Check first message
    first_line, result = _regex_first_match(loglines, logpattern.headers, reverse=True)
    if not result:
        return logstatus.INCOMPLETE
    loglines = loglines[first_line:]

    # Filter log lines that are not final termination lines
    loglines_before_termination = loglines
    pre_termination_line, result = _regex_first_match(
        loglines, logpattern.pre_termination, reverse=True
    )
    if result is not None:
        loglines_before_termination = loglines_before_termination[pre_termination_line:]

    _, result = _regex_first_match(
        loglines_before_termination, logpattern.termination_message, reverse=True
    )
    if not result:
        return logstatus.INCOMPLETE
    else:
        if result.get("ErrorMessage", None) is not None:
            return logstatus.FAILED

    # Check termination status
    _, result = _regex_first_match(
        loglines, logpattern.termination_status, reverse=True
    )
    if not result:
        return logstatus.INCOMPLETE

    # Simple pattern
    for regex in logpattern.various:
        _, result = _regex_first_match(loglines, regex, reverse=True)

    return logstatus.FINISHED


def _get_last_nonempty_line(loglines, start_line):
    """Check loglines starting at index start_line and return the number of the last line that is not empty"""

    last_line = len(loglines) - 1
    for i in range(start_line, len(loglines)):
        if len(loglines[i].strip()) == 0:
            last_line = i - 1
            break

    return last_line


def _get_last_tree_line(loglines, start_line):
    """Check loglines starting at index start_line and return the number of the 'Explored ... nodes' line"""

    last_line = len(loglines)
    explored = re.compile(r"Explored \d+ nodes")
    for i in range(start_line, len(loglines)):
        if explored.match(loglines[i]):
            break

    return last_line - 1


def _get_typed_values(values):

    typed_values = {}

    int_regex = re.compile("[-+]?\d+$")
    float_regex = re.compile("[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?$")
    percentage_regex = re.compile("[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?%$")

    for key, value in values.items():
        if not isinstance(value, str):
            continue
        if int_regex.match(value):
            typed_values[key] = int(value)
        elif float_regex.match(value):
            typed_values[key] = float(value)
        elif percentage_regex.match(value):
            typed_values[key] = float(value[:-1]) / 100

    return typed_values


def get_log_info(loglines, verbose=False):

    if not isinstance(loglines, list):
        raise TypeError("Wrong log format")

    # Default values
    values = {"ObjVal": "-", "ObjBound": "-", "MIPGap": "-"}

    # Used to match and parse floating point numbers of any format
    float_pattern = "[-+]?((\d*\.\d+)|(\d+\.?))([Ee][+-]?\d+)?"

    # Step 1: Find last header line
    first_line, result = _regex_first_match(loglines, logpattern.headers, reverse=True)
    if not result:
        print("Error: Could not find initial log message in logfile")
        return None
    else:
        # get all header information
        for _,result in _regex_matches(loglines[:first_line+1], logpattern.headers):
            values.update(result)

    # Discard previous lines
    loglines = loglines[first_line:]

    # Step 2: Find valid (final) termination message
    loglines_before_termination = loglines
    pre_termination_line, result = _regex_first_match(
        loglines, logpattern.pre_termination, reverse=True
    )
    if result is not None:
        loglines_before_termination = loglines_before_termination[pre_termination_line:]

    line, result = _regex_first_match(
        loglines_before_termination, logpattern.termination_message, reverse=True
    )

    if not result:
        print("Error: Could not find termination log message. Logfile incomplete?")
        return None
    else:
        values.update(result)

    # Step 3: Check status on exit
    line, result = _regex_first_match(
        loglines, logpattern.termination_status, reverse=True
    )

    if not result:
        print("Error: Could not determine termination status. Logfile incomplete?")
        return None
    else:
        # Status Status and additional information (a bit hacky: identify status by CAPITAL_AND_UNDERSCORE_ONLY group name)
        for key, value in result.items():
            if not re.match("[A-Z_]+$", key):
                values[key] = value
            else:
                values["Status"] = key

    # Presolve information (reverse order is important for lookup!)
    line, result = _regex_first_match(loglines, logpattern.presolve, reverse=True)
    if result:
        values.update(result)
    else:
        line, result = _regex_first_match(
            loglines, logpattern.presolve_complete, reverse=False
        )
        if line is not None:
            values["PresolvedNumConstrs"] = 0
            values["PresolvedNumNZs"] = 0
            values["PresolvedNumVars"] = 0

    # Coefficient statistics
    line, result = _regex_first_match(
        loglines, re.compile("Coefficient statistics:"), reverse=False
    )
    if line:

        # Check patterns on next 5 lines
        coefficient_statistic_lines = loglines[line + 1 : line + 6]
        for regex in logpattern.coefficients:
            line, result = _regex_first_match(
                coefficient_statistic_lines, re.compile(regex), reverse=False
            )
            values.update(result)

    # Simple pattern
    for regex in logpattern.various:
        line, result = _regex_first_match(loglines, regex, reverse=True)
        if result:

            # Update values, but do not overwrite existing values
            result.update(values)
            values = result

    # Result files
    result_files = []
    for line, result in _regex_matches(
        loglines, re.compile("Wrote result file '(?P<ResultFile>.*)'$"), reverse=False
    ):
        result_files.append(result["ResultFile"])

    if len(result_files) > 0:
        values["ResultFiles"] = result_files

    # Cut counts
    cut_count_first_line, result = _regex_first_match(
        loglines, re.compile("Cutting planes:"), reverse=False
    )
    if cut_count_first_line:
        cut_count_last_line = _get_last_nonempty_line(
            loglines, cut_count_first_line + 1
        )
        for line, result in _regex_matches(
            loglines[cut_count_first_line + 1 : cut_count_last_line + 1],
            re.compile("  (?P<Name>[\w ]+): (?P<Count>\d+)"),
            reverse=False,
        ):
            if result:
                values["Cuts: " + result["Name"].strip()] = int(result["Count"])

    # NoRel log
    norel_log_start = re.compile("Starting NoRel heuristic")
    norel_first_line, result = _regex_first_match(
        loglines, [norel_log_start], reverse=False
    )
    if norel_first_line and norel_first_line < len(loglines) - 1:
        norel_last_line = _get_last_nonempty_line(loglines, norel_first_line + 1)
        norel_primal_regex = re.compile(
            "Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)"
        )
        norel_elapsed_time = re.compile(
            "Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s"
        )
        norel_elapsed_bound = re.compile(
            "Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s\s\(best\sbound\s(?P<BestBd>[^\s]+)\)"
        )
        norel_log = []
        norel_incumbent = {}
        for norel_log_line in loglines[
            norel_first_line + 1 : norel_last_line + 1
        ]:
            # NoRel shows the solutions and timings/bounds on different lines, so
            # when we see a timing line, we store the most recent incumbent there,
            # instead of recording the primal when the log line is found.
            result = norel_primal_regex.match(norel_log_line)
            if result:
                norel_incumbent = result.groupdict()
            result = norel_elapsed_bound.match(norel_log_line) or norel_elapsed_time.match(norel_log_line)
            if result:
                tmp = result.groupdict()
                tmp.update(norel_incumbent)
                norel_log.append(tmp)
        if len(norel_log) > 0:
            values["NoRelLog"] = norel_log

    # Simplex Log (can be regular LP, root node or crossover)
    simplex_log_start = re.compile(
        "Iteration(\s+)Objective(\s+)Primal Inf.(\s+)Dual Inf.(\s+)Time"
    )
    simplex_first_line, result = _regex_first_match(
        loglines, [simplex_log_start], reverse=False
    )
    if simplex_first_line and simplex_first_line < len(loglines) - 1:

        # Slice out simplex log lines
        simplex_last_line = _get_last_nonempty_line(loglines, simplex_first_line + 1)
        simplex_log_line_regex = re.compile(
            "\s*(?P<Iteration>\d+)\s+(?P<Objective>[^\s]+)\s+(?P<PInf>[^\s]+)\s+(?P<DInf>[^\s]+)\s+(?P<Time>\d+)s"
        )
        simplex_log = []
        for simplex_log_line in loglines[
            simplex_first_line + 1 : simplex_last_line + 1
        ]:
            result = simplex_log_line_regex.match(simplex_log_line)
            if result:
                simplex_log.append(result.groupdict())

        if len(simplex_log) > 0:
            values["SimplexLog"] = simplex_log

    # Barrier log (without barrier statistics)
    barrier_log_start = re.compile(
        "Iter(\s+)Primal(\s+)Dual(\s+)Primal(\s+)Dual(\s+)Compl(\s+)Time"
    )
    barrier_first_line, result = _regex_first_match(
        loglines, [barrier_log_start], reverse=False
    )
    if barrier_first_line and barrier_first_line < len(loglines) - 1:

        # Slice out barrier log lines
        barrier_last_line = _get_last_nonempty_line(loglines, barrier_first_line + 1)
        barrier_log_line_regex = re.compile(
            "\s*(?P<Iteration>\d+)(?P<Indicator>\s|\*)\s+(?P<PObj>[^\s]+)\s+(?P<DObj>[^\s]+)\s+(?P<PRes>[^\s]+)\s+(?P<DRes>[^\s]+)\s+(?P<Compl>[^\s]+)\s+(?P<Time>\d+)s"
        )
        barrier_log = []
        for barrier_log_line in loglines[
            barrier_first_line + 1 : barrier_last_line + 1
        ]:
            result = barrier_log_line_regex.match(barrier_log_line)
            if result:
                barrier_log.append(result.groupdict())

        if len(barrier_log) > 0:
            values["BarrierLog"] = barrier_log

    # Tree Search Log
    tree_search_log_start = re.compile(r" Expl Unexpl(.*)It/Node Time$")

    # Regular expressions for different log line types
    tree_search_full_log_line_regex = re.compile(
        r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Obj>{0})\s+(?P<Depth>\d+)\s+(?P<IntInf>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}%))\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
            float_pattern
        )
    )
    tree_search_nodepruned_line_regex = re.compile(
        r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Obj>(cutoff|infeasible|postponed))\s+(?P<Depth>\d+)\s+(?P<Incumbent>(-|{0}))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}%))\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
            float_pattern
        )
    )
    tree_search_new_solution_heuristic_log_line_regex = re.compile(
        r"(?P<NewSolution>H)\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>{0}%)\s+(?P<ItPerNode>(-|{0}))\s+(?P<Time>\d+)s".format(
            float_pattern
        )
    )
    tree_search_new_solution_branching_log_line_regex = re.compile(
        r"(?P<NewSolution>\*)\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Depth>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>{0}%)\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
            float_pattern
        )
    )
    tree_search_status_line_regex = re.compile(
        r"\s\s*(?P<CurrentNode>\d+)\s+(?P<RemainingNodes>\d+)\s+(?P<Obj>-)\s+(?P<Depth>\d+)\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+(?P<Gap>(-|{0}%))\s+(?P<ItPerNode>({0}|-))\s+(?P<Time>\d+)s".format(
            float_pattern
        )
    )

    tree_search_log = []
    ignored_lines = 0

    tree_search_first_line, result = _regex_first_match(
        loglines, [tree_search_log_start], reverse=False
    )
    if tree_search_first_line and tree_search_first_line < len(loglines) - 2:

        # Slice out tree search log lines
        tree_search_last_line = _get_last_tree_line(
            loglines, tree_search_first_line + 2
        )
        lastheur = None

        for tree_search_log_line in loglines[
            tree_search_first_line + 2 : tree_search_last_line + 1
        ]:

            result = tree_search_full_log_line_regex.match(
                tree_search_log_line.rstrip()
            )

            line, result = _regex_first_match(
                [tree_search_log_line.rstrip()],
                [
                    tree_search_full_log_line_regex,
                    tree_search_nodepruned_line_regex,
                    tree_search_status_line_regex,
                    tree_search_new_solution_branching_log_line_regex,
                    tree_search_new_solution_heuristic_log_line_regex,
                ],
            )

            if line is not None:
                result.update(_get_typed_values(result))
                if lastheur and result.get("NewSolution") == "H":
                    result["NewSolution"] = lastheur
                tree_search_log.append(result)
            else:
                ignored_lines += 1

    if len(tree_search_log) > 0:
        values["TreeSearchLog"] = tree_search_log
        if ignored_lines > 0 and verbose:
            print("Info: Ignored", ignored_lines, "tree search lines")

    # Warnings
    # e.g.
    # Warning: Model contains large matrix coefficient range
    # Warning: switch to quad precision
    # Warning: 1 variables dropped from basis
    # Warning: unscaled primal violation = 1 and residual = 2.38419e-07
    # Warning: unscaled dual violation = 0.000662516 and residual = 0.000662516
    # Warning: max bound violation (1.5772e-06) exceeds tolerance
    # Warning: max constraint violation (2.4714e-03) exceeds tolerance

    all_warnings = [line.strip() for line in loglines if line.startswith("Warning:")]
    if len(all_warnings) > 0:
        values["Warnings"] = all_warnings
        values["NumWarnings"] = len(all_warnings)

    # Parameters
    parameters = {}
    for line, result in _regex_matches(loglines, logpattern.parameters, reverse=True):

        # Chronological order, will override previous values
        parameters[result["Name"]] = result["Value"]

    # Add parameters but add suffix if a value is already present
    for key, value in parameters.items():
        values["%s (Parameter)" % key] = value

    # typed values (int, double) if possible
    values.update(_get_typed_values(values))

    # Derive model type
    model_type = ""

    # Int/Bin variables?
    mip_var_types = (
        values.get("PresolvedNumBinVars", 0)
        + values.get("PresolvedNumIntVars", 0)
        + values.get("PresolvedNumSemiIntVars", 0)
        + values.get("PresolvedNumSemiContVars", 0)
    )

    if mip_var_types > 0 or "RelaxIterCount" in values or "NodeCount" in values:
        model_type += "MI"

    # Something quadratic?
    if values.get("NumQNZs", 0) > 0 or values.get("NumQConstrs", 0) > 0:
        model_type += "Q"

    # Quadratic constraints?
    if values.get("NumQConstrs", 0) > 0:
        model_type += "C"

    if model_type == "":
        model_type = "LP"
    else:
        model_type += "P"

    values["ModelType"] = model_type

    return values


def _strip_modelname(logname, modelname):
    """small helper function to strip the model name from the log name"""
    logname = os.path.basename(logname)
    startmodel = logname.find(modelname)
    if startmodel == -1:
        return os.path.splitext(logname)[0]
    else:
        return logname[: startmodel - 1]


def _copy_keys(source, target):
    """copy some more info from one DataFrame to another to better distinguish runs/logs"""
    # tl_ = tl_[tl_.columns].apply(pd.to_numeric, errors='coerce')
    keys = ["Log", "LogFilePath", "Seed", "Model", "ModelFile", "Version"]
    for key in keys:
        if source.get(key) is not None:
            target[key] = source[key].iloc[0]


def get_dataframe(logfiles, timelines=False, verbose=False, merged_logs=False, prettyparams=False):
    """Create a dataframe with all stats of the logs

    - timelines=True: also create dictionary of timelines of all logs
    - verbose=True: print progress info
    - merged_logs: if False, only the last log in the file is parsed
    """

    glob_logfiles = []

    # Expand wildcards, skip non-existing elements
    for logfile in logfiles:
        logfile_expanded = glob.glob(logfile)
        if not logfile_expanded:
            print("Info: Log file not found: '%s'" % logfile)
        else:
            glob_logfiles.extend(logfile_expanded)

    log_infos = []
    for logfile in glob_logfiles:
        if verbose:
            print(f"processing {logfile}...")
        with open(logfile) as f:
            loglines = f.readlines()
            if merged_logs:
                header = [
                    ind
                    for ind, l in enumerate(loglines)
                    if re.search(logpattern.headers[0], l)
                ]
                header.append(len(loglines))
            else:
                header = [0, len(loglines)]
            for i,h in enumerate(range(len(header) - 1)):
                log_info = get_log_info(loglines[header[h] : header[h + 1]], verbose)
                if log_info is None:
                    print(f"error processing {logfile}")
                    continue
                # add some more information to better distinguish the individual runs/logs
                log_info["LogFilePath"] = os.path.abspath(logfile)
                log_info["Log"] = os.path.splitext(os.path.basename(logfile))[0]

                # add counter if using merged_logs:
                log_info["LogFilePath"] += f"({i+1})"

                if log_info.get("ModelFilePath"):
                    log_info["ModelFile"] = os.path.basename(
                        log_info["ModelFilePath"]
                    ).split(os.path.extsep)[0]
                    log_info["Log"] = _strip_modelname(
                        log_info["LogFilePath"], log_info["ModelFile"]
                    )
                else:
                    log_info["Log"] = os.path.splitext(
                        os.path.basename(log_info["LogFilePath"])
                    )[0]

                log_infos.append(log_info)

    allresults = []
    for log_info in log_infos:
        items = {
            key: value
            for (key, value) in log_info.items()
            if not isinstance(value, list) and not isinstance(value, dict)
        }
        allresults.append(items)

    summary = pd.DataFrame(allresults)

    if "Seed (Parameter)" in summary.keys():
        summary["Seed"] = summary["Seed (Parameter)"].fillna(0).astype(int).astype(str)
        summary = summary.drop(labels="Seed (Parameter)", axis=1)

    summary = fill_default_parameters(summary.replace("-", nan))
    if prettyparams:
        summary = add_categorical_descriptions(summary)

    if timelines:

        # collect norel log
        norel = pd.DataFrame()
        for log_info in log_infos:
            log = log_info.get("LogFilePath")
            final = summary[summary["LogFilePath"] == log]
            nrlines = log_info.get("NoRelLog")
            if nrlines is not None:
                norel_ = pd.DataFrame(nrlines).apply(
                    pd.to_numeric, errors="coerce"
                )
                _copy_keys(final, norel_)
                norel = norel.append(norel_, ignore_index=True)

        # collect root LP log
        rootlp = pd.DataFrame()
        for log_info in log_infos:
            log = log_info.get("LogFilePath")
            final = summary[summary["LogFilePath"] == log]
            slines = log_info.get("SimplexLog")
            blines = log_info.get("BarrierLog")
            simplex_ = pd.DataFrame(slines)
            barrier_ = pd.DataFrame(blines)
            crossover = False
            # filter out empty dictionaries and convert all values to numerics
            if barrier_.get("Iteration") is not None:
                barrier_ = barrier_[barrier_.columns].apply(
                    pd.to_numeric, errors="coerce"
                )
                _copy_keys(final, barrier_)
                barrier_["Type"] = "barrier"
                rootlp = rootlp.append(barrier_, ignore_index=True)
                crossover = True
            # filter out empty dictionaries and convert all values to numerics
            if simplex_.get("Iteration") is not None:
                simplex_ = simplex_[simplex_.columns].apply(
                    pd.to_numeric, errors="coerce"
                )
                _copy_keys(final, simplex_)
                simplex_["Type"] = "crossover" if crossover else "simplex"
                rootlp = rootlp.append(simplex_, ignore_index=True)

        # collect tree search log
        tl = pd.DataFrame()
        for log_info in log_infos:
            lines = log_info.get("TreeSearchLog")
            tl_ = pd.DataFrame(lines)
            # filter out empty dictionaries and convert all values to numerics
            if tl_.get("Time") is not None:
                log = log_info.get("LogFilePath")
                final = summary[summary["LogFilePath"] == log]
                # append one last row containing the final data
                tl_ = tl_.append(
                    pd.DataFrame(
                        {
                            "CurrentNode": final["NodeCount"],
                            "Incumbent": final["ObjVal"],
                            "BestBd": final["ObjBound"],
                            "Gap": final["MIPGap"],
                            "Time": final["Runtime"],
                        }
                    )
                )
                tl_ = tl_[tl_.columns].apply(pd.to_numeric, errors="coerce")
                _copy_keys(final, tl_)

                tl = tl.append(tl_, ignore_index=True)

        return summary, dict(nodelog=tl, rootlp=rootlp, norel=norel)
    else:
        return summary


def plot(df: pd.DataFrame, points="all", barmode="group", **kwargs):
    """plot different chart types to compare performance and see performance variability across random seeds

    uses Plotly express; all available keyword arguments can be passed through to px.bar(), px.scatter(), etc.
    """

    options = list(df.columns) + [None]

    if "Incumbent" in options:
        # read custom axis data or use common defaults for summary DataFrame
        x_default = kwargs.pop("x", "Time")
        y_default = kwargs.pop("y", "Incumbent")
        color_default = kwargs.pop("color", "Log")
    else:
        # read custom axis data or use common defaults for summary DataFrame
        x_default = kwargs.pop("x", "Log")
        y_default = kwargs.pop("y", "Runtime")
        color_default = kwargs.pop("color", "Seed")

    # set type to None to disable plotting until a type is selected
    type_default = kwargs.pop("type", None)

    # pop values for remaining widgets to avoid double inputs
    symbol_default = kwargs.pop("symbol", None)
    log_x_default = kwargs.pop("log_x", False)
    log_y_default = kwargs.pop("log_y", False)

    # check wether selected keys are available in DataFrame
    if x_default not in options:
        x_default = None
    if y_default not in options:
        y_default = None
    if color_default not in options:
        color_default = None

    switches = dict(
        x=widgets.Dropdown(options=options, value=x_default),
        y=widgets.Dropdown(options=options, value=y_default),
        color=widgets.Dropdown(options=options, value=color_default),
        type=widgets.Dropdown(
            options=["box", "bar", "scatter", "line"], value=type_default
        ),
        symbol=widgets.Dropdown(options=options, value=symbol_default),
        log_x=widgets.Checkbox(value=log_x_default),
        log_y=widgets.Checkbox(value=log_y_default),
    )

    @interact(**switches)
    def _(x, y, color, type, symbol, log_x, log_y):
        if type == "box":
            return px.box(
                df,
                x=x,
                y=y,
                color=color,
                points=points,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
        elif type == "bar":
            return px.bar(
                df,
                x=x,
                y=y,
                color=color,
                barmode=barmode,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
        elif type == "scatter":
            return px.scatter(
                df,
                x=x,
                y=y,
                color=color,
                symbol=symbol,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
        elif type == "line":
            return px.line(
                df,
                x=x,
                y=y,
                color=color,
                symbol=symbol,
                log_x=log_x,
                log_y=log_y,
                **kwargs,
            )
