# Создаем mock методы для получения данных с основной страници и с одной из возможных страниц с данными
import os
from bs4 import BeautifulSoup as BS
from pathlib import Path

current_path = Path(os.path.dirname(__file__))

# print(f"{current_path=}")
# print(f'{current_path.joinpath("cbr.ru.base.html")=}')

def make_base_request_mock() -> BS:
    with open(current_path.joinpath("cbr.ru.base.html"), "r", encoding="utf-8") as r:
        html_data = r.read()
        # print(html_data)
        return BS(html_data, features="html.parser")

def make_mock_request_to_R01660() -> BS:
    with open(current_path.joinpath("cbr.ru.R01660.html"), "r", encoding="utf-8") as r:
        html_data = r.read()
        # print(html_data)
        return BS(html_data, features="html.parser")
