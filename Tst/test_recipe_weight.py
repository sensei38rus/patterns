from Src.Logics.recipe_manager import recipe_manager
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


"""
Набор модульных тестов расчёта веса Брутто / Нетто технологических карт
"""


def _create_ingredient(name: str, quantity, unit=None, is_packaging: bool = False) -> recipe_item_model:
    """
    Вспомогательный метод - строка состава с указанной нормой расхода.
    По умолчанию единица измерения - грамм.
    """
    if unit is None:
        unit = range_model.create_gram()

    group = nomenclature_group_model("Тест")
    nomenclature = nomenclature_model(name, name, group, unit)
    return recipe_item_model(nomenclature, quantity, unit, None, "", is_packaging)


def _find_syrniki():
    """
    Вспомогательный метод - сгенерированная при первом старте карта "Сырники из творога классические".
    """
    manager = recipe_manager()
    manager.convert()
    return next(r for r in manager.recipes.values() if r.name == "Сырники из творога классические")


def test_success_recipe_item_model_weight_converts_to_base_unit():
    """
    Ожидание: Вес ингредиента пересчитан в базовую единицу измерения (2 кг -> 2000 г).
    Метод: recipe_item_model.weight (getter)
    Описание: Коэффициент пересчёта единицы измерения применяется к норме расхода.
    """
    # Arrange (Подготовка)
    kilogram = range_model.create_kilogram()
    item = _create_ingredient("Сахар", 2, kilogram)

    # Act (Действие)
    weight = item.weight

    # Assert (Проверка)
    assert weight == 2000


def test_success_recipe_model_weight_zero_for_empty_recipe():
    """
    Ожидание: Вес Брутто и Нетто пустой карты равен нулю.
    Метод: recipe_model.weight_brutto, recipe_model.weight_netto
    Описание: Нет ингредиентов - нет веса.
    """
    # Arrange (Подготовка)
    recipe = recipe_model("Пустая карта", 10, 1)

    # Act (Действие)
    brutto = recipe.weight_brutto
    netto = recipe.weight_netto

    # Assert (Проверка)
    assert brutto == 0
    assert netto == 0


def test_success_recipe_model_weight_brutto_equals_netto_without_packaging():
    """
    Ожидание: Без упаковки вес Брутто равен весу Нетто и равен сумме ингредиентов.
    Метод: recipe_model.weight_brutto, recipe_model.weight_netto
    Описание: 300 г муки + 50 г сахара = 350 в обеих величинах.
    """
    # Arrange (Подготовка)
    recipe = recipe_model("Тестовая карта", 10, 1)
    recipe.add_item(_create_ingredient("Мука", 300))
    recipe.add_item(_create_ingredient("Сахар", 50))

    # Act (Действие)
    brutto = recipe.weight_brutto
    netto = recipe.weight_netto

    # Assert (Проверка)
    assert netto == 350
    assert brutto == 350


def test_success_recipe_model_weight_brutto_includes_packaging():
    """
    Ожидание: Вес Брутто включает упаковку, вес Нетто - исключает её.
    Метод: recipe_model.weight_brutto, recipe_model.weight_netto
    Описание: 300 г муки + упаковка 1 шт -> Нетто 300, Брутто 301.
    """
    # Arrange (Подготовка)
    recipe = recipe_model("Тестовая карта", 10, 1)
    recipe.add_item(_create_ingredient("Мука", 300))
    recipe.add_item(_create_ingredient("Коробка", 1, range_model.create_piece(), True))

    # Act (Действие)
    brutto = recipe.weight_brutto
    netto = recipe.weight_netto

    # Assert (Проверка)
    assert netto == 300
    assert brutto == 301


def test_success_recipe_model_weight_includes_sub_recipes():
    """
    Ожидание: Вес родительской карты включает вес вложенного полуфабриката.
    Метод: recipe_model.weight_brutto, recipe_model.weight_netto
    Описание: Родитель (20) + полуфабрикат (300) -> Нетто 320; упаковка
              полуфабриката (1) попадает только в Брутто -> 321.
    """
    # Arrange (Подготовка)
    filling = recipe_model("Полуфабрикат", 5, 1)
    filling.add_item(_create_ingredient("Творог", 300))
    filling.add_item(_create_ingredient("Коробка", 1, range_model.create_piece(), True))

    parent = recipe_model("Блюдо", 10, 1)
    parent.add_item(_create_ingredient("Мука", 20))
    parent.add_sub_recipe(filling)

    # Assert (Проверка)
    assert filling.weight_netto == 300
    assert filling.weight_brutto == 301
    assert parent.weight_netto == 320
    assert parent.weight_brutto == 321


def test_success_recipe_model_weight_after_add_item():
    """
    Ожидание: После добавления ингредиента веса Брутто и Нетто выросли на его вес.
    Метод: recipe_model.add_item, recipe_model.weight_brutto, recipe_model.weight_netto
    Описание: Добавление сахара 30 г увеличивает обе величины ровно на 30.
    """
    # Arrange (Подготовка)
    recipe = recipe_model("Тестовая карта", 10, 1)
    recipe.add_item(_create_ingredient("Мука", 300))
    netto_before = recipe.weight_netto
    brutto_before = recipe.weight_brutto
    sugar = _create_ingredient("Сахар", 30)

    # Act (Действие)
    result = recipe.add_item(sugar)

    # Assert (Проверка)
    assert result == True
    assert recipe.weight_netto == netto_before + 30
    assert recipe.weight_brutto == brutto_before + 30


def test_success_recipe_model_weight_after_remove_item():
    """
    Ожидание: После исключения ингредиента веса Брутто и Нетто уменьшились на его вес.
    Метод: recipe_model.remove_item, recipe_model.weight_brutto, recipe_model.weight_netto
    Описание: Удаление сахара 30 г возвращает обе величины к исходным значениям.
    """
    # Arrange (Подготовка)
    recipe = recipe_model("Тестовая карта", 10, 1)
    recipe.add_item(_create_ingredient("Мука", 300))
    sugar = _create_ingredient("Сахар", 30)
    recipe.add_item(sugar)
    netto_before = recipe.weight_netto
    brutto_before = recipe.weight_brutto

    # Act (Действие)
    result = recipe.remove_item(sugar)

    # Assert (Проверка)
    assert result == True
    assert recipe.weight_netto == netto_before - 30
    assert recipe.weight_brutto == brutto_before - 30


def test_false_recipe_model_remove_item_not_found():
    """
    Ожидание: Повторное удаление той же строки возвращает False и не меняет веса.
    Метод: recipe_model.remove_item
    Описание: Строка уже удалена - повторный вызов не влияет на вес Брутто и Нетто.
    """
    # Arrange (Подготовка)
    recipe = recipe_model("Тестовая карта", 10, 1)
    sugar = _create_ingredient("Сахар", 30)
    recipe.add_item(sugar)
    recipe.remove_item(sugar)
    netto_before = recipe.weight_netto
    brutto_before = recipe.weight_brutto

    # Act (Действие)
    result = recipe.remove_item(sugar)

    # Assert (Проверка)
    assert result == False
    assert recipe.weight_netto == netto_before
    assert recipe.weight_brutto == brutto_before


def test_false_recipe_model_remove_invalid_item_type():
    """
    Ожидание: Удаление строки неверного типа возвращает False, веса не меняются.
    Метод: recipe_model.remove_item
    Описание: Передача строки вместо recipe_item_model не приводит к изменениям.
    """
    # Arrange (Подготовка)
    recipe = recipe_model("Тестовая карта", 10, 1)
    recipe.add_item(_create_ingredient("Мука", 300))
    netto_before = recipe.weight_netto
    brutto_before = recipe.weight_brutto

    # Act (Действие)
    result = recipe.remove_item("не строка состава")

    # Assert (Проверка)
    assert result == False
    assert recipe.weight_netto == netto_before
    assert recipe.weight_brutto == brutto_before


def test_success_recipe_manager_seeded_recipe_weights():
    """
    Ожидание: Сгенерированный при первом старте рецепт имеет вес Нетто 403 и Брутто 404.
    Метод: recipe_model.weight_brutto, recipe_model.weight_netto
    Описание: Нетто = полуфабрикат 363 (300+1+30+2+30) + мука 20 + масло 20;
              Брутто = Нетто + упаковка 1 (Docs/Recipe.md).
    """
    # Arrange (Подготовка)
    recipe = _find_syrniki()

    # Act (Действие)
    netto = recipe.weight_netto
    brutto = recipe.weight_brutto

    # Assert (Проверка)
    assert netto == 403
    assert brutto == 404
    assert brutto == netto + 1


def test_success_recipe_manager_seeded_recipe_weight_after_add_and_remove():
    """
    Ожидание: Веса сгенерированного рецепта пересчитываются при добавлении и исключении ингредиента.
    Метод: recipe_model.add_item, recipe_model.remove_item, weight_brutto, weight_netto
    Описание: Добавление сахара 30 г -> Нетто 433 / Брутто 434; после удаления
              возврат к исходным 403 / 404.
    """
    # Arrange (Подготовка)
    recipe = _find_syrniki()
    netto_before = recipe.weight_netto
    brutto_before = recipe.weight_brutto
    sugar = _create_ingredient("Сахар", 30)

    # Act (Действие)
    recipe.add_item(sugar)
    netto_with_sugar = recipe.weight_netto
    brutto_with_sugar = recipe.weight_brutto
    recipe.remove_item(sugar)

    # Assert (Проверка)
    assert netto_with_sugar == netto_before + 30
    assert brutto_with_sugar == brutto_before + 30
    assert recipe.weight_netto == netto_before
    assert recipe.weight_brutto == brutto_before
