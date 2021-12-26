# Функциональные тесты с реальным получением данных

from pathlib import Path
from parsers.parser import CBRFParser, CBRFParserError
import pytest
from run import stm, db_filename, init_db, delete_db, scrap_currency, dump_currency

# CBRFParser tests
# currency_name = 'Суданский фунт'
# currency_id = 'R01660'
# currency_min_items = 144

currency_name = 'Украинский карбованец'
currency_id = 'R01720'
currency_min_items = 6684

# @pytest.mark.skip(reason="skip while dev")
def test_init_parser() -> None:
    cbrfp = CBRFParser()
    # Проверяем что работает request-подключение и заполняются данными (2 парсера - валюты и даты) 
    assert cbrfp.init_parser()
    assert cbrfp.currencies and len(cbrfp.currencies) == 142
    assert cbrfp.currencies.get(currency_name) == currency_id
    assert len(cbrfp.date_intervals) == 2

# @pytest.mark.skip(reason="skip while dev")
def test_prod_parse_currency_data_table() -> None:
    cbrfp = CBRFParser()
    assert cbrfp.init_parser()
    bs = cbrfp._make_request_for_currency_data(currency_name)
    data = cbrfp.parseDataTableBlock(bs)
    assert len(list(data)) >= currency_min_items

# run program functions tests

@pytest.fixture
def gen_prod_sqlite_database() -> None:
    # Проверяем, если файл БД существует (иначе затрем прод базу нашими тестами)
    assert not Path(db_filename).exists()
    init_db()
    yield
    delete_db()
    assert not Path(db_filename).exists()

def test_run_functionality(gen_prod_sqlite_database) -> None:
    scrap_currency(currency_name)
    dump_currency(currency_name)
    len(list(stm.get_currency_timeline_by_name(currency_name)))
    assert len(list(stm.get_currency_timeline_by_name(currency_name))) >= currency_min_items
    # Дополнительно тестируем на запрос несуществующей валюты
    with pytest.raises(CBRFParserError):
        scrap_currency("Валюта которой н")

