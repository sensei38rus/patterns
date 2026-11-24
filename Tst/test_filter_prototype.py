from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.group_dto import group_dto
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.receipt_dto import receipt_dto
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
import pytest

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

"""
Проверить создание filter_prototype без условия.
Условие по умолчанию: пустой filter_dto
"""
def test_empty_filter_prototype_create():
    # Подготовка

    # Действие
    prototype = filter_prototype()

    # Проверки
    assert prototype.condition is not None
    assert prototype.condition.entity == ""
    assert prototype.condition.field == ""
    assert prototype.condition.value == ""
    assert prototype.condition.type == filter_type_enum.EQUALS

"""
Проверить создание filter_prototype с готовым условием.
Условие копируется, оригинал не изменяется
"""
def test_not_empty_filter_prototype_create():
    # Подготовка
    condition = filter_dto()
    condition.entity = "nomenclature_model"
    condition.field = "name"
    condition.value = "Сахар"
    condition.type = filter_type_enum.LIKE

    # Действие
    prototype = filter_prototype(condition)
    condition.value = "Другое"

    # Проверки
    assert prototype.condition.entity == "nomenclature_model"
    assert prototype.condition.field == "name"
    assert prototype.condition.value == "Сахар"
    assert prototype.condition.type == filter_type_enum.LIKE

"""
Проверить настройку условий через configure.
Нет исключения, возвращается тот же прототип
"""
def test_not_empty_filter_prototype_configure():
    # Подготовка
    prototype = filter_prototype()

    # Действие
    result = prototype.configure(
        entity="group_model",
        field="unique_code",
        value="abc",
        type=filter_type_enum.LIKE,
    )

    # Проверки
    assert result is prototype
    assert prototype.condition.entity == "group_model"
    assert prototype.condition.field == "unique_code"
    assert prototype.condition.value == "abc"
    assert prototype.condition.type == filter_type_enum.LIKE

"""
Проверить клонирование прототипа.
Копия независима: изменение копии не затрагивает оригинал
"""
def test_not_equal_filter_prototype_clone():
    # Подготовка
    prototype = filter_prototype()
    prototype.configure(
        entity="nomenclature_model",
        field="name",
        value="Сахар",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    copy = prototype.clone()
    copy.configure(
        entity="receipt_model",
        field="unique_code",
        value="fff",
        type=filter_type_enum.LIKE,
    )

    # Проверки
    assert copy is not prototype
    assert copy.condition is not prototype.condition
    assert prototype.condition.entity == "nomenclature_model"
    assert prototype.condition.field == "name"
    assert prototype.condition.value == "Сахар"
    assert prototype.condition.type == filter_type_enum.EQUALS
    assert copy.condition.entity == "receipt_model"
    assert copy.condition.field == "unique_code"
    assert copy.condition.value == "fff"
    assert copy.condition.type == filter_type_enum.LIKE

"""
Проверить передачу некорректного условия в конструктор.
Есть исключение argument_exception
"""
def test_raise_filter_prototype_fail_condition():
    # Подготовка

    # Действие и проверка
    with pytest.raises(argument_exception):
        filter_prototype("не filter_dto")

"""
Проверить фильтрацию номенклатуры (DOMAIN) одним прототипом
"""
def test_not_empty_filter_prototype_apply_nomenclature_model():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    prototype = filter_prototype().configure(
        entity=storage_manager.nomenclature_key(),
        field="name",
        value="Сахар",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    result = prototype.apply(items)

    # Проверки
    assert len(result) == 1
    assert result[0].name == "Сахар"

"""
Проверить фильтрацию группы (DOMAIN) тем же классом прототипа
"""
def test_not_empty_filter_prototype_apply_group_model():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.group_key()]
    expected = items[0]

    prototype = filter_prototype().configure(
        entity=storage_manager.group_key(),
        field="unique_code",
        value=expected.unique_code,
        type=filter_type_enum.EQUALS,
    )

    # Действие
    result = prototype.apply(items)

    # Проверки
    assert len(result) == 1
    assert result[0].unique_code == expected.unique_code

"""
Проверить фильтрацию единицы измерения (DOMAIN) тем же классом прототипа
"""
def test_not_empty_filter_prototype_apply_range_model():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.range_key()]

    prototype = filter_prototype().configure(
        entity=storage_manager.range_key(),
        field="unique_code",
        value=items[0].unique_code[:8],
        type=filter_type_enum.LIKE,
    )

    # Действие
    result = prototype.apply(items)

    # Проверки
    assert len(result) >= 1
    assert any(item.unique_code.startswith(condition) for item in result for condition in [items[0].unique_code[:8]])

"""
Проверить фильтрацию рецепта (DOMAIN) тем же классом прототипа
"""
def test_not_empty_filter_prototype_apply_receipt_model():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.receipt_key()]

    prototype = filter_prototype().configure(
        entity=storage_manager.receipt_key(),
        field="unique_code",
        value=items[0].unique_code[:8],
        type=filter_type_enum.LIKE,
    )

    # Действие
    result = prototype.apply(items)

    # Проверки
    assert len(result) >= 1
    assert any(condition in item.unique_code for item in result for condition in [items[0].unique_code[:8]])

"""
Проверить фильтрацию Dto-моделей номенклатуры тем же прототипом
"""
def test_not_empty_filter_prototype_apply_nomenclature_dto():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    items = []
    for domain in manager.data[storage_manager.nomenclature_key()]:
        items.append(nomenclature_dto().from_domain_model(domain))

    prototype = filter_prototype().configure(
        entity=storage_manager.nomenclature_key(),
        field="name",
        value="Сах",
        type=filter_type_enum.LIKE,
    )

    # Действие
    result = prototype.apply(items)

    # Проверки
    assert len(result) == 1
    assert isinstance(result[0], nomenclature_dto)
    assert "Сах" in result[0].name

"""
Проверить фильтрацию Dto-моделей группы, единицы измерения и рецепта
одним и тем же прототипом (clone на каждую задачу)
"""
def test_not_empty_filter_prototype_apply_all_dto_models():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    base = filter_prototype()

    group_items = [group_dto().from_domain_model(item) for item in manager.data[storage_manager.group_key()]]
    range_items = [range_dto().from_domain_model(item) for item in manager.data[storage_manager.range_key()]]
    receipt_items = [receipt_dto().from_domain_model(item) for item in manager.data[storage_manager.receipt_key()]]

    group_copy = base.clone().configure(
        entity=storage_manager.group_key(),
        field="unique_code",
        value=group_items[0].unique_code,
        type=filter_type_enum.EQUALS,
    )

    range_copy = base.clone().configure(
        entity=storage_manager.range_key(),
        field="unique_code",
        value=range_items[0].unique_code,
        type=filter_type_enum.EQUALS,
    )

    receipt_copy = base.clone().configure(
        entity=storage_manager.receipt_key(),
        field="unique_code",
        value=receipt_items[0].unique_code,
        type=filter_type_enum.EQUALS,
    )

    # Действие
    group_result = group_copy.apply(group_items)
    range_result = range_copy.apply(range_items)
    receipt_result = receipt_copy.apply(receipt_items)

    # Проверки
    assert len(group_result) == 1
    assert isinstance(group_result[0], group_dto)
    assert len(range_result) == 1
    assert isinstance(range_result[0], range_dto)
    assert len(receipt_result) == 1
    assert isinstance(receipt_result[0], receipt_dto)

    # Оригинал прототипа не изменился копиями
    assert base.condition.entity == ""
    assert base.condition.value == ""

"""
Проверить фильтрацию прототипом с несуществующим значением.
Пустой результат
"""
def test_empty_filter_prototype_apply_not_found():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    prototype = filter_prototype().configure(
        entity=storage_manager.nomenclature_key(),
        field="name",
        value="Несуществующая позиция",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    result = prototype.apply(items)

    # Проверки
    assert len(result) == 0

"""
Проверить передачу некорректного списка в filter_prototype.apply.
Есть исключение argument_exception
"""
def test_raise_filter_prototype_apply_fail_items():
    # Подготовка
    prototype = filter_prototype().configure(
        entity="nomenclature_model",
        field="name",
        value="Сахар",
    )

    # Действие и проверка
    with pytest.raises(argument_exception):
        prototype.apply(None)
