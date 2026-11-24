from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Services.filter_service import filter_service

"""
Прототип фильтрации данных.
Один прототип используется для всех DOMAIN-моделей и их Dto:
номенклатура, группа, единица измерения, рецепт.
Условие хранится в filter_dto; копия создается методом clone()
"""
class filter_prototype(abstract_prototype):
    # Условие фильтрации
    __condition: filter_dto = None

    """
    Конструктор.
    При отсутствии условия создается пустой filter_dto
    """
    def __init__(self, condition: filter_dto = None) -> None:
        if condition is not None and not isinstance(condition, filter_dto):
            raise argument_exception("Ожидается условие фильтрации filter_dto!")

        self.__condition = condition.clone() if condition is not None else filter_dto()

    """
    Условие фильтрации
    """
    @property
    def condition(self) -> filter_dto:
        return self.__condition

    @condition.setter
    def condition(self, value: filter_dto) -> None:
        if not isinstance(value, filter_dto):
            raise argument_exception("Ожидается условие фильтрации filter_dto!")

        self.__condition = value.clone()

    """
    Задать условие фильтрации по полям.
    Возвращает текущий прототип для построения цепочки вызовов
    """
    def configure(
        self,
        entity: str,
        field: str,
        value: str,
        type: filter_type_enum = filter_type_enum.EQUALS,
    ) -> "filter_prototype":
        self.__condition.entity = entity
        self.__condition.field = field
        self.__condition.value = value
        self.__condition.type = type
        return self

    """
    Отфильтровать список (доменные модели или Dto) по условию прототипа
    """
    def apply(self, items: list) -> list:
        if not isinstance(items, list):
            raise argument_exception("Ожидается список данных для фильтрации!")

        return filter_service.apply(items, self.__condition)

    """
    Создать независимую копию прототипа.
    Условие копируется глубоко: изменения копии не влияют на оригинал
    """
    def clone(self) -> "filter_prototype":
        return filter_prototype(self.__condition)
