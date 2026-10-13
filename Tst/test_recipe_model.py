import pytest
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_step_model import recipe_step_model
from Src.Models.recipe_model import recipe_model


"""
Набор модульных тестов для класса recipe_model
"""


def _create_ingredient(name: str, quantity: float) -> recipe_item_model:
    """
    Вспомогательный метод - строка состава для указанного ингредиента в граммах.
    """
    gram = range_model.create_gram()
    group = nomenclature_group_model("Молочные продукты")
    nomenclature = nomenclature_model(name, name, group, gram)
    return recipe_item_model(nomenclature, quantity, gram)


def _create_recipe(name: str = "Сырники из творога") -> recipe_model:
    """
    Вспомогательный метод - минимально корректная технологическая карта.
    """
    return recipe_model(name=name, cooking_time=30, portions=2, pieces=6)


def test_success_recipe_model_full_creation():
    """
    Ожидание: Успешное создание технологической карты с полным набором параметров.
    Метод: recipe_model.__init__
    Описание: Карта содержит наименование, время приготовления, выход в порциях
              и штуках, описание, строки состава, шаги и вложенные карты.
    """
    # Arrange (Подготовка)
    flour = _create_ingredient("Мука пшеничная", 50)
    sugar = _create_ingredient("Сахар", 30)
    step = recipe_step_model("Подготовка сырья", 1, "Муку просеять, творог протереть.")
    sub_recipe = recipe_model("Творожная масса", 10, 1)

    # Act (Действие)
    recipe = recipe_model(
        name="Сырники из творога классические",
        cooking_time=30,
        portions=2,
        pieces=6,
        description="Блюдо завтрака, подача горячими по 3 шт.",
        items=[flour, sugar],
        steps=[step],
        sub_recipes=[sub_recipe]
    )

    # Assert (Проверка)
    assert recipe.name == "Сырники из творога классические"
    assert recipe.cooking_time == 30
    assert recipe.portions == 2
    assert recipe.pieces == 6
    assert recipe.description == "Блюдо завтрака, подача горячими по 3 шт."
    assert recipe.items == [flour, sugar]
    assert recipe.steps == [step]
    assert recipe.sub_recipes == [sub_recipe]
    assert recipe.is_composite == True


def test_success_recipe_model_without_optional_values():
    """
    Ожидание: Успешное создание карты без выхода в штуках, описания и коллекций.
    Метод: recipe_model.__init__
    Описание: pieces, description и коллекции необязательны - по умолчанию None, пустая
              строка и пустые списки.
    """
    # Act (Действие)
    recipe = recipe_model(name="Блины классические", cooking_time=20, portions=4)

    # Assert (Проверка)
    assert recipe.pieces is None
    assert recipe.description == ""
    assert recipe.items == []
    assert recipe.steps == []
    assert recipe.sub_recipes == []
    assert recipe.is_composite == False


def test_argument_exception_recipe_model_empty_name():
    """
    Ожидание: Выброс argument_exception при пустом наименовании карты.
    Метод: abs_mod.name (setter)
    Описание: Наименование блюда/полуфабриката - обязательный реквизит карты.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_model(name="", cooking_time=30, portions=2)


def test_argument_exception_recipe_model_zero_cooking_time():
    """
    Ожидание: Выброс argument_exception при нулевом времени приготовления.
    Метод: recipe_model.cooking_time (setter)
    Описание: Время приготовления должно быть строго больше нуля.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_model(name="Сырники", cooking_time=0, portions=2)


def test_argument_exception_recipe_model_non_integer_cooking_time():
    """
    Ожидание: Выброс argument_exception при дробном времени приготовления.
    Метод: recipe_model.cooking_time (setter)
    Описание: Время приготовления задаётся целым числом минут.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_model(name="Сырники", cooking_time=30.5, portions=2)


def test_argument_exception_recipe_model_zero_portions():
    """
    Ожидание: Выброс argument_exception при нулевом выходе в порциях.
    Метод: recipe_model.portions (setter)
    Описание: Выход в порциях должен быть строго больше нуля.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_model(name="Сырники", cooking_time=30, portions=0)


def test_argument_exception_recipe_model_zero_pieces():
    """
    Ожидание: Выброс argument_exception при нулевом выходе в штуках.
    Метод: recipe_model.pieces (setter)
    Описание: Выход в штуках - положительное целое число или None.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_model(name="Сырники", cooking_time=30, portions=2, pieces=0)


def test_success_recipe_model_boundary_1000_description():
    """
    Ожидание: Успешное создание карты с описанием ровно в 1000 символов.
    Метод: recipe_model.description (setter)
    Описание: Граничное значение - описание в 1000 символов допустимо.
    """
    # Arrange (Подготовка)
    long_description = "А" * 1000

    # Act (Действие)
    recipe = recipe_model("Сырники", 30, 2, description=long_description)

    # Assert (Проверка)
    assert len(recipe.description) == 1000


def test_max_length_exception_recipe_model_description_too_long():
    """
    Ожидание: Выброс max_length_exception при описании длиннее 1000 символов.
    Метод: recipe_model.description (setter)
    Описание: Описание карты ограничено 1000 символами.
    """
    # Arrange (Подготовка)
    too_long_description = "А" * 1001

    # Act & Assert (Действие и Проверка)
    with pytest.raises(max_length_exception):
        recipe_model("Сырники", 30, 2, description=too_long_description)


def test_success_recipe_model_add_item():
    """
    Ожидание: Строка состава добавляется в карту (True).
    Метод: recipe_model.add_item
    Описание: Новая строка состава попадает в коллекцию items.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    flour = _create_ingredient("Мука пшеничная", 50)

    # Act (Действие)
    result = recipe.add_item(flour)

    # Assert (Проверка)
    assert result == True
    assert recipe.items == [flour]


def test_false_recipe_model_add_duplicate_item():
    """
    Ожидание: Повторное добавление той же строки состава отклоняется (False).
    Метод: recipe_model.add_item
    Описание: Уникальность по id - дубликат не увеличивает коллекцию.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    flour = _create_ingredient("Мука пшеничная", 50)
    recipe.add_item(flour)
    count_before = len(recipe.items)

    # Act (Действие)
    result = recipe.add_item(flour)

    # Assert (Проверка)
    assert result == False
    assert len(recipe.items) == count_before


def test_false_recipe_model_add_invalid_item_type():
    """
    Ожидание: Добавление строки состава неверного типа отклоняется (False).
    Метод: recipe_model.add_item
    Описание: Передача строки вместо recipe_item_model возвращает False.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()

    # Act & Assert (Действие и Проверка)
    assert recipe.add_item("не строка состава") == False
    assert recipe.add_item(None) == False


def test_argument_exception_recipe_model_items_not_list():
    """
    Ожидание: Выброс argument_exception при присвоении коллекции не-списка.
    Метод: recipe_model.items (setter)
    Описание: Поле items принимает только список.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe.items = "не список"


def test_argument_exception_recipe_model_items_invalid_element():
    """
    Ожидание: Выброс argument_exception при элементе неверного типа в списке items.
    Метод: recipe_model.items (setter)
    Описание: Каждый элемент списка должен быть recipe_item_model.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    flour = _create_ingredient("Мука пшеничная", 50)

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe.items = [flour, "сахар"]


def test_success_recipe_model_add_step():
    """
    Ожидание: Шаг технологического процесса добавляется в карту (True).
    Метод: recipe_model.add_step
    Описание: Новый шаг попадает в коллекцию steps.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    step = recipe_step_model("Подготовка сырья", 1, "Проверить сроки годности сырья.")

    # Act (Действие)
    result = recipe.add_step(step)

    # Assert (Проверка)
    assert result == True
    assert recipe.steps == [step]


def test_false_recipe_model_add_invalid_step_type():
    """
    Ожидание: Добавление шага неверного типа отклоняется (False).
    Метод: recipe_model.add_step
    Описание: Передача числа вместо recipe_step_model возвращает False.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()

    # Act & Assert (Действие и Проверка)
    assert recipe.add_step(1) == False


def test_argument_exception_recipe_model_steps_invalid_element():
    """
    Ожидание: Выброс argument_exception при элементе неверного типа в списке steps.
    Метод: recipe_model.steps (setter)
    Описание: Каждый элемент списка должен быть recipe_step_model.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    step = recipe_step_model("Подготовка сырья", 1, "Проверить сроки годности сырья.")

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe.steps = [step, 42]


def test_success_recipe_model_add_sub_recipe():
    """
    Ожидание: Вложенная карта добавляется, флаг is_composite становится True.
    Метод: recipe_model.add_sub_recipe
    Описание: Реализация составной рецептуры (п. 2.5 ТЗ) - одна карта в составе другой.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    sub_recipe = recipe_model("Творожная масса", 10, 1)
    count_before = len(recipe.sub_recipes)

    # Act (Действие)
    result = recipe.add_sub_recipe(sub_recipe)

    # Assert (Проверка)
    assert result == True
    assert len(recipe.sub_recipes) == count_before + 1
    assert recipe.sub_recipes[0] is sub_recipe
    assert recipe.is_composite == True


def test_false_recipe_model_add_duplicate_sub_recipe():
    """
    Ожидание: Повторное добавление вложенной карты отклоняется (False).
    Метод: recipe_model.add_sub_recipe
    Описание: Уникальность по id - дубликат вложенной карты не добавляется.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    sub_recipe = recipe_model("Творожная масса", 10, 1)
    recipe.add_sub_recipe(sub_recipe)
    count_before = len(recipe.sub_recipes)

    # Act (Действие)
    result = recipe.add_sub_recipe(sub_recipe)

    # Assert (Проверка)
    assert result == False
    assert len(recipe.sub_recipes) == count_before


def test_false_recipe_model_add_self_as_sub_recipe():
    """
    Ожидание: Добавление карты самой в себя отклоняется (False).
    Метод: recipe_model.add_sub_recipe
    Описание: Непосредственный цикл ссылок запрещён - карта не может входить в свой состав.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()

    # Act & Assert (Действие и Проверка)
    assert recipe.add_sub_recipe(recipe) == False
    assert recipe.is_composite == False


def test_false_recipe_model_add_sub_recipe_cycle():
    """
    Ожидание: Добавление карты, в поддереве которой уже содержится текущая, отклоняется (False).
    Метод: recipe_model.add_sub_recipe
    Описание: Косвенный цикл A -> B -> A запрещён (A уже содержит B, поэтому B нельзя
              вложить в A повторно).
    """
    # Arrange (Подготовка)
    recipe_a = recipe_model("Блюдо А", 30, 2)
    recipe_b = recipe_model("Полуфабрикат Б", 10, 1)
    recipe_a.add_sub_recipe(recipe_b)

    # Act (Действие)
    result = recipe_b.add_sub_recipe(recipe_a)

    # Assert (Проверка)
    assert result == False
    assert recipe_b.is_composite == False


def test_argument_exception_recipe_model_add_invalid_sub_recipe_type():
    """
    Ожидание: Добавление вложенной карты неверного типа отклоняется (False).
    Метод: recipe_model.add_sub_recipe
    Описание: Передача строки вместо recipe_model возвращает False.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()

    # Act & Assert (Действие и Проверка)
    assert recipe.add_sub_recipe("не карта") == False


def test_argument_exception_recipe_model_sub_recipes_not_list():
    """
    Ожидание: Выброс argument_exception при присвоении коллекции не-списка.
    Метод: recipe_model.sub_recipes (setter)
    Описание: Поле sub_recipes принимает только список.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe.sub_recipes = {"не": "список"}


def test_argument_exception_recipe_model_sub_recipes_self_reference():
    """
    Ожидание: Выброс argument_exception при присвоении списка, содержащего саму карту.
    Метод: recipe_model.sub_recipes (setter)
    Описание: Циклическая ссылка на себя недопустима при массовом присвоении.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe.sub_recipes = [recipe]


def test_argument_exception_recipe_model_sub_recipes_duplicates():
    """
    Ожидание: Выброс argument_exception при дубликатах в списке sub_recipes.
    Метод: recipe_model.sub_recipes (setter)
    Описание: Одна и та же карта не может встречаться в составе дважды.
    """
    # Arrange (Подготовка)
    recipe = _create_recipe()
    sub_recipe = recipe_model("Творожная масса", 10, 1)

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe.sub_recipes = [sub_recipe, sub_recipe]


def test_success_recipe_model_syrniki_full_card():
    """
    Ожидание: Полная технологическая карта "Сырники из творога" из Docs/Recipe.md собирается без ошибок.
    Метод: recipe_model.__init__, add_item, add_step
    Описание: Сценарный тест - 6 ингредиентов, 3 шага, выход 2 порции (6 штук), время 30 минут.
    """
    # Arrange (Подготовка)
    fridge = storage_model(name="Холодильник цеха", address="ул. Промышленная, 5, пом. 102")
    main_storage = storage_model(name="Основной склад", address="ул. Промышленная, 5, пом. 101")
    gram = range_model.create_gram()
    milliliter = range_model.create_milliliter()
    piece = range_model.create_piece()
    dairy = nomenclature_group_model("Молочные продукты")
    grocery = nomenclature_group_model("Бакалея")

    items = [
        recipe_item_model(nomenclature_model("Творог 9%", "Творог 9%", dairy, gram), 300, gram, fridge),
        recipe_item_model(nomenclature_model("Яйца куриные", "Яйца куриные", dairy, piece), 1, piece, fridge),
        recipe_item_model(nomenclature_model("Сахар", "Сахар", grocery, gram), 30, gram, main_storage),
        recipe_item_model(nomenclature_model("Мука пшеничная", "Мука пшеничная", grocery, gram), 50, gram, main_storage),
        recipe_item_model(nomenclature_model("Соль", "Соль", grocery, gram), 2, gram, main_storage),
        recipe_item_model(nomenclature_model("Масло подсолнечное", "Масло подсолнечное", grocery, milliliter), 20, milliliter, main_storage),
    ]
    steps = [
        recipe_step_model("Подготовка сырья", 1, "Проверить сроки годности, муку просеять, творог протереть."),
        recipe_step_model("Замес творожной массы", 2, "Перетереть творог с яйцом, сахаром и солью, ввести муку."),
        recipe_step_model("Формовка и тепловая обработка", 3, "Сформовать сырники и обжарить по 2-3 минуты с каждой стороны."),
    ]

    # Act (Действие)
    recipe = recipe_model(
        name="Сырники из творога классические",
        cooking_time=30,
        portions=2,
        pieces=6,
        description="Подавать горячими по 3 штуки на порцию, не ниже 65°C.",
        items=items,
        steps=steps
    )

    # Assert (Проверка)
    assert len(recipe.items) == 6
    assert len(recipe.steps) == 3
    assert recipe.cooking_time == 30
    assert recipe.portions == 2
    assert recipe.pieces == 6
    assert recipe.is_composite == False
    assert recipe.items[0].nomenclature.name == "Творог 9%"
    assert recipe.items[0].quantity == 300
    assert recipe.steps[0].order == 1
    assert recipe.steps[2].name == "Формовка и тепловая обработка"
