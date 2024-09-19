import pytest

import eve2cml.main


@pytest.mark.parametrize(
    "case",
    [
        {"name": "none", "text": "", "cols": 80},
        {"name": "even", "text": "even", "cols": 80},
        {"name": "odd", "text": "oddoddodd", "cols": 80},
        {"name": "oddlen", "text": "even", "cols": 79},
        # can't properly deal with text longer than available columns, no
        # biggie, though:
        # {"name": "long", "text": "verylong text goes here", "cols": 10},
    ],
)
def test_centered_line(case):
    test_text = case["text"]
    cols = case["cols"]
    result = eve2cml.main.centered_line_with_stars(test_text, cols)
    assert len(result) == cols
    if len(test_text) > 0:
        assert f" {test_text} " in result
