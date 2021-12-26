import argh
from parsers.parser import CBRFParser
from parsers.db import CBRFDBStoregeManager, DbParameters, SQLiteStorageManager
from pathlib import Path
import os

# Глобальные переменные для упрощения, поскольку у нас нет других имплементаций
db_filename = "cbrf_currencies.db"
dbconf:DbParameters = DbParameters(dbname=db_filename) 
stm: CBRFDBStoregeManager = SQLiteStorageManager(dbconf=dbconf)

def init_db() -> None:
    """
    Инициализировать пустую БД (требуется выполнить один раз перед первым использованием скраппинга)
    и в случае, если список валют изменился.
    """
    stm.init_db()

    cbrfp = CBRFParser()
    if cbrfp.init_parser():
        stm.update_currencies(cbrfp.currencies)
        print(f"Успешно обновлен список валют")
    
    print(f"БД инициализирована. StorageManager: '{stm}'; файл БД '{db_filename}' ")

def scrap_currency(currency_name: str) -> None:
    """
    Запустить скраппинг данных указанной валюты (как на сайте при выборе в ComboBox)
    """
    if not Path(db_filename).exists():
        print(f"Файл БД '{db_filename}' не найден. Пожалуйста инициализируйте БД перед использованием парсера")
        return
    
    print(f"Получаем данные по запрашиваемой валюте '{currency_name}'")
    cbrfp = CBRFParser()
    if cbrfp.init_parser():
        currency_id = cbrfp.get_currency_id_by_name(currency_name)
        stm.fill_currency_timeline(cbrfp.make_scrapping(currency_name), currency_id)
    else:
        print("Инициализация парсера не выполнена. Парсинг данных невозможен.")

def delete_db() -> None:
    """
    Удалить файл БД sqlite
    """
    if Path(db_filename).exists():
        os.remove(db_filename)
        print(f"Файл БД '{db_filename}' удален успешно")
    else:
        print(f"Файл БД '{db_filename} не найден'")

def currency_list() -> None:
    """
    Возвращает список знакомых парсеру валют
    """
    cbrfp = CBRFParser()
    if cbrfp.init_parser():
        for c in cbrfp.get_currencies_list():
            print(c)

def dump_currency(currency_name: str) -> None:
    """
    Выдать дамп имеющихся данных по запрашиваемой валюте из БД в консоль
    """
    for cur in stm.get_currency_timeline_by_name(currency_name):
        print(cur)

if __name__ == "__main__":
    argh.dispatch_commands([scrap_currency, init_db, delete_db, currency_list, dump_currency])