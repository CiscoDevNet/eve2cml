import eve2cml.main


def test_centered_line():
    # Test when data is None
    full = eve2cml.main.centered_line_with_stars()
    assert len(full) == 80

    partial = eve2cml.main.centered_line_with_stars("this")
    assert len(full) == 80
    assert " this " in partial
