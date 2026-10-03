import pytest
from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception


class test_entity(abs_mod):
    """
    Тестовая сущность, наследующая базовый класс abs_mod для проверки его функциональности.
    """
    pass


def test_not_none_model_get_id_not_null():
    """
    Ожидание: Идентификатор id не равен None при создании сущности.
    Метод: abs_mod.id (getter)
    Описание: Проверяет, что при инициализации объекта свойство id автоматически заполняется и не равно None.
    """
    # Arrange (Подготовка)
    entity = test_entity()

    # Act (Действие)
    result = entity.id

    # Assert (Проверка)
    assert result is not None


def test_not_equal_model_id_different_instances():
    """
    Ожидание: Идентификаторы двух разных сущностей не равны.
    Метод: abs_mod.id (getter)
    Описание: Проверяет уникальность автоматически сгенерированных идентификаторов для разных экземпляров сущности.
 
    """
    # Arrange (Подготовка)
    entity1 = test_entity()
    entity2 = test_entity()

    # Act & Assert (Действие и Проверка)
    assert entity1.id != entity2.id


def test_equal_model_compare_by_same_id():
    """
    Ожидание: Две сущности равны при совпадении их идентификаторов id.
    Метод: abs_mod.__eq__
    Описание: Проверяет сравнение сущностей: если их id совпадают, оператор равенства возвращает True,
              даже если это разные объекты в памяти.
    """
    # Arrange (Подготовка)
    entity1 = test_entity()
    entity2 = test_entity()

    # Act (Действие)
    entity1.id = "133"
    entity2.id = "133"

    # Assert (Проверка)
    assert entity1.id == entity2.id
    assert entity1 == entity2
    assert entity1 is not entity2
    assert id(entity1) != id(entity2)


def test_argument_exception_model_set_name_empty_value():
    """
    Ожидание: Выброс пользовательского исключения argument_exception при пустом имени.
    Метод: abs_mod.name (setter)
    Описание: Проверяет, что сеттер свойства name выбрасывает именно argument_exception,
              а также проверяет заполненность полей field и message в объекте исключения.
    """
    # Arrange (Подготовка)
    entity = test_entity()

    # Act & Assert (Действие и Проверка перехвата)
    with pytest.raises(argument_exception) as exc_info:
        entity.name = ""


def test_argument_exception_model_set_name_none_value():
    """
    Ожидание: Выброс пользовательского исключения argument_exception при значении None.
    Метод: abs_mod.name (setter)
    Описание: Проверяет выброс argument_exception при передаче None в сеттер name.
    """
    # Arrange (Подготовка)
    entity = test_entity()

    # Act & Assert (Действие и Проверка перехвата)
    with pytest.raises(argument_exception) as exc_info:
        entity.name = None