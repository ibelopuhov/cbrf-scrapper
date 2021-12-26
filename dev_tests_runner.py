from tests.test_and_analysis import make_base_request_mock, make_mock_request_to_R01660
from parsers.parser import CBRFParser
from parsers.db import DbParameters, SQLiteStorageManager, CBRFDBStoregeManager
import pytest
from pathlib import Path
import os

# Parsers mock tests

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

# SQlite DB manager implementation tests

@pytest.fixture
def sqlite_config() -> DbParameters:
    db_file_name = "test_database.db"
    yield DbParameters(dbname=db_file_name)
    if Path(db_file_name).exists():
        os.remove(db_file_name)

@pytest.fixture
def gen_empty_sqlite_dbmanager(sqlite_config) -> CBRFDBStoregeManager:
    stm: CBRFDBStoregeManager = SQLiteStorageManager(sqlite_config)
    stm.init_db()
    assert stm.initialized
    yield stm

@pytest.fixture
def gen_currency_box_data() -> dict:
    currency_box_map: dict = CBRFParser.parseCurrencyBox(make_base_request_mock())
    assert len(currency_box_map) == 142
    yield currency_box_map

@pytest.fixture
def gen_timeline_currency_data() -> dict:
    currency_timeline_data:dict = CBRFParser.parseDataTableBlock(make_mock_request_to_R01660())
    # assert len(list(currency_timeline_data)) == 144
    yield currency_timeline_data

def test_currency_table_init(gen_empty_sqlite_dbmanager, gen_currency_box_data) -> None:
    stm: SQLiteStorageManager = gen_empty_sqlite_dbmanager
    stm.update_currencies(cur_dict=gen_currency_box_data)
    with stm._get_conn() as conn:
        cursor = conn.cursor()
        res = cursor.execute("SELECT count(*) from currencies;").fetchone()
        assert res[0] == 142

def test_filling_timeline_data_and_returning_all_results(gen_empty_sqlite_dbmanager, gen_currency_box_data, gen_timeline_currency_data) -> None:
    stm: SQLiteStorageManager = gen_empty_sqlite_dbmanager
    stm.update_currencies(cur_dict=gen_currency_box_data)

    stm.fill_currency_timeline(timeline_coll=gen_timeline_currency_data, currency_id='R01660')
    with stm._get_conn() as conn:
        cursor = conn.cursor()
        res = cursor.execute("SELECT count(*) from currencies_timeline;").fetchone()
        print(res)
        assert res[0] == 144
    
    # Получить реально загруженные ранее тестовые данные 
    assert len(list(stm.get_currency_timeline_by_name('Суданский фунт'))) == 144
    # Проверить корректность возврата пустого списка на несуществующей или ошибочном наименовании валюты
    assert len(list(stm.get_currency_timeline_by_name('Не Суданский фунт'))) == 0
    # Null result
    assert len(list(stm.get_currency_timeline_by_name(None))) == 0