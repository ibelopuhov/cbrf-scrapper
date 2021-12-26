# Функциональные тесты с реальным получением данных
import os
from pathlib import Path
from parsers.parser import CBRFParser
from parsers.db import DbParameters, SQLiteStorageManager, CBRFDBStoregeManager
import pytest

# CBRFParser tests

@pytest.mark.skip(reason="temporary skip")
def test_init_parser() -> None:
    cbrfp = CBRFParser()
    # Проверяем что работает request-подключение и заполняются данными (2 парсера - валюты и даты) 
    assert cbrfp.init_parser()
    assert cbrfp.currencies and len(cbrfp.currencies) == 142
    assert cbrfp.currencies.get('Суданский фунт') == 'R01660'
    assert len(cbrfp.date_intervals) == 2

@pytest.mark.skip(reason="temporary skip")
def test_prod_parse_currency_data_table() -> None:
    cbrfp = CBRFParser()
    assert cbrfp.init_parser()

    currency_name = 'Суданский фунт'
    bs = cbrfp._make_request_for_currency_data(currency_name)
    data = cbrfp.parseDataTableBlock(bs)
    assert len(list(data)) >= 144

# DB manager tests

def test_sqlite_db_initialization() -> None:
    db_file_name = "test_database.db"

    # удаляем возможно оставшийся файл БД в случае неудачного прохождения теста    
    if Path(db_file_name).exists():
        os.remove(db_file_name)

    dbconf = DbParameters(dbname=db_file_name)
    stm: CBRFDBStoregeManager = SQLiteStorageManager(dbconf)
    
    assert not stm.initialized

    stm.init_db()
    assert stm.initialized
    
    assert Path(db_file_name).exists()
    os.remove(db_file_name)
    assert not Path(db_file_name).exists()
    