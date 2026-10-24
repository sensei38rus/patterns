import datetime

import pytest

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory, ConvertFactory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.range_model import range_model


"""
Набор модульных тестов для класса convert_factory
"""


class document_model(abs_mod):
    """
    Вспомогательная тестовая модель документа со ссылкой,
    списком ссылок, датой и примитивными полями.
    """

    def __init__(self, base_range=None, ranges=None):
        super().__init__()
        self.name = "Документ"
        self.__line_count = 3
        self.__created_at = datetime.datetime(2026, 10, 24, 12, 30, 0)
        self.__tags = ["срочно", "гарячее"]
        self.__base_range = base_range
        self.__ranges = list(ranges) if ranges else []

    @property
    def line_count(self):
        return self.__line_count

    @property
    def created_at(self):
        return self.__created_at

    @property
    def tags(self):
        return self.__tags

    @property
    def base_range(self):
        return self.__base_range

    @property
    def ranges(self):
        return self.__ranges


class broken_model(abs_mod):
    """
    Вспомогательная тестовая модель с некорректным свойством.
    """

    @property
    def payload(self):
        raise RuntimeError("сбой чтения свойства")


@pytest.mark.parametrize("value, expected", [(-7, {"int": -7}), (0, {"int": 0}), (42, {"int": 42})])
def test_success_convert_factory_convert_integer_value(value, expected):
    """
    Ожидание: Набор из одного словаря для целого числа.
    Метод: convert_factory.convert
    Описание: Целочисленный источник конвертируется базовым конвертером
              в словарь вида {имя_типа: значение}.
    """
    # Arrange
    factory = convert_factory()

    # Act
    result = factory.convert(value)

    # Assert
    assert result == [expected]


@pytest.mark.parametrize("value, expected", [(-7.5, {"float": -7.5}), (3.14, {"float": 3.14})])
def test_success_convert_factory_convert_float_value(value, expected):
    """
    Ожидание: Набор из одного словаря для вещественного числа.
    Метод: convert_factory.convert
    Описание: Вещественный источник конвертируется базовым конвертером.
    """
    # Arrange
    factory = convert_factory()

    # Act
    result = factory.convert(value)

    # Assert
    assert result == [expected]


def test_success_convert_factory_convert_str_value():
    """
    Ожидание: Набор из одного словаря для строки.
    Метод: convert_factory.convert
    Описание: Строковый источник конвертируется базовым конвертером.
    """
    # Arrange
    factory = convert_factory()

    # Act
    result = factory.convert("грамм")

    # Assert
    assert result == [{"str": "грамм"}]


def test_success_convert_factory_convert_datetime_value():
    """
    Ожидание: Набор из одного словаря для даты и времени.
    Метод: convert_factory.convert
    Описание: Источник типа datetime конвертируется конвертером даты и времени.
    """
    # Arrange
    factory = convert_factory()
    value = datetime.datetime(2026, 10, 24, 12, 30, 15)

    # Act
    result = factory.convert(value)

    # Assert
    assert result == [{"datetime": value}]


def test_success_convert_factory_convert_list_of_values():
    """
    Ожидание: Набор словарей для каждого элемента списка.
    Метод: convert_factory.convert
    Описание: Список примитивов и дат конвертируется поэлементно,
              порядок элементов сохраняется.
    """
    # Arrange
    factory = convert_factory()
    moment = datetime.datetime(2026, 10, 24, 12, 0, 0)

    # Act
    result = factory.convert([1, "два", moment, 4.0])

    # Assert
    assert result == [
        {"int": 1},
        {"str": "два"},
        {"datetime": moment},
        {"float": 4.0},
    ]


def test_success_convert_factory_convert_model_fields():
    """
    Ожидание: Набор из одного словаря с полями модели без вложенных ссылок.
    Метод: convert_factory.convert
    Описание: Все property-поля модели попадают в словарь; примитивные
              значения конвертируются базовым конвертером, ссылка base_range
              у базовой единицы остаётся пустой (None).
    """
    # Arrange
    factory = convert_factory()
    model = range_model("грамм", 1)

    # Act
    result = factory.convert(model)

    # Assert
    assert len(result) == 1
    assert result[0]["name"] == {"str": "грамм"}
    assert result[0]["conversion_factor"] == {"int": 1}
    assert result[0]["coefficient"] == {"int": 1}
    assert result[0]["value"] == {"int": 1}
    assert result[0]["id"] == {"str": model.id}
    assert result[0]["unique_code"] == {"str": model.id}
    assert result[0]["base_range"] is None
    assert result[0]["base"] is None


def test_success_convert_factory_convert_nested_reference():
    """
    Ожидание: Словарь родителя и отдельный словарь вложенной модели.
    Метод: convert_factory.convert
    Описание: Ссылочное поле заменяется идентификатором в словаре родителя,
              а сама вложенная модель добавляется отдельным словарём после
              словаря родителя.
    """
    # Arrange
    factory = convert_factory()
    model = range_model.create_kilogram()

    # Act
    result = factory.convert(model)

    # Assert
    assert len(result) == 2

    parent = result[0]
    child = result[1]
    assert parent["base_range"] == model.base_range.id
    assert parent["base"] == model.base_range.id
    assert parent["name"] == {"str": "килограмм"}
    assert parent["conversion_factor"] == {"int": 1000}

    assert child["name"] == {"str": "грамм"}
    assert child["conversion_factor"] == {"int": 1}
    assert child["base_range"] is None
    assert child["base"] is None


def test_success_convert_factory_convert_document_structure():
    """
    Ожидание: Набор словарей, повторяющих исходную структуру документа.
    Метод: convert_factory.convert
    Описание: Словарь документа содержит поля с конвертированными значениями
              (дата, примитивы, теги) и идентификаторы ссылок; каждая модель
              из списка ссылок добавляется отдельным словарём в порядке списка.
    """
    # Arrange
    factory = convert_factory()
    first = range_model("грамм", 1)
    second = range_model("килограмм", 1000)
    document = document_model(ranges=[first, second])

    # Act
    result = factory.convert(document)

    # Assert
    assert len(result) == 3

    document_fields = result[0]
    assert document_fields["name"] == {"str": "Документ"}
    assert document_fields["line_count"] == {"int": 3}
    assert document_fields["created_at"] == {"datetime": datetime.datetime(2026, 10, 24, 12, 30, 0)}
    assert document_fields["tags"] == [{"str": "срочно"}, {"str": "гарячее"}]
    assert document_fields["base_range"] is None
    assert document_fields["ranges"] == [first.id, second.id]

    assert result[1]["name"] == {"str": "грамм"}
    assert result[2]["name"] == {"str": "килограмм"}


def test_success_convert_factory_convert_cyclic_reference():
    """
    Ожидание: Конечный набор словарей при циклической ссылке между моделями.
    Метод: convert_factory.convert
    Описание: Модели с взаимными ссылками конвертируются без зацикливания -
              каждая модель попадает в набор ровно один раз.
    """
    # Arrange
    factory = convert_factory()
    first = range_model("первый", 1)
    second = range_model("второй", 2)
    first.base = second
    second.base = first

    # Act
    result = factory.convert(first)

    # Assert
    assert len(result) == 2
    assert result[0]["base_range"] == second.id
    assert result[1]["base_range"] == first.id


def test_success_convert_factory_convert_dict_source():
    """
    Ожидание: Словарь источника конвертируется в словарь полей и словари вложенных моделей.
    Метод: convert_factory.convert
    Описание: Значения словаря конвертируются соответствующими конвертерами,
              модель становится идентификатором плюс отдельным словарём.
    """
    # Arrange
    factory = convert_factory()
    model = range_model("грамм", 1)
    moment = datetime.datetime(2026, 10, 24, 12, 0, 0)
    source = {"count": 5, "title": "сырники", "moment": moment, "range": model}

    # Act
    result = factory.convert(source)

    # Assert
    assert len(result) == 2
    assert result[0] == {
        "count": {"int": 5},
        "title": {"str": "сырники"},
        "moment": {"datetime": moment},
        "range": model.id,
    }
    assert result[1]["name"] == {"str": "грамм"}


def test_error_convert_factory_convert_none():
    """
    Ожидание: Выброс argument_exception при передаче None.
    Метод: convert_factory.convert
    Описание: Источник None не поддерживается фабрикой.
    """
    # Arrange
    factory = convert_factory()

    # Act & Assert
    with pytest.raises(argument_exception):
        factory.convert(None)


def test_error_convert_factory_convert_unsupported_type():
    """
    Ожидание: Выброс argument_exception при передаче неподдерживаемого типа.
    Метод: convert_factory.convert
    Описание: Объект типа object не подходит ни под один конвертер фабрики.
    """
    # Arrange
    factory = convert_factory()

    # Act & Assert
    with pytest.raises(argument_exception):
        factory.convert(object())


def test_error_convert_factory_convert_broken_property():
    """
    Ожидание: Выброс argument_exception при некорректном свойстве модели.
    Метод: convert_factory.convert
    Описание: Ошибка чтения property модели преобразуется в argument_exception.
    """
    # Arrange
    factory = convert_factory()

    # Act & Assert
    with pytest.raises(argument_exception):
        factory.convert(broken_model())


def test_success_convert_factory_convertors_property():
    """
    Ожидание: Фабрика предоставляет три конвертера.
    Метод: convert_factory.convertors
    Описание: В набор входят basic_convertor, datetime_convertor и reference_convertor.
    """
    # Arrange
    factory = convert_factory()

    # Act
    convertors = factory.convertors

    # Assert
    assert len(convertors) == 3
    assert isinstance(convertors[0], basic_convertor)
    assert isinstance(convertors[1], datetime_convertor)
    assert isinstance(convertors[2], reference_convertor)


def test_success_convert_factory_is_convertor_user():
    """
    Ожидание: Фабрика использует только подклассы abstract_convertor.
    Метод: convert_factory.convertors
    Описание: Все конвертеры фабрики наследуются от абстрактного конвертера.
    """
    # Arrange
    factory = convert_factory()

    # Act & Assert
    for convertor in factory.convertors:
        assert isinstance(convertor, abstract_convertor)


def test_success_convert_factory_alias_available():
    """
    Ожидание: Алиас ConvertFactory указывает на convert_factory.
    Метод: convert_factory (алиас ConvertFactory)
    Описание: ПascalCase-имя класса сохранено для совместимости.
    """
    # Arrange, Act & Assert
    assert ConvertFactory is convert_factory
