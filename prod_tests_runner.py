# Функциональные тесты с реальным получением данных
import os
from pathlib import Path
from parsers.parser import CBRFParser
import pytest

# CBRFParser tests

@pytest.mark.skip(reason="skip while dev")
def test_init_parser() -> None:
    cbrfp = CBRFParser()
    # Проверяем что работает request-подключение и заполняются данными (2 парсера - валюты и даты) 
    assert cbrfp.init_parser()
    assert cbrfp.currencies and len(cbrfp.currencies) == 142
    assert cbrfp.currencies.get('Суданский фунт') == 'R01660'
    assert len(cbrfp.date_intervals) == 2

@pytest.mark.skip(reason="skip while dev")
def test_prod_parse_currency_data_table() -> None:
    cbrfp = CBRFParser()
    assert cbrfp.init_parser()

    currency_name = 'Суданский фунт'
    bs = cbrfp._make_request_for_currency_data(currency_name)
    data = cbrfp.parseDataTableBlock(bs)
    assert len(list(data)) >= 144

# run program functions tests

def test_init_db() -> None:
    assert False

def test_delete_db() -> None:
    assert False

def test_currency_list() -> None:
    assert False

def test_scrap_currency() -> None:
    assert False

def test_dump_currency() -> None:
    assert False

