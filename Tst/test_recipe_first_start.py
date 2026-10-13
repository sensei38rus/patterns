from Src.Logics.recipe_manager import recipe_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model


"""
Набор модульных тестов генерации рецептов при первом старте (Docs/Recipe.md)
"""


def _find_recipe(name: str):
    """
    Вспомогательный метод - найти технологическую карту по наименованию.
    """
    manager = recipe_manager()
    manager.convert()
    return next((r for r in manager.recipes.values() if r.name == name), None)


def test_success_recipe_manager_creates_recipe_on_first_start():
    """
    Ожидание: При первом старте сгенерирована технологическая карта "Сырники из творога классические".
    Метод: recipe_manager.convert
    Описание: settings.json содержит is_first_start == True, поэтому convert()
              формирует рецепт по образцу Docs/Recipe.md.
    """
    # Arrange (Подготовка)
    manager = recipe_manager()

    # Act (Действие)
    manager.convert()
    names = [r.name for r in manager.recipes.values()]

    # Assert (Проверка)
    assert "Сырники из творога классические" in names


def test_success_recipe_manager_seeded_recipe_contains_sub_recipe():
    """
    Ожидание: Сгенерированный рецепт содержит полуфабрикат "Творожная масса".
    Метод: recipe_manager.__create_recipes
    Описание: Составная рецептура (п. 2.5 ТЗ) - основная карта включает вложенную
              карту полуфабриката.
    """
    # Arrange (Подготовка)
    recipe = _find_recipe("Сырники из творога классические")

    # Assert (Проверка)
    assert recipe is not None
    assert recipe.is_composite == True
    assert len(recipe.sub_recipes) == 1
    assert recipe.sub_recipes[0].name == "Творожная масса"


def test_success_recipe_manager_seeded_recipe_contains_packaging():
    """
    Ожидание: Сгенерированный рецепт содержит строку с упаковкой.
    Метод: recipe_manager.__create_recipes
    Описание: В составе основной карты присутствует "Коробка для завтраков"
              с признаком is_packaging == True.
    """
    # Arrange (Подготовка)
    recipe = _find_recipe("Сырники из творога классические")
    packaging_items = [i for i in recipe.items if i.is_packaging]

    # Assert (Проверка)
    assert len(packaging_items) == 1
    assert packaging_items[0].nomenclature.name == "Коробка для завтраков"
    assert packaging_items[0].quantity == 1


def test_success_recipe_manager_seeded_sub_filling_registered():
    """
    Ожидание: Полуфабрикат "Творожная масса" зарегистрирован отдельной технологической картой.
    Метод: recipe_manager.__create_recipes
    Описание: Обе карты (полуфабрикат и блюдо) доступны в хранилище рецептов.
    """
    # Act (Действие)
    filling = _find_recipe("Творожная масса")

    # Assert (Проверка)
    assert filling is not None
    assert filling.is_composite == False
    assert len(filling.items) == 5


def test_success_recipe_manager_seeded_recipe_ingredients():
    """
    Ожидание: Основная карта содержит 3 строки состава по Docs/Recipe.md.
    Метод: recipe_manager.__create_recipes
    Описание: Мука на подпыл (20 г), масло подсолнечное (20 мл) и упаковка (1 шт).
    """
    # Arrange (Подготовка)
    recipe = _find_recipe("Сырники из творога классические")
    names = [i.nomenclature.name for i in recipe.items]

    # Assert (Проверка)
    assert len(recipe.items) == 3
    assert "Мука пшеничная" in names
    assert "Масло подсолнечное" in names
    assert "Коробка для завтраков" in names
    assert recipe.steps[0].name == "Подготовка сырья"


def test_success_recipe_manager_convert_idempotent():
    """
    Ожидание: Повторный convert() не дублирует технологические карты.
    Метод: recipe_manager.convert
    Описание: Идемпотентность - второй вызов возвращает True, количество карт не меняется.
    """
    # Arrange (Подготовка)
    manager = recipe_manager()
    manager.convert()
    count_before = len(manager.recipes)

    # Act (Действие)
    result = manager.convert()

    # Assert (Проверка)
    assert result == True
    assert len(manager.recipes) == count_before


def test_true_recipe_manager_is_initialized():
    """
    Ожидание: Флаг is_initialized равен True после convert().
    Метод: recipe_manager.is_initialized (getter)
    Описание: После успешной инициализации внутренний флаг становится True.
    """
    # Arrange (Подготовка)
    manager = recipe_manager()

    # Act (Действие)
    manager.convert()

    # Assert (Проверка)
    assert manager.is_initialized == True


def test_empty_recipe_manager_convert_is_first_start_false():
    """
    Ожидание: Пустое хранилище при is_first_start == False.
    Метод: recipe_manager.convert(settings)
    Описание: При передаче настроек с is_first_start == False (DI) генерация
              технологических карт не выполняется.
    """
    # Arrange (Подготовка)
    if hasattr(recipe_manager, 'instance'):
        del recipe_manager.instance

    custom_settings = settings_model()
    custom_settings.is_first_start = False
    manager = recipe_manager()

    # Act (Действие)
    try:
        result = manager.convert(settings=custom_settings)

        # Assert (Проверка)
        assert result == True
        assert len(manager.recipes) == 0
    finally:
        if hasattr(recipe_manager, 'instance'):
            del recipe_manager.instance
        if hasattr(storage_manager, 'instance'):
            del storage_manager.instance
