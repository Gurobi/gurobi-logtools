from grblogtools.helpers import parse_block
from grblogtools.termination import TerminationParser

# TODO add tests for other status parsers

test_lines_1 = """
Solution count 10: 1.20001e+09 1.26668e+09 1.40001e+09 ... 1.50001e+09
Optimal solution found (tolerance 1.00e-04)
Best objective 1.200012600000e+09, best bound 1.200012600000e+09, gap 0.0000%
"""


def test_termination_parser():
    parser = TerminationParser()
    parse_block(parser, test_lines_1)
    assert parser.get_summary() == {
        "SolCount": 10,
        "ObjVal": 1.2000126e09,
        "ObjBound": 1.2000126e09,
        "MIPGap": 0.0,
        "Status": "OPTIMAL",
    }
