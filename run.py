import argh

def init_db() -> None:
    """
    Инициализировать пустую БД (требуется выполнить один раз перед первым использованием скраппинга)
    и в случае, если список валют изменился.
    """
    pass

def scrap_currency(currency_name: str) -> None:
    """
    Запустить скраппинг данных указанной валюты (как на сайте при выборе в ComboBox)
    """
    pass

def delete_db() -> None:
    """
    Удалить файл БД sqlite
    """
    pass

def currency_list() -> None:
    """
    Возвращает список знакомых парсеру валют
    """
    pass

def dump_currency(currency_name: str) -> None:
    """
    Выдать дамп имеющихся данных по запрашиваемой валюте из БД в консоль
    """

if __name__ == "__main__":
    argh.dispatch_commands([scrap_currency, init_db, delete_db, currency_list, dump_currency])