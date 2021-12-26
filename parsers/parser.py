from typing import Iterable
from bs4 import BeautifulSoup as BS
import requests
from requests.exceptions import Timeout

class CBRFParserError(Exception):
    ...

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
    
    def init_parser(self) -> bool:
        bs = self._make_request_to_base_page()
        
        self.currencies = self.parseCurrencyBox(bs)
        if not self.currencies or len(self.currencies) < 100:
            raise CBRFParserError("Ошибка парсинга выбора валюты")  
        
        self.date_intervals = self.parseDateFilter(bs)
        if not self.date_intervals or len(self.date_intervals) != 2:
            raise CBRFParserError("Ошибка парсинга минимальной и максимально-допустимой даты для запроса")
        
        self.initialized = True
        return self.initialized

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

    @staticmethod
    def make_request(url: str, *args) -> BS:
        # make url
        comb_url = url if not args else url.format(*args) 
        # print(f"Do request to {comb_url=}")

        try:
            resp = requests.get(comb_url)

            if resp.ok:
                return BS(resp.text, features="html.parser")

        except Timeout as te:
            print(te)
        finally:
            resp.close()

    def _make_request_to_base_page(self) -> BS:
        """
        Выполняет запрос на получение базовой html-страницы (формы запроса на получение исторических данных)
        """
        return self.make_request(self.cbrf_url_base)

    def _make_request_for_currency_data(self, currency_name: str) -> BS:
        """
        Выполняет запрос на выдачу страницы с историческими данными по валюте,
        наименованиие которой указано в параметре currency_name
        """
        if self.initialized:
            if self.currencies.get(currency_name):
                return self.make_request(self.cbrf_data_req_url, 
                    self.currencies[currency_name], 
                    self.date_intervals['data-min-date'], 
                    self.date_intervals['data-max-date'])
            else:
                raise CBRFParserError(f"Нет информации о запрашиваемой валюте '{currency_name}'")
        else:
             raise CBRFParserError("Парсер не инициализирован актуальными данными. Выполните вызов метода init_parser().")
   
    def get_currencies_list(self) -> Iterable:
        if not self.initialized:
            raise CBRFParserError("Парсер не инициализирован актуальными данными. Выполните вызов метода init_parser().")
        
        for k in self.currencies.keys():
            yield k
    
    def get_currency_id_by_name(self, currency_name: str) -> str:
        if not self.initialized:
            raise CBRFParserError("Парсер не инициализирован актуальными данными. Выполните вызов метода init_parser().")
        
        if self.currencies.get(currency_name):
            return self.currencies.get(currency_name)
        else:
            raise CBRFParserError(f"Нет информации о запрашиваемой валюте '{currency_name}'")
    
    def make_scrapping(self, currency_name: str) -> Iterable:
        """
        Непосредственно выполняет скраппинг данных для запрашиваемой валюты по ее имени
        """
        bs = self._make_request_for_currency_data(currency_name)
        return self.parseDataTableBlock(bs)