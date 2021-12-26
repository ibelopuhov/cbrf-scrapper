from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from sqlite3.dbapi2 import Connection
from typing import Iterable
import sqlite3

@dataclass
class DbParameters:
    """
    Класс с типичными параметрами соединения с СУБД
    """
    dbname: str
    host: str = 'localhost'
    port: int = '5432'
    username: str = 'user'
    password: str = 'password'

class CBRFDBStoregeManager:
    """
    Абстрактный класс для сохранения и обрабтки информации, полученной от парсера
    """
    dbconf: DbParameters

    @abstractmethod
    def init_db(self) -> None:
        ...
    
    @abstractmethod
    def update_currencies(self, cur_dict: dict) -> None:
        ...
    
    @abstractmethod
    def fill_currency_timeline(self, timeline_coll: Iterable, currency_id: str) -> None:
        ...

    @abstractmethod
    def get_currency_timeline_by_name(self, currency_name: str) -> Iterable:
        ...

# Делаем простую реализацию на SQLite
class SQLiteStorageManager(CBRFDBStoregeManager):
    """
    Простая реализация хранения данных на SQLite
    """

    def __init__(self, dbconf: DbParameters) -> None:
        self.dbconf = dbconf
        self.initialized = False
    
    @contextmanager
    def _get_conn(self) -> Connection:
        try:
            conn = sqlite3.connect(self.dbconf.dbname)
            print(f"База данных {self.dbconf.dbname} подключена к SQLite")
            
            try:
                yield conn
                conn.commit()
            finally:
                if (conn):
                    conn.close()
                    print(f"Соединение с БД {self.dbconf.dbname} закрыто")
        except sqlite3.Error as error:
            print(f"Ошибка БД {self.dbconf.dbname}", error)
            raise error   

    def init_db(self) -> None:
        table_currencies = '''
            CREATE TABLE IF NOT EXISTS currencies (
                currency_id TEXT,
                currency_name TEXT NOT NULL,
                PRIMARY KEY (currency_id, currency_name)
            );
            '''
        table_currencies_timeline = '''
            CREATE TABLE IF NOT EXISTS currencies_timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    currency_id TEXT NOT NULL, 
                    date_ datetime, 
                    unit INTEGER NOT NULL, 
                    curs REAL NOT NULL,
                    FOREIGN KEY (currency_id)
                        REFERENCES currencies (currency_id) );
            '''
        with self._get_conn() as conn:     
            conn.execute(table_currencies)
            conn.execute(table_currencies_timeline)
        
        self.initialized = True



