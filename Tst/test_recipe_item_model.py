import pytest
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_item_model import recipe_item_model


"""
Набор модульных тестов для класса recipe_item_model
"""


def _create_cottage_cheese() -> nomenclature_model:
    """
    Вспомогательный метод - тестовая номенклатура "Творог 9%".
    """
    gram = range_model.create_gram()
    group = nomenclature_group_model("Молочные продукты")
    return nomenclature_model("Творог 9%", "Творог 9% протёртый", group, gram)


def _create_fridge() -> storage_model:
    """
    Вспомогательный метод - тестовое место хранения "Холодильник цеха".
    """
    return storage_model(name="Холодильник цеха", address="ул. Промышленная, 5, пом. 102")


def test_success_recipe_item_model_full_creation():
    """
    Ожидание: Успешное создание строки состава с полным набором параметров.
    Метод: recipe_item_model.__init__
    Описание: Строка содержит ингредиент, норму расхода, единицу измерения,
              место хранения и примечание (шаблон из Docs/Recipe.md).
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()
    fridge = _create_fridge()

    # Act (Действие)
    item = recipe_item_model(cottage_cheese, 300, gram, fridge, "Протереть через сито")

    # Assert (Проверка)
    assert item.nomenclature is cottage_cheese
    assert item.quantity == 300
    assert item.range is gram
    assert item.storage is fridge
    assert item.note == "Протереть через сито"


def test_success_recipe_item_model_without_optional_values():
    """
    Ожидание: Успешное создание строки состава без места хранения и примечания.
    Метод: recipe_item_model.__init__
    Описание: storage и note необязательные реквизиты - допускают None и пустую строку.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()

    # Act (Действие)
    item = recipe_item_model(cottage_cheese, 300, gram)

    # Assert (Проверка)
    assert item.storage is None
    assert item.note == ""


def test_argument_exception_recipe_item_model_invalid_nomenclature_type():
    """
    Ожидание: Выброс argument_exception при передаче строки вместо номенклатуры.
    Метод: recipe_item_model.nomenclature (setter)
    Описание: Поле nomenclature должно быть экземпляром nomenclature_model.
    """
    # Arrange (Подготовка)
    gram = range_model.create_gram()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model("Творог 9%", 300, gram)


def test_argument_exception_recipe_item_model_none_nomenclature():
    """
    Ожидание: Выброс argument_exception при отсутствии ингредиента.
    Метод: recipe_item_model.nomenclature (setter)
    Описание: Ингредиент - обязательный реквизит строки состава, None недопустим.
    """
    # Arrange (Подготовка)
    gram = range_model.create_gram()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model(None, 300, gram)


def test_argument_exception_recipe_item_model_zero_quantity():
    """
    Ожидание: Выброс argument_exception при нулевой норме расхода.
    Метод: recipe_item_model.quantity (setter)
    Описание: Норма расхода должна быть строго больше нуля.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model(cottage_cheese, 0, gram)


def test_argument_exception_recipe_item_model_negative_quantity():
    """
    Ожидание: Выброс argument_exception при отрицательной норме расхода.
    Метод: recipe_item_model.quantity (setter)
    Описание: Отрицательные значения нормы расхода недопустимы.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model(cottage_cheese, -10, gram)


def test_argument_exception_recipe_item_model_non_numeric_quantity():
    """
    Ожидание: Выброс argument_exception при нечисловой норме расхода.
    Метод: recipe_item_model.quantity (setter)
    Описание: Поле quantity должно быть числом (int или float), а не строкой.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model(cottage_cheese, "300", gram)


def test_argument_exception_recipe_item_model_invalid_range_type():
    """
    Ожидание: Выброс argument_exception при передаче строки вместо единицы измерения.
    Метод: recipe_item_model.range (setter)
    Описание: Поле range должно быть экземпляром range_model.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model(cottage_cheese, 300, "грамм")


def test_argument_exception_recipe_item_model_invalid_storage_type():
    """
    Ожидание: Выброс argument_exception при передаче строки вместо склада.
    Метод: recipe_item_model.storage (setter)
    Описание: Поле storage должно быть storage_model или None.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model(cottage_cheese, 300, gram, "Холодильник цеха")


def test_success_recipe_item_model_boundary_255_note():
    """
    Ожидание: Успешное создание строки состава с примечанием ровно в 255 символов.
    Метод: recipe_item_model.note (setter)
    Описание: Граничное значение - примечание в 255 символов допустимо.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()
    long_note = "А" * 255

    # Act (Действие)
    item = recipe_item_model(cottage_cheese, 300, gram, note=long_note)

    # Assert (Проверка)
    assert len(item.note) == 255


def test_max_length_exception_recipe_item_model_note_too_long():
    """
    Ожидание: Выброс max_length_exception при примечании длиннее 255 символов.
    Метод: recipe_item_model.note (setter)
    Описание: Примечание к строке состава ограничено 255 символами.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()
    too_long_note = "А" * 256

    # Act & Assert (Действие и Проверка)
    with pytest.raises(max_length_exception):
        recipe_item_model(cottage_cheese, 300, gram, note=too_long_note)


def test_argument_exception_recipe_item_model_invalid_note_type():
    """
    Ожидание: Выброс argument_exception при нестроковом примечании.
    Метод: recipe_item_model.note (setter)
    Описание: Поле note должно быть строкой.
    """
    # Arrange (Подготовка)
    cottage_cheese = _create_cottage_cheese()
    gram = range_model.create_gram()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_item_model(cottage_cheese, 300, gram, note=123)
