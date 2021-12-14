from grblogtools.norel import NoRelParser


norel_section_test_data = """
Variable types: 19 continuous, 297 integer (297 binary)
Found heuristic solution: objective 3.133356e+09
Starting NoRel heuristic
Elapsed time for NoRel heuristic: 5s
Found heuristic solution: objective 3.033354e+09
Found heuristic solution: objective 1.450014e+09
Elapsed time for NoRel heuristic: 10s (best bound 8.00002e+08)
Found heuristic solution: objective 1.400013e+09
Elapsed time for NoRel heuristic: 16s (best bound 8.00002e+08)
Found heuristic solution: objective 1.200013e+09
Elapsed time for NoRel heuristic: 21s (best bound 8.00002e+08)
Elapsed time for NoRel heuristic: 27s (best bound 8.00002e+08)
Elapsed time for NoRel heuristic: 93s (best bound 8.00002e+08)

Root simplex log...
"""


def test_norel_parser():
    """ Pass all test lines in sequence and test summary/timeline. """
    parser = NoRelParser()
    lines = norel_section_test_data.strip().split("\n")
    parser.parse_lines(lines)
    # only the 'Root simplex log...' line was passed but not parsed.
    assert parser.ignored_lines == 1
    assert parser.summary == {
        "NoRelBestSolution": 1.200013e9,
        "NoRelTime": 93.0,
        "NoRelBestBound": 8.00002e8,
    }
    assert parser.timeline == [
        {"Time": 5.0},
        {"Time": 10.0, "BestBd": 8.00002e8, "Incumbent": 1.450014e9},
        {"Time": 16.0, "BestBd": 8.00002e8, "Incumbent": 1.400013e9},
        {"Time": 21.0, "BestBd": 8.00002e8, "Incumbent": 1.200013e9},
        {"Time": 27.0, "BestBd": 8.00002e8, "Incumbent": 1.200013e9},
        {"Time": 93.0, "BestBd": 8.00002e8, "Incumbent": 1.200013e9},
    ]
