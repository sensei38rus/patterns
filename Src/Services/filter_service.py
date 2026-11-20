from Src.Core.validator import argument_exception, operation_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum

"""
Сервис фильтрации данных по заданному Dto-условию.
Работает с доменными моделями и Dto-структурами
"""
class filter_service:

    """
    Отфильтровать список данных по условию.
    Поддерживаются варианты EQUALS (полное совпадение)
    и LIKE (вхождение строки) для полей name и unique_code
    """
    @staticmethod
    def apply(items: list, condition: filter_dto) -> list:
        if not isinstance(items, list):
            raise argument_exception("Ожидается список доменных сущностей!")
        if not isinstance(condition, filter_dto):
            raise argument_exception("Ожидается условие фильтрации filter_dto!")

        result = []

        for item in items:
            # Поддерживаются и доменные модели, и Dto-структуры
            field_value = getattr(item, condition.field, None)
            if field_value is None or not isinstance(field_value, (str, int)):
                continue

            if filter_service.__match(str(field_value), condition):
                result.append(item)

        return result


    """
    Проверить соответствие строкового значения условию фильтрации
    """
    @staticmethod
    def __match(field_value: str, condition: filter_dto) -> bool:
        if condition.type == filter_type_enum.EQUALS:
            return field_value == condition.value

        if condition.type == filter_type_enum.LIKE:
            return condition.value.lower() in field_value.lower()

        raise operation_exception(f"Неизвестный вариант фильтрации: {condition.type}!")
