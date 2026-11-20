from Src.Core.validator import validator, argument_exception
from Src.Dtos.filter_type_enum import filter_type_enum

"""
Dto для фильтрации данных по доменным сущностям:
номенклатура, группа, единица измерения, рецепт.
Поддерживается поиск по полям самой сущности и по вложенным
структурам: base (базовая единица), group (группа),
parent (группа-владелец), range (единица измерения)
"""
class filter_dto:
    # Ключ доменной сущности (коллекции хранилища)
    __entity: str = ""

    # Поле для сравнения (допускается путь вида base.name)
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

    # Листовые поля для сравнения
    __allowed_leaf_fields: set = {
        "name",
        "unique_code",
    }

    # Ссылочные (вложенные) свойства моделей
    __allowed_link_fields: set = {
        "base",
        "group",
        "parent",
        "range",
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
    Поле для сравнения: name, unique_code либо путь
    вложенной структуры (base.name, group.unique_code, parent.name)
    """
    @property
    def field(self) -> str:
        return self.__field

    @field.setter
    def field(self, value: str) -> None:
        validator.validate(value, str)

        field = value.strip()
        filter_dto.__validate_field_path(field)
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
        if isinstance(value, str):
            value = filter_dto.__parse_type(value)
        elif isinstance(value, int) and not isinstance(value, bool):
            try:
                value = filter_type_enum(value)
            except ValueError:
                raise argument_exception(f"Недопустимый вариант фильтрации: {value}!")

        validator.validate(value, filter_type_enum)
        self.__type = value

    """
    Создать Dto из словаря (тела REST-запроса)
    """
    @staticmethod
    def from_dict(source: dict) -> "filter_dto":
        if not isinstance(source, dict):
            raise argument_exception("Ожидается словарь условия фильтрации!")

        dto = filter_dto()

        if source.get("entity"):
            dto.entity = source["entity"]
        if source.get("field") is not None:
            dto.field = source["field"]
        if source.get("value") is not None:
            dto.value = source["value"]
        if source.get("type") is not None:
            dto.type = source["type"]

        return dto

    """
    Создать независимую копию условия фильтрации
    """
    def clone(self) -> "filter_dto":
        dto = filter_dto()
        dto.__entity = self.__entity
        dto.__field = self.__field
        dto.__value = self.__value
        dto.__type = self.__type
        return dto

    """
    Проверить путь поля: лист или цепочка вложенных ссылок
    """
    @staticmethod
    def __validate_field_path(field: str) -> None:
        parts = field.split(".")

        if len(parts) < 1 or any(part.strip() == "" for part in parts):
            raise argument_exception(f"Некорректное поле для фильтрации: {field}!")

        for part in parts[:-1]:
            if part not in filter_dto.__allowed_link_fields:
                raise argument_exception(
                    f"Недопустимое вложенное поле для фильтрации: {part}!"
                )

        leaf = parts[-1]
        if leaf not in filter_dto.__allowed_leaf_fields:
            raise argument_exception(
                f"Недопустимое поле для фильтрации: {leaf}!"
            )

    """
    Разобрать вариант сравнения из строки или кода
    """
    @staticmethod
    def __parse_type(value: str) -> filter_type_enum:
        text = value.strip().upper()

        for item in filter_type_enum:
            if text == item.name or text == str(item.value):
                return item

        raise argument_exception(f"Недопустимый вариант фильтрации: {value}!")
