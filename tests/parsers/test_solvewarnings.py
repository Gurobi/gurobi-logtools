import pytest

from gurobi_logtools.parsers.solvewarnings import SolveWarningsParser


@pytest.mark.parametrize(
    "line,expected_warning",
    [
        (
            "Warning: mps file contains small (< 1e-13) coefficients, ignored",
            "mps file contains small (< 1e-13) coefficients, ignored",
        ),
        ("Warning: some other warning message", "some other warning message"),
        ("Warning: another warning", "another warning"),
        ("Warning: test", "test"),
    ],
)
def test_parse_single_warning(line: str, expected_warning: str) -> None:
    parser = SolveWarningsParser()
    result = parser.parse(line)

    assert result.matched is True
    summary = parser.get_summary()
    assert "Warnings" in summary
    assert len(summary["Warnings"]) == 1
    assert summary["Warnings"][0] == expected_warning


def test_parse_multiple_warnings() -> None:
    parser = SolveWarningsParser()
    lines = [
        "Warning: mps file contains small (< 1e-13) coefficients, ignored",
        "Warning: some other warning message",
        "Not a warning line",
        "Warning: another warning",
    ]

    for line in lines:
        parser.parse(line)

    summary = parser.get_summary()
    assert "Warnings" in summary
    assert len(summary["Warnings"]) == 3
    assert (
        summary["Warnings"][0]
        == "mps file contains small (< 1e-13) coefficients, ignored"
    )
    assert summary["Warnings"][1] == "some other warning message"
    assert summary["Warnings"][2] == "another warning"


def test_parse_duplicate_warnings() -> None:
    parser = SolveWarningsParser()
    lines = [
        "Warning: duplicate warning",
        "Some other line",
        "Warning: duplicate warning",
        "Warning: different warning",
        "Warning: duplicate warning",
    ]

    for line in lines:
        parser.parse(line)

    summary = parser.get_summary()
    assert "Warnings" in summary
    assert len(summary["Warnings"]) == 2
    assert summary["Warnings"][0] == "duplicate warning"
    assert summary["Warnings"][1] == "different warning"


@pytest.mark.parametrize(
    "line",
    [
        "This is a normal log line",
        "Normal log line 1",
        "Not a warning line",
        "Warning without colon",
        "NOTWARNING: something",
    ],
)
def test_parse_non_warning_line(line: str) -> None:
    parser = SolveWarningsParser()
    result = parser.parse(line)

    assert result.matched is False
    summary = parser.get_summary()
    assert summary == {}


def test_empty_summary_when_no_warnings() -> None:
    parser = SolveWarningsParser()
    lines = [
        "Normal log line 1",
        "Normal log line 2",
        "Another normal line",
    ]

    for line in lines:
        parser.parse(line)

    summary = parser.get_summary()
    assert summary == {}


def test_warning_with_extra_whitespace() -> None:
    parser = SolveWarningsParser()
    line = "Warning:   text with extra spaces   "
    result = parser.parse(line)

    assert result.matched is True
    summary = parser.get_summary()
    assert summary["Warnings"][0] == "text with extra spaces"
