from typing import Iterable
from bs4 import BeautifulSoup as BS

class CBRFParser:
    """
    Кастомный парсер для скрейпинга данных динамики валют с сайта ЦБ РФ
    """

    cbrf_url_base: str = "https://cbr.ru/currency_base/dynamics/"
    cbrf_data_req_url: str = "?UniDbQuery.Posted=True&UniDbQuery.so=1&UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.VAL_NM_RQ={}&UniDbQuery.From={}&UniDbQuery.To={}"

    def __init__(self, cbrf_url_base:str=cbrf_url_base) -> None:
        """
        Делаем инициализацию атрибутов инстанца дефолтными значениями из класса
        """
        self.cbrf_url_base = cbrf_url_base
        self.cbrf_data_req_url = self.cbrf_url_base + CBRFParser.cbrf_data_req_url
        self.currencies: dict = None
        self.date_intervals: dict = None
        self.initialized: bool = False
    
    @staticmethod
    def parseCurrencyBox(bsoup: BS) -> dict:
        """
        Выполняет парсинг комбо-бокса выбора валюты для выдачи
        """
        sel_box = bsoup.find('label', {"class": "input_label"})
        if sel_box:   
            return { op.getText().strip():op['value'] for op in sel_box.findAll('option')}
        return None 

    @staticmethod    
    def parseDateFilter(bsoup: BS) -> dict:
        """
        Выполняет парсинг date picker на предмет зашитых в него ограничений на допустимые начальную
        и конечную даты для выполненения запроса ('data-min-date' и 'data-max-date')
        """
        dp_box = bsoup.find('div', {"class": "datepicker-filter"})
        if dp_box:
            return {'data-min-date':dp_box['data-min-date'], 'data-max-date': dp_box['data-max-date']}
        return None

    @staticmethod
    def parseDataTableBlock(bsoup: BS) -> Iterable:
        """
        Генератор - выдает значения данных по валюте (таблицу) со страницы результата запроса
        """
        data_table = bsoup.find('table', {"class": "data"})
        if data_table:
            for tr in data_table.find_all('tr'):
                d = tuple(tr.getText() for tr in tr.findAll('td'))
                if len(d) == 3:
                    yield d
        return []

