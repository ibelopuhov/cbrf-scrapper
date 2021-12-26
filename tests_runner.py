from tests.test_and_analysis import make_base_request_mock, make_mock_request_to_R01660

def test_mock_base_got_result() -> None:
    bs = make_base_request_mock()
    header = bs.find('header')
    assert header

def test_mock_R01660_got_result() -> None:
    bs = make_mock_request_to_R01660()
    header = bs.find('header')
    assert header