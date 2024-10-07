from pathlib import PosixPath
from unittest import mock

import pytest

from eve2cml import main


@pytest.fixture
def mock_args(mocker):
    return mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=mock.Mock(
            level="warning",
            stdout=False,
            nocolor=False,
            dump=False,
            all=False,
            text=False,
            file_or_zip=["test.unl"],
            mapper=None,
        ),
    )


def test_main_yaml_output(mocker, mock_args):
    _ = mock_args
    mocker.patch(
        "eve2cml.main.convert_files",
        return_value=[mock.Mock(filename="test", as_cml_dict=lambda: {})],
    )
    mock_open = mocker.patch("builtins.open", mock.mock_open())
    main.main()
    mock_open.assert_called_once_with(PosixPath("test.yaml"), "w", encoding="utf-8")


def test_main_dump(mocker, mock_args):
    mock_args.return_value.text = True
    mocker.patch(
        "eve2cml.main.convert_files",
        return_value=[
            mock.Mock(
                filename="test",
                topology=mock.Mock(nodes=[], networks=[]),
                objects=mock.Mock(textobjects=[]),
            )
        ],
    )
    mock_open = mocker.patch("builtins.open", mock.mock_open())
    main.main()
    mock_open.assert_called_once_with("test.txt", "w", encoding="utf-8")
