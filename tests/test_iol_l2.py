from pathlib import Path

import pytest

import eve2cml.main


@pytest.mark.parametrize(
    "filename",
    [
        "ioll2-v1.unl",
        "ioll2-v2.unl",
    ],
)
def test_iol_conversion(request, filename):
    testdata = Path(request.path).parent / "testdata" / filename
    mapper = eve2cml.main.Eve2CMLmapper().load()
    labs = eve2cml.main.convert_files(str(testdata), mapper)
    assert len(labs) == 1
    result = labs[0].as_cml_dict()
    assert result["nodes"][0]["node_definition"] == "ioll2-xe"
