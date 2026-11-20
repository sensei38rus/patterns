from Src.Core.validator import validator, argument_exception
from Src.Dtos.filter_type_enum import filter_type_enum

"""
Dto для фильтрации данных по доменным сущностям:
номенклатура, группа, единица измерения, рецепт
"""
class filter_dto:
    # Ключ доменной сущности (коллекции хранилища)
    __entity: str = ""

    # Поле для сравнения
    __field: str = ""

    # Значение для сравнения
    __value: str = ""

    # Вариант сравнения
    __type: filter_type_enum = filter_type_enum.EQUALS

    # Допустимые ключи доменных сущностей фильтрации
    __allowed_entities: set = {
        "nomenclature_model",
        "group_model",
        "range_model",
        "receipt_model",
    }

    # Допустимые поля для сравнения
    __allowed_fields: set = {
        "name",
        "unique_code",
    }

    """
    Ключ доменной сущности
    """
    @property
    def entity(self) -> str:
        return self.__entity

    @entity.setter
    def entity(self, value: str) -> None:
        validator.validate(value, str)

        entity = value.strip()
        if entity not in filter_dto.__allowed_entities:
            raise argument_exception(
                f"Недопустимая доменная сущность для фильтрации: {entity}!"
            )

        self.__entity = entity

    """
    Поле для сравнения (наименование или уникальный код)
    """
    @property
    def field(self) -> str:
        return self.__field

    @field.setter
    def field(self, value: str) -> None:
        validator.validate(value, str)

        field = value.strip()
        if field not in filter_dto.__allowed_fields:
            raise argument_exception(
                f"Недопустимое поле для фильтрации: {field}!"
            )

        self.__field = field

    """
    Значение для сравнения
    """
    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        validator.validate(value, str)
        self.__value = value.strip()

    """
    Вариант сравнения
    """
    @property
    def type(self) -> filter_type_enum:
        return self.__type

    @type.setter
    def type(self, value: filter_type_enum) -> None:
        validator.validate(value, filter_type_enum)
        self.__type = value
