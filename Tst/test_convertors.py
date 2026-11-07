import datetime

import pytest

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.range_model import range_model


"""
Набор модульных тестов для конвертеров типов
"""


def test_error_abstract_convertor_create_instance():
    """
    Ожидание: Нельзя создать экземпляр абстрактного конвертера.
    Метод: abstract_convertor.__init__
    Описание: Абстрактный класс содержит абстрактный метод Convert,
              поэтому его инстанцирование завершается исключением TypeError.
    """
    # Arrange, Act & Assert
    with pytest.raises(TypeError):
        abstract_convertor()


def test_success_convertors_are_abstract_convertor():
    """
    Ожидание: Все конкретные конвертеры наследуются от abstract_convertor.
    Метод: isinstance
    Описание: basic_convertor, datetime_convertor и reference_convertor
              являются подклассами абстрактного конвертера.
    """
    # Arrange
    converters = [basic_convertor(), datetime_convertor(), reference_convertor()]

    # Act & Assert
    for converter in converters:
        assert isinstance(converter, abstract_convertor)


@pytest.mark.parametrize("value", [-7, 0, 42])
def test_success_basic_convertor_convertable_integer_value(value):
    """
    Ожидание: Целочисленное значение распознаётся как конвертируемое.
    Метод: basic_convertor.convertable
    Описание: Экземпляры типа int должны поддерживаться базовым конвертером.
    """
    # Arrange
    convertor = basic_convertor()

    # Act & Assert
    assert convertor.convertable(value) is True


@pytest.mark.parametrize("value", [-7.5, 0.0, 3.14])
def test_success_basic_convertor_convertable_float_value(value):
    """
    Ожидание: Вещественное значение распознаётся как конвертируемое.
    Метод: basic_convertor.convertable
    Описание: Экземпляры типа float должны поддерживаться базовым конвертером.
    """
    # Arrange
    convertor = basic_convertor()

    # Act & Assert
    assert convertor.convertable(value) is True


@pytest.mark.parametrize("value", ["", "грамм", "123"])
def test_success_basic_convertor_convertable_str_value(value):
    """
    Ожидание: Строковое значение распознаётся как конвертируемое.
    Метод: basic_convertor.convertable
    Описание: Экземпляры типа str должны поддерживаться базовым конвертером.
    """
    # Arrange
    convertor = basic_convertor()

    # Act & Assert
    assert convertor.convertable(value) is True


@pytest.mark.parametrize("value", [None, datetime.datetime.now(), range_model.create_gram()])
def test_success_basic_convertor_not_convertable_foreign_values(value):
    """
    Ожидание: Чужеродные типы не распознаются базовым конвертером.
    Метод: basic_convertor.convertable
    Описание: None, datetime и модели не должны попадать в область
              действия базового конвертера.
    """
    # Arrange
    convertor = basic_convertor()

    # Act & Assert
    assert convertor.convertable(value) is False


@pytest.mark.parametrize("value", [-7, 0, 42])
def test_success_basic_convertor_convert_integer_value(value):
    """
    Ожидание: Целое число конвертируется в плоское значение без обёртки.
    Метод: basic_convertor.Convert
    Описание: Источник возвращается как есть — значение без словаря
              вида {имя_типа: значение}.
    """
    # Arrange
    convertor = basic_convertor()

    # Act
    result = convertor.Convert(value)

    # Assert
    assert result == value


@pytest.mark.parametrize("value", [-7.5, 0.0, 3.14])
def test_success_basic_convertor_convert_float_value(value):
    """
    Ожидание: Вещественное число конвертируется в плоское значение без обёртки.
    Метод: basic_convertor.Convert
    Описание: Источник возвращается как есть — значение без словаря
              вида {имя_типа: значение}.
    """
    # Arrange
    convertor = basic_convertor()

    # Act
    result = convertor.Convert(value)

    # Assert
    assert result == value


@pytest.mark.parametrize("value", ["", "грамм", "сырники"])
def test_success_basic_convertor_convert_str_value(value):
    """
    Ожидание: Строка конвертируется в плоское значение без обёртки.
    Метод: basic_convertor.Convert
    Описание: Источник возвращается как есть — значение без словаря
              вида {имя_типа: значение}.
    """
    # Arrange
    convertor = basic_convertor()

    # Act
    result = convertor.Convert(value)

    # Assert
    assert result == value


def test_error_basic_convertor_convert_none_value():
    """
    Ожидание: Выброс argument_exception при передаче None.
    Метод: basic_convertor.Convert
    Описание: Значение None не поддерживается базовым конвертером.
    """
    # Arrange
    convertor = basic_convertor()

    # Act & Assert
    with pytest.raises(argument_exception):
        convertor.Convert(None)


def test_error_basic_convertor_convert_model_value():
    """
    Ожидание: Выброс argument_exception при передаче модели.
    Метод: basic_convertor.Convert
    Описание: Модель не является примитивным типом и не поддерживается.
    """
    # Arrange
    convertor = basic_convertor()
    model = range_model.create_gram()

    # Act & Assert
    with pytest.raises(argument_exception):
        convertor.Convert(model)


def test_error_basic_convertor_convert_datetime_value():
    """
    Ожидание: Выброс argument_exception при передаче datetime.
    Метод: basic_convertor.Convert
    Описание: Дата и время обрабатываются отдельным конвертером.
    """
    # Arrange
    convertor = basic_convertor()
    value = datetime.datetime(2026, 10, 24, 12, 0, 0)

    # Act & Assert
    with pytest.raises(argument_exception):
        convertor.Convert(value)


def test_success_datetime_convertor_convertable_datetime_value():
    """
    Ожидание: Значение datetime распознаётся как конвертируемое.
    Метод: datetime_convertor.convertable
    Описание: Экземпляры datetime.datetime должны поддерживаться конвертером.
    """
    # Arrange
    convertor = datetime_convertor()
    value = datetime.datetime(2026, 10, 24, 12, 0, 0)

    # Act & Assert
    assert convertor.convertable(value) is True


def test_success_datetime_convertor_not_convertable_date_value():
    """
    Ожидание: Значение date не распознаётся как конвертируемое.
    Метод: datetime_convertor.convertable
    Описание: datetime.date не является подклассом datetime.datetime.
    """
    # Arrange
    convertor = datetime_convertor()
    value = datetime.date(2026, 10, 24)

    # Act & Assert
    assert convertor.convertable(value) is False


def test_success_datetime_convertor_convert_datetime_value():
    """
    Ожидание: Значение datetime конвертируется в плоское значение без обёртки.
    Метод: datetime_convertor.Convert
    Описание: Источник возвращается как есть — значение без словаря
              вида {имя_типа: значение}.
    """
    # Arrange
    convertor = datetime_convertor()
    value = datetime.datetime(2026, 10, 24, 12, 30, 15)

    # Act
    result = convertor.Convert(value)

    # Assert
    assert result == value


def test_error_datetime_convertor_convert_date_value():
    """
    Ожидание: Выброс argument_exception при передаче date.
    Метод: datetime_convertor.Convert
    Описание: Только datetime.datetime поддерживается конвертером.
    """
    # Arrange
    convertor = datetime_convertor()
    value = datetime.date(2026, 10, 24)

    # Act & Assert
    with pytest.raises(argument_exception):
        convertor.Convert(value)


def test_error_datetime_convertor_convert_none_value():
    """
    Ожидание: Выброс argument_exception при передаче None.
    Метод: datetime_convertor.Convert
    Описание: Значение None не поддерживается конвертером даты и времени.
    """
    # Arrange
    convertor = datetime_convertor()

    # Act & Assert
    with pytest.raises(argument_exception):
        convertor.Convert(None)


def test_error_datetime_convertor_convert_str_value():
    """
    Ожидание: Выброс argument_exception при передаче строки.
    Метод: datetime_convertor.Convert
    Описание: Строка, даже в формате даты, не поддерживается конвертером.
    """
    # Arrange
    convertor = datetime_convertor()

    # Act & Assert
    with pytest.raises(argument_exception):
        convertor.Convert("2026-10-24T12:00:00")


def test_success_reference_convertor_convertable_model_value():
    """
    Ожидание: Модель распознаётся как конвертируемая.
    Метод: reference_convertor.convertable
    Описание: Экземпляры abs_mod (и их производные) поддерживаются конвертером.
    """
    # Arrange
    convertor = reference_convertor()
    model = range_model.create_gram()

    # Act & Assert
    assert convertor.convertable(model) is True


def test_success_reference_convertor_not_convertable_foreign_values():
    """
    Ожидание: Чужеродные типы не распознаются конвертером ссылок.
    Метод: reference_convertor.convertable
    Описание: Примитивы, None и datetime не являются моделями.
    """
    # Arrange
    convertor = reference_convertor()
    values = [None, 42, 3.14, "грамм", datetime.datetime.now()]

    # Act & Assert
    for value in values:
        assert convertor.convertable(value) is False


def test_success_reference_convertor_convert_model_fields():
    """
    Ожидание: Словарь публичных свойств модели.
    Метод: reference_convertor.Convert
    Описание: Все property-поля модели попадают в результирующий словарь.
    """
    # Arrange
    convertor = reference_convertor()
    model = range_model("грамм", 1)

    # Act
    result = convertor.Convert(model)

    # Assert
    assert isinstance(result, dict)
    assert result["name"] == "грамм"
    assert result["conversion_factor"] == 1
    assert result["id"] == model.id
    assert result["unique_code"] == model.id


def test_success_reference_convertor_convert_nested_reference():
    """
    Ожидание: Ссылочное свойство модели заменяется его идентификатором.
    Метод: reference_convertor.Convert
    Описание: Значение свойства, являющееся экземпляром abs_mod,
              заменяется на его идентификатор (id).
    """
    # Arrange
    convertor = reference_convertor()
    model = range_model.create_kilogram(name="килограмм", base_name="грамм")

    # Act
    result = convertor.Convert(model)

    # Assert
    assert result["base_range"] == model.base_range.id
    assert result["base"] == model.base_range.id


def test_success_reference_convertor_alias_available():
    """
    Ожидание: Алиас ReferenceConvertor указывает на reference_convertor.
    Метод: reference_convertor (алиас ReferenceConvertor)
    Описание: Старое имя класса сохранено для совместимости.
    """
    # Arrange
    from Src.Logics.reference_convertor import ReferenceConvertor

    # Act
    convertor = ReferenceConvertor()

    # Assert
    assert isinstance(convertor, reference_convertor)
