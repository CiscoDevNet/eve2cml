import eve2cml.main
import pytest


@pytest.mark.parametrize(
    "case",
    [
        {"name": "none", "text": "", "cols": 80},
        {"name": "even", "text": "even", "cols": 80},
        {"name": "odd", "text": "oddoddodd", "cols": 80},
        {"name": "oddlen", "text": "even", "cols": 79},
    ],
)
def test_centered_line(case):
    name = case["text"]
    result = eve2cml.main.centered_line_with_stars(name)
    assert len(result) == 80
    if len(name) > 0:
        assert f" {name} " in result
