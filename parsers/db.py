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
            # print(f"База данных {self.dbconf.dbname} подключена к SQLite")
            
            try:
                yield conn
                conn.commit()
            finally:
                if (conn):
                    conn.close()
                    # print(f"Соединение с БД {self.dbconf.dbname} закрыто")
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

    def update_currencies(self, cur_dict: dict) -> None:
        ins_q = '''
            insert into currencies (currency_name, currency_id)
            values (?, ?);
        '''
        with self._get_conn() as conn:
            conn.execute("delete from currencies;")
            conn.executemany(ins_q, [(k, v) for k, v in cur_dict.items()])

    def fill_currency_timeline(self, timeline_coll: Iterable, currency_id: str) -> None:
        del_q = '''
            delete from currencies_timeline where currency_id=?;
        '''
        
        ins_q = '''
            insert into currencies_timeline (currency_id, date_, unit, curs)
            values (?, ?, ?, ?);
        '''
        with self._get_conn() as conn:
            conn.execute(del_q, (currency_id, ))
            conn.executemany(ins_q, [(currency_id, tp[0], tp[1], tp[2]) for tp in timeline_coll])

    def get_currency_timeline_by_name(self, currency_name: str) -> Iterable:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            currency_id = None
            cur_id_row = cursor.execute("select currency_id from currencies where currency_name=?;", (currency_name, )).fetchone()
            if cur_id_row:
                currency_id = cur_id_row[0]
            else:
                # Если валюты не найдено среди таблицы валют - сразу возвращаем пустой список 
                # (пока стратегия такая, возможно ошибку кидать)
                cursor.close()
                return []

            cursor.close()

            if currency_id:
                cursor = conn.cursor()
                for row in cursor.execute("select * from currencies_timeline where currency_id=?", (currency_id, )):
                    yield row
                cursor.close()
            else:
                return []

    def __str__(self) -> str:
        return "SQLite storage manager"