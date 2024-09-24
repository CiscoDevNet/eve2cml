import io
from pathlib import Path

import pytest

import eve2cml.main


@pytest.mark.parametrize(
    "case",
    [
        {
            "filename": "hub.unl",
            "nodes": 4,
            "links": 3,
            "annotations": 1,
        },
        {
            "filename": "nat.unl",
            "nodes": 4,
            "links": 2,
            "annotations": 0,
        },
        {
            "filename": "pnet.unl",
            "nodes": 4,
            "links": 3,
            "annotations": 0,
        },
        {
            "filename": "test.unl",
            "nodes": 2,
            "links": 1,
            "annotations": 4,
        },
        {
            "filename": "test.zip",
            "nodes": 2,
            "links": 1,
            "annotations": 4,
        },
    ],
)
def test_integration(request, case):
    testdata = Path(request.path).parent / "testdata" / case["filename"]
    mapper = eve2cml.main.Eve2CMLmapper().load()
    labs = eve2cml.main.convert_files(str(testdata), mapper)
    assert len(labs) == 1
    result = labs[0].as_cml_dict()
    assert len(result.keys()) == 4
    assert len(result["nodes"]) == case["nodes"]
    assert len(result["links"]) == case["links"]
    assert len(result["annotations"]) == case["annotations"]


def test_text_out(request):
    testdata = Path(request.path).parent / "testdata" / "test.unl"
    mapper = eve2cml.main.Eve2CMLmapper().load()
    labs = eve2cml.main.convert_files(str(testdata), mapper)
    assert len(labs) == 1
    text_obj = io.StringIO()
    eve2cml.main.dump_as_text(text_obj, labs[0], True)
    text_obj.seek(0)
    content = text_obj.read()
    assert len(content) > 0


def test_no_file():
    mapper = eve2cml.main.Eve2CMLmapper().load()
    with pytest.raises(SystemExit, match="1"):
        eve2cml.main.convert_files("doesntexist", mapper)
