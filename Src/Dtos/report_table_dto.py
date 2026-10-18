from Src.Core.entity_model import entity_model
from Src.Core.validator import validator

"""
Модель нейтрального табличного представления источника данных для отчета
"""
class report_table_dto(entity_model):
    """
    Нейтральное табличное представление сущности для форматирования отчетом любого формата.
    """

    def __init__(self, tag: str = "item", title: str = "", attributes: dict = None,
                 columns: list = None, rows: list = None):
        """
        Конструктор DTO.

        Параметры:
            tag: Имя сущности для XML (корневой тег), например recipe / nomenclature / unit
            title: Наименование сущности
            attributes: Дополнительные атрибуты сущности {ключ: значение}
            columns: Колонки таблицы - список кортежей (ключ, заголовок)
            rows: Данные - список словарей {ключ колонки: значение}
        """
        super().__init__()
        self.tag = tag
        self.title = title
        self.attributes = attributes if attributes is not None else {}
        self.columns = columns if columns is not None else []
        self.rows = rows if rows is not None else []

    @property
    def tag(self) -> str:
        """
        Возвращает имя сущности для XML (корневой тег), например recipe / nomenclature / unit.
        """
        return self.__tag

    @tag.setter
    def tag(self, value: str) -> None:
        """
        Задаёт имя сущности для XML (корневой тег).
        """
        validator.validate(value, str, 255)
        self.__tag = value.strip()

    @property
    def title(self) -> str:
        """
        Возвращает наименование сущности.
        """
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        """
        Задаёт наименование сущности.
        """
        validator.validate(value, str, 255)
        self.__title = value.strip()

    @property
    def attributes(self) -> dict:
        """
        Возвращает дополнительные атрибуты сущности {ключ: значение}.
        """
        return self.__attributes

    @attributes.setter
    def attributes(self, value: dict) -> None:
        """
        Задаёт дополнительные атрибуты сущности {ключ: значение}.
        """
        if value is None:
            raise ValueError("attributes: не может быть None")
        if not isinstance(value, dict):
            raise ValueError("attributes: ожидается словарь {ключ: значение}")
        self.__attributes = value

    @property
    def columns(self) -> list:
        """
        Возвращает колонки таблицы - список кортежей (ключ, заголовок).
        """
        return self.__columns

    @columns.setter
    def columns(self, value: list) -> None:
        """
        Задаёт колонки таблицы - список кортежей (ключ, заголовок).
        """
        if value is None:
            raise ValueError("columns: не может быть None")
        if not isinstance(value, list):
            raise ValueError("columns: ожидается список кортежей (ключ, заголовок)")
        self.__columns = value

    @property
    def rows(self) -> list:
        """
        Возвращает данные таблицы - список словарей {ключ колонки: значение}.
        """
        return self.__rows

    @rows.setter
    def rows(self, value: list) -> None:
        """
        Задаёт данные таблицы - список словарей {ключ колонки: значение}.
        """
        if value is None:
            raise ValueError("rows: не может быть None")
        if not isinstance(value, list):
            raise ValueError("rows: ожидается список словарей {ключ колонки: значение}")
        self.__rows = value

    @property
    def keys(self) -> list:
        """
        Возвращает ключи колонок в порядке вывода.
        """
        return [key for key, title in self.columns]


ReportTableDto = report_table_dto
