from Src.Logics.recipe_manager import recipe_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


"""
Набор модульных тестов фабричных методов доменных моделей
"""


def _find_syrniki():
    """
    Вспомогательный метод - сгенерированная при первом старте карта "Сырники из творога классические".
    """
    manager = recipe_manager()
    manager.convert()
    return next(r for r in manager.recipes.values() if r.name == "Сырники из творога классические")


def test_success_nomenclature_group_model_create_factories():
    """
    Ожидание: Фабричные методы создают 4 первичные группы номенклатуры.
    Метод: nomenclature_group_model.create_grocery, create_dairy, create_dishes, create_packaging
    Описание: Первый старт использует фабрики вместо прямых конструкторов.
    """
    # Act (Действие)
    groups = [
        nomenclature_group_model.create_grocery(),
        nomenclature_group_model.create_dairy(),
        nomenclature_group_model.create_dishes(),
        nomenclature_group_model.create_packaging(),
    ]

    # Assert (Проверка)
    assert [g.name for g in groups] == ["Бакалея", "Молочные продукты", "Блюда", "Упаковка"]


def test_success_storage_model_create_factories():
    """
    Ожидание: Фабричные методы создают первичные склады с корректными реквизитами.
    Метод: storage_model.create_main_storage, storage_model.create_fridge
    Описание: Наименования и адреса соответствуют данным первого старта.
    """
    # Act (Действие)
    main_storage = storage_model.create_main_storage()
    fridge = storage_model.create_fridge()

    # Assert (Проверка)
    assert main_storage.name == "Основной склад"
    assert main_storage.address == "ул. Промышленная, 5, пом. 101"
    assert fridge.name == "Холодильник цеха"
    assert fridge.address == "ул. Промышленная, 5, пом. 102"


def test_success_nomenclature_model_create_with_default_references():
    """
    Ожидание: Фабрика номенклатуры без аргументов создаёт группу и единицу измерения по умолчанию.
    Метод: nomenclature_model.create_flour, nomenclature_model.create_breakfast_box
    Описание: Мука -> группа "Бакалея" и килограмм; коробка -> группа "Упаковка" и штука.
    """
    # Act (Действие)
    flour = nomenclature_model.create_flour()
    box = nomenclature_model.create_breakfast_box()

    # Assert (Проверка)
    assert flour.name == "Мука пшеничная"
    assert flour.group.name == "Бакалея"
    assert flour.range.name == "килограмм"
    assert box.name == "Коробка для завтраков"
    assert box.group.name == "Упаковка"
    assert box.range.name == "штука"


def test_success_nomenclature_model_create_with_shared_references():
    """
    Ожидание: Переданные группы и единицы измерения сохраняются по ссылке.
    Метод: nomenclature_model.create_flour
    Описание: Фабрика не создаёт дубликаты справочников, если они переданы вызывающему коду.
    """
    # Arrange (Подготовка)
    group = nomenclature_group_model("Локальная группа")
    kilogram = range_model.create_kilogram()

    # Act (Действие)
    flour = nomenclature_model.create_flour(group, kilogram)

    # Assert (Проверка)
    assert flour.group is group
    assert flour.range is kilogram


def test_success_recipe_item_model_create_factories():
    """
    Ожидание: Фабрики строки состава выставляют корректный признак упаковки.
    Метод: recipe_item_model.create, recipe_item_model.create_packaging
    Описание: create -> is_packaging False, create_packaging -> is_packaging True.
    """
    # Arrange (Подготовка)
    flour = nomenclature_model.create_flour()
    gram = range_model.create_gram()

    # Act (Действие)
    ingredient = recipe_item_model.create(flour, 300, gram)
    packaging = recipe_item_model.create_packaging(flour, 1, gram)

    # Assert (Проверка)
    assert ingredient.is_packaging == False
    assert packaging.is_packaging == True
    assert ingredient.quantity == 300
    assert packaging.quantity == 1


def test_success_recipe_model_create_cottage_cheese_filling_standalone():
    """
    Ожидание: Фабрика создаёт полуфабрикат "Творожная масса" без внешних справочников.
    Метод: recipe_model.create_cottage_cheese_filling
    Описание: Самодостаточная фабрика - 5 ингредиентов, вес Нетто/Брутто 363.
    """
    # Act (Действие)
    filling = recipe_model.create_cottage_cheese_filling()

    # Assert (Проверка)
    assert filling.name == "Творожная масса"
    assert filling.is_composite == False
    assert len(filling.items) == 5
    assert filling.weight_netto == 363
    assert filling.weight_brutto == 363


def test_success_recipe_model_create_syrniki_standalone():
    """
    Ожидание: Фабрика создаёт карту "Сырники из творога классические" без внешних справочников.
    Метод: recipe_model.create_syrniki
    Описание: Составная карта с полуфабрикатом и упаковкой; веса Нетто 403 / Брутто 404.
    """
    # Act (Действие)
    recipe = recipe_model.create_syrniki()

    # Assert (Проверка)
    assert recipe.name == "Сырники из творога классические"
    assert recipe.is_composite == True
    assert recipe.sub_recipes[0].name == "Творожная масса"
    assert len(recipe.items) == 3
    assert len(recipe.steps) == 2
    assert recipe.weight_netto == 403
    assert recipe.weight_brutto == 404


def test_success_storage_manager_first_start_uses_factory_references():
    """
    Ожидание: Первый старт ссылается на общие экземпляры справочников storage_manager.
    Метод: storage_manager._initialize_primary_data
    Описание: Группа и единица измерения номенклатуры - те же объекты, что в реестре менеджера.
    """
    # Arrange (Подготовка)
    manager = storage_manager()
    manager.convert()
    flour = next(n for n in manager.nomenclatures.values() if n.name == "Мука пшеничная")
    grocery = next(g for g in manager.groups.values() if g.name == "Бакалея")
    kilogram = next(r for r in manager.ranges.values() if r.name == "килограмм")

    # Assert (Проверка)
    assert flour.group is grocery
    assert flour.range is kilogram


def test_success_recipe_manager_first_start_uses_factory_references():
    """
    Ожидание: Первый старт рецептов ссылается на общие экземпляры справочников storage_manager.
    Метод: recipe_manager._initialize_primary_data
    Описание: Номенклатура и склады в строках карт - те же объекты, что в реестре storage_manager.
    """
    # Arrange (Подготовка)
    storage = storage_manager()
    storage.convert()
    recipe = _find_syrniki()
    filling = recipe.sub_recipes[0]

    nomenclatures = {n.name: n for n in storage.nomenclatures.values()}
    storages = {s.name: s for s in storage.storages.values()}

    flour_item = next(i for i in recipe.items if i.nomenclature.name == "Мука пшеничная")
    packaging_item = next(i for i in recipe.items if i.is_packaging)
    cottage_item = next(i for i in filling.items if i.nomenclature.name == "Творог 9%")

    # Assert (Проверка)
    assert flour_item.nomenclature is nomenclatures["Мука пшеничная"]
    assert packaging_item.nomenclature is nomenclatures["Коробка для завтраков"]
    assert cottage_item.nomenclature is nomenclatures["Творог 9%"]
    assert flour_item.storage is storages["Основной склад"]
    assert cottage_item.storage is storages["Холодильник цеха"]
