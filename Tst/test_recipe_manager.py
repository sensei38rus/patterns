import pytest
from Src.Logics.recipe_manager import recipe_manager
from Src.Models.recipe_model import recipe_model


"""
Набор модульных тестов для класса recipe_manager
"""


def _create_recipe(name: str = "Сырники из творога") -> recipe_model:
    """
    Вспомогательный метод - минимально корректная технологическая карта.
    """
    return recipe_model(name=name, cooking_time=30, portions=2, pieces=6)


def test_same_instance_recipe_manager_singleton():
    """
    Ожидание: Два вызова возвращают один и тот же объект в памяти.
    Метод: recipe_manager.__new__
    Описание: Проверяет оператор is — оба инстанса ссылаются на один объект.
    """
    # Подготовка
    m1 = recipe_manager()
    m2 = recipe_manager()

    # Проверки
    assert m1 is m2


def test_shared_data_recipe_manager_singleton():
    """
    Ожидание: Данные в двух инстансах синглтона общие.
    Метод: recipe_manager.__new__
    Описание: Тест с пары — коллекция recipes ссылается на один и тот же словарь.
    """
    # Подготовка
    m1 = recipe_manager()
    m2 = recipe_manager()

    # Проверки
    assert m1.recipes is m2.recipes


def test_true_recipe_manager_convert():
    """
    Ожидание: convert() возвращает True.
    Метод: recipe_manager.build
    Описание: Хранилище рецептов не имеет файлового источника и всегда готово к работе.
    """
    # Подготовка
    manager = recipe_manager()

    # Действие
    result = manager.convert()

    # Проверки
    assert result == True


def test_true_recipe_manager_is_loaded_after_convert():
    """
    Ожидание: is_loaded равен True после convert().
    Метод: recipe_manager.build (переопределение abstract_manager)
    Описание: Контракт базового класса abstract_manager: после успешной конвертации
              свойство is_loaded возвращает True.
    """
    # Подготовка
    manager = recipe_manager()

    # Действие
    manager.convert()

    # Проверки
    assert manager.is_loaded == True


def test_true_recipe_manager_add_recipe():
    """
    Ожидание: Новая технологическая карта успешно добавляется (True).
    Метод: recipe_manager.add_recipe
    Описание: Добавление карты с уникальным id увеличивает размер коллекции.
    """
    # Подготовка
    manager = recipe_manager()
    manager.convert()
    count_before = len(manager.recipes)
    new_recipe = _create_recipe("Сырники из творога")

    # Действие
    result = manager.add_recipe(new_recipe)

    # Проверки
    assert result == True
    assert len(manager.recipes) == count_before + 1


def test_false_recipe_manager_add_duplicate_recipe():
    """
    Ожидание: Повторное добавление существующей карты отклоняется (False).
    Метод: recipe_manager.add_recipe
    Описание: Уникальность по id — объект с тем же id не добавляется повторно.
    """
    # Подготовка
    manager = recipe_manager()
    manager.convert()
    existing_recipe = _create_recipe("Блины классические")
    manager.add_recipe(existing_recipe)
    count_before = len(manager.recipes)

    # Действие
    result = manager.add_recipe(existing_recipe)

    # Проверки
    assert result == False
    assert len(manager.recipes) == count_before


def test_false_recipe_manager_add_invalid_type():
    """
    Ожидание: Метод добавления отклоняет объекты неверного типа (False).
    Метод: recipe_manager.add_recipe
    Описание: Передача строки, числа, None или списка вместо recipe_model возвращает False.
    """
    # Подготовка
    manager = recipe_manager()

    # Действие и проверки
    assert manager.add_recipe("не карта") == False
    assert manager.add_recipe(123) == False
    assert manager.add_recipe(None) == False
    assert manager.add_recipe([]) == False


def test_success_recipe_manager_get_recipe():
    """
    Ожидание: Карта находится по идентификатору после добавления.
    Метод: recipe_manager.get_recipe
    Описание: Возвращается тот же объект, который был добавлен; для неизвестного id — None.
    """
    # Подготовка
    manager = recipe_manager()
    manager.convert()
    recipe = _create_recipe("Сырники из творога")
    manager.add_recipe(recipe)

    # Действие
    found = manager.get_recipe(recipe.id)
    missing = manager.get_recipe("00000000-0000-0000-0000-000000000000")

    # Проверки
    assert found is recipe
    assert missing is None


def test_none_recipe_manager_get_recipe_without_id():
    """
    Ожидание: Запрос по пустому идентификатору возвращает None.
    Метод: recipe_manager.get_recipe
    Описание: None в качестве идентификатора не является ошибкой - возвращает None.
    """
    # Подготовка
    manager = recipe_manager()

    # Действие и проверки
    assert manager.get_recipe(None) is None
    assert manager.get_recipe("   ") is None
