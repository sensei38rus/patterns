from datetime import datetime
from Src.Core.validator import argument_exception
from Src.Dtos.log_category_enum import log_category_enum

"""
Dto события журнала операций.

Событие содержит основную категорию операции (category) и полный набор
категорий, к которым оно относится (groups). Например, создание склада -
это одновременно складская операция (WAREHOUSE) и CRUD операция (CRUD),
поэтому для нее category = WAREHOUSE, groups = [WAREHOUSE, CRUD].
Наблюдатели отбирают события по любому из значений groups
"""
class log_event_dto:
    # Время регистрации события
    __timestamp: datetime = None
    # Основная категория операции
    __category: log_category_enum = None
    # Все категории, к которым относится событие
    __groups: list = None
    # Наименование операции (create, update, delete, filter, osv, ...)
    __operation: str = ""
    # Ключ доменной сущности
    __entity: str = ""
    # Уникальный код сущности
    __unique_code: str = ""
    # Человекочитаемое сообщение
    __message: str = ""
    # Статус выполнения (success | error)
    __status: str = "success"
    # Дополнительные детали операции
    __details: dict = None

    """
    Конструктор
    Args:
        category (log_category_enum): Основная категория операции
        operation (str): Наименование операции
    """
    def __init__(self, category: log_category_enum = log_category_enum.CRUD, operation: str = ""):
        if not isinstance(category, log_category_enum):
            raise argument_exception("Ожидается категория операции (log_category_enum)!")

        self.__timestamp = datetime.now()
        self.__category = category
        self.__groups = [category]
        self.__operation = str(operation)
        self.__entity = ""
        self.__unique_code = ""
        self.__message = ""
        self.__status = "success"
        self.__details = {}

    """
    Время регистрации события
    """
    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    """
    Основная категория операции
    """
    @property
    def category(self) -> log_category_enum:
        return self.__category

    """
    Все категории, к которым относится событие
    """
    @property
    def groups(self) -> list:
        return list(self.__groups)

    """
    Наименование операции
    """
    @property
    def operation(self) -> str:
        return self.__operation

    """
    Ключ доменной сущности
    """
    @property
    def entity(self) -> str:
        return self.__entity

    """
    Уникальный код сущности
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    """
    Сообщение события
    """
    @property
    def message(self) -> str:
        return self.__message

    """
    Статус выполнения операции
    """
    @property
    def status(self) -> str:
        return self.__status

    """
    Дополнительные детали операции
    """
    @property
    def details(self) -> dict:
        return dict(self.__details)

    """
    Ключ доменной сущности
    """
    @entity.setter
    def entity(self, value: str) -> None:
        self.__entity = "" if value is None else str(value)

    """
    Уникальный код сущности
    """
    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = "" if value is None else str(value)

    """
    Сообщение события
    """
    @message.setter
    def message(self, value: str) -> None:
        self.__message = "" if value is None else str(value)

    """
    Статус выполнения операции (success | error)
    """
    @status.setter
    def status(self, value: str) -> None:
        self.__status = "error" if str(value).strip().lower() == "error" else "success"

    """
    Добавить категорию в набор категорий события
    """
    def add_group(self, category: log_category_enum) -> None:
        if not isinstance(category, log_category_enum):
            raise argument_exception("Ожидается категория операции (log_category_enum)!")

        if category not in self.__groups:
            self.__groups.append(category)

    """
    Дополнительные детали операции
    """
    def add_detail(self, key: str, value) -> None:
        if key is None or str(key).strip() == "":
            raise argument_exception("Не указан ключ детали события!")

        self.__details[ str(key) ] = value

    """
    Проверить, относится ли событие к указанной категории
    """
    def belongs_to(self, category) -> bool:
        if isinstance(category, str):
            try:
                category = log_category_enum(category.strip().upper())
            except ValueError:
                return False
        if not isinstance(category, log_category_enum):
            return False

        return category in self.__groups

    """
    Преобразовать событие в словарь для сериализации в Json
    """
    def to_dict(self) -> dict:
        return {
            "timestamp": self.__timestamp.isoformat(sep=" "),
            "category": self.__category.value,
            "groups": [item.value for item in self.__groups],
            "operation": self.__operation,
            "entity": self.__entity,
            "unique_code": self.__unique_code,
            "message": self.__message,
            "status": self.__status,
            "details": dict(self.__details)
        }
