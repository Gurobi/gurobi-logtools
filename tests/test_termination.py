from grblogtools.helpers import parse_block
from grblogtools.termination import TerminationParser

# TODO add tests for other status parsers

test_lines_1 = """
Thread count was 8 (of 8 available processors)
Solution count 10: 1.20001e+09 1.26668e+09 1.40001e+09 ... 1.50001e+09
Optimal solution found (tolerance 1.00e-04)
Best objective 1.200012600000e+09, best bound 1.200012600000e+09, gap 0.0000%
"""


test_lines_2 = """
Thread count was 8 (of 8 available processors)

Solution count 10: 1.50001e+09 1.50001e+09 1.50001e+09 ... 1.60001e+09

Time limit reached
Best objective 1.500006024411e+09, best bound 9.000096250000e+08, gap 39.9996%
"""


def test_termination_parser_1():
    parser = TerminationParser()
    parse_block(parser, test_lines_1)
    assert parser.get_summary() == {
        "Threads": 8,  # clashes with the HeaderParser result (should always match)
        "Cores": 8,  # should always match logical cores?
        "SolCount": 10,
        "ObjVal": 1.2000126e09,
        "ObjBound": 1.2000126e09,
        "MIPGap": 0.0,
        "Status": "OPTIMAL",
    }


def test_termination_parser_2():
    parser = TerminationParser()
    parse_block(parser, test_lines_2)
    assert parser.get_summary() == {
        "Threads": 8,
        "Cores": 8,
        "SolCount": 10,
        "ObjVal": 1.500006024411e09,
        "ObjBound": 9.000096250000e08,
        "MIPGap": 0.399996,
        "Status": "TIME_LIMIT",
    }
