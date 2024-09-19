import pytest

from eve2cml.eve.textobject import rgb_to_hex


def test_rgb_to_hex():
    assert rgb_to_hex("rgb(127, 140, 141)") == "#7F8C8DFF"
    assert rgb_to_hex("rgb(255, 0, 0)") == "#FF0000FF"
    assert rgb_to_hex("rgb(0, 255, 0)") == "#00FF00FF"
    assert rgb_to_hex("rgb(0, 0, 255)") == "#0000FFFF"
    assert rgb_to_hex("rgb(255, 255, 255)") == "#FFFFFFFF"
    assert rgb_to_hex("rgb(255, 255, 255, 0)") == "#FFFFFF00"
    assert rgb_to_hex("rgb(255, 255, 255, 128)") == "#FFFFFF80"
    assert rgb_to_hex("rgba(234, 234, 244, 0)") == "#EAEAF400"


def test_rgb_to_hex_invalid_input():
    with pytest.raises(ValueError):
        rgb_to_hex("invalid_rgb_string")
    with pytest.raises(ValueError):
        rgb_to_hex("rgb(256, 255, 255)")
    with pytest.raises(ValueError):
        rgb_to_hex("rgb(255, 255, 256)")
    with pytest.raises(ValueError):
        rgb_to_hex("rgb(-1, 0, 0)")
    with pytest.raises(ValueError):
        rgb_to_hex("rgb(0, -1, 0)")
    with pytest.raises(ValueError):
        rgb_to_hex("rgb(0, 0, -1)")
