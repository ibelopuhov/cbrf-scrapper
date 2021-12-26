# Функциональные тесты с реальным получением данных
from parsers.parser import CBRFParser


def test_init_parser() -> None:
    cbrfp = CBRFParser()
    # Проверяем что работает request-подключение и заполняются данными (2 парсера - валюты и даты) 
    assert cbrfp.init_parser()
    assert cbrfp.currencies and len(cbrfp.currencies) == 142
    assert cbrfp.currencies.get('Суданский фунт') == 'R01660'
    assert len(cbrfp.date_intervals) == 2

def test_prod_parse_currency_data_table() -> None:
    cbrfp = CBRFParser()
    assert cbrfp.init_parser()
    currency_name = 'Суданский фунт'
    bs = cbrfp._make_request_for_currency_data(currency_name)
    data = cbrfp.parseDataTableBlock(bs)
    assert len(list(data)) >= 144

