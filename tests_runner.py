from tests.test_and_analysis import make_base_request_mock, make_mock_request_to_R01660
from parsers.parser import CBRFParser

def test_mock_base_got_result() -> None:
    bs = make_base_request_mock()
    header = bs.find('header')
    assert header

def test_mock_R01660_got_result() -> None:
    bs = make_mock_request_to_R01660()
    header = bs.find('header')
    assert header

def test_parse_currency_box() -> None:
    currency_box_map: dict = CBRFParser.parseCurrencyBox(make_base_request_mock())
    assert currency_box_map
    assert len(currency_box_map) == 142

def test_parse_date_filter() -> None:
    date_filter_data: dict =  CBRFParser.parseDateFilter(make_base_request_mock())
    assert date_filter_data

def test_parse_currency_table() -> None:
    currency_timeline_data: dict = CBRFParser.parseDataTableBlock(make_mock_request_to_R01660())
    data_list = list(currency_timeline_data)
    len_data = len(data_list)
    # print(data_list)
    assert len_data == 144