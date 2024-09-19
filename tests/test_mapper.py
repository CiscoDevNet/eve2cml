import logging
from pathlib import Path

import pytest

from eve2cml import mapper


def test_mapper():
    m = mapper.Eve2CMLmapper().load()
    assert m

    d = m.as_dict()
    assert d

    with open("/dev/null", "w", encoding="utf-8") as out:
        m.dump(out)

    nd = m.node_def("iol", "iol", "i86bi_linux_l2")
    assert nd

    nd = m.node_def("qemu", "vios", "")
    assert nd

    label = m.cml_iface_label(0, "iosv", "gaga")
    assert label != "gaga"

    label = m.cml_iface_label(0, "doesntexist", "gaga")
    assert label == "gaga"


def test_custom_mapper(request, caplog):
    caplog.set_level(logging.INFO)

    caplog.clear()
    _ = mapper.Eve2CMLmapper().load("doesntexist")
    assert "mapper provided but not found" in caplog.text

    caplog.clear()
    testdata = Path(request.path).parent / "testdata" / "map1.yaml"
    _ = mapper.Eve2CMLmapper().load(str(testdata))
    assert "custom mapper loaded" in caplog.text

    caplog.clear()
    testdata = Path(request.path).parent / "testdata" / "map2.yaml"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        _ = mapper.Eve2CMLmapper().load(str(testdata))
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1
    assert "can't decode" in caplog.text

    caplog.clear()
    testdata = Path(request.path).parent / "testdata" / "hub.unl"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        _ = mapper.Eve2CMLmapper().load(str(testdata))
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1
    assert "can't use provided mapper" in caplog.text
