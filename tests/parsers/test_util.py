import pytest

from grblogtools.parsers.util import model_type


@pytest.mark.parametrize(
    "kwargs, result",
    [
        ({}, "LP"),
        ({"discrete_vars": 1}, "MIP"),
        ({"quad_nonzeros": 1}, "QP"),
        ({"discrete_vars": 1, "quad_nonzeros": 1}, "MIQP"),
        ({"quad_constrs": 1}, "QCP"),
        ({"quad_nonzeros": 1, "quad_constrs": 1}, "QCP"),
        ({"discrete_vars": 1, "quad_constrs": 1}, "MIQCP"),
        ({"discrete_vars": 1, "quad_nonzeros": 1, "quad_constrs": 1}, "MIQCP"),
    ],
)
def test_model_type(kwargs, result):
    assert model_type(**kwargs) == result
