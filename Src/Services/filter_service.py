from Src.Core.validator import argument_exception, operation_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum

"""
Сервис фильтрации данных по заданному Dto-условию.
Работает с доменными моделями и Dto-структурами.
Поддерживается поиск по полям сущности и по вложенным
структурам (base, group, parent, range) через путь field
"""
class filter_service:

    """
    Отфильтровать список данных по условию.
    Поддерживаются варианты EQUALS (полное совпадение)
    и LIKE (вхождение строки) для полей name и unique_code,
    а также их вложенных представлений (например base.name)
    """
    @staticmethod
    def apply(items: list, condition: filter_dto) -> list:
        if not isinstance(items, list):
            raise argument_exception("Ожидается список доменных сущностей!")
        if not isinstance(condition, filter_dto):
            raise argument_exception("Ожидается условие фильтрации filter_dto!")

        result = []

        for item in items:
            field_value = filter_service.__resolve(item, condition.field)
            if field_value is None or not isinstance(field_value, (str, int)):
                continue

            if filter_service.__match(str(field_value), condition):
                result.append(item)

        return result


    """
    Получить значение поля по пути (в том числе вложенному).
    Возвращает None, если путь не разрешается
    """
    @staticmethod
    def __resolve(item, path: str):
        if item is None or not isinstance(path, str) or path.strip() == "":
            return None

        current = item
        for part in path.split("."):
            if current is None:
                return None

            # Коллекции (состав рецепта) не обходятся по пути фильтрации
            if isinstance(current, (list, tuple, dict)):
                return None

            current = getattr(current, part, None)

        return current


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
