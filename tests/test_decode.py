from eve2cml.eve.decode import decode_data


def test_decode_data():
    # Test when data is None
    assert decode_data(None) == ""

    # Test when data is a valid base64 encoded string
    data = "SGVsbG8gV29ybGQh"
    expected_result = "Hello World!"
    assert decode_data(data) == expected_result

    # Test when data is an invalid base64 encoded string
    invalid_data = "InvalidData"
    assert decode_data(invalid_data) == invalid_data
