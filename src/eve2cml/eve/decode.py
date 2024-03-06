import base64
import logging

_LOGGER = logging.getLogger(__name__)


def decode_data(data: str):
    try:
        decoded = base64.b64decode(data).decode("utf-8")
    except Exception as exc:
        _LOGGER.exception("b64 decode %s", exc)
        decoded = data
    return decoded
