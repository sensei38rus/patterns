from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Services.filter_service import filter_service
import pytest

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

"""
Проверить установку вложенного поля base.name в filter_dto.
Нет исключения
"""
def test_not_empty_filter_dto_nested_field_base_name():
    # Подготовка
    dto = filter_dto()

    # Действие
    dto.field = "base.name"

    # Проверки
    assert dto.field == "base.name"

"""
Проверить установку вложенных полей group, parent, range.
Нет исключения
"""
def test_not_empty_filter_dto_nested_fields_all_links():
    # Подготовка
    dto = filter_dto()

    # Действие
    dto.field = "group.unique_code"
    dto.field = "parent.name"
    dto.field = "range.name"

    # Проверки
    assert dto.field == "range.name"

"""
Проверить установку недопустимого вложенного поля.
Есть исключение argument_exception
"""
def test_raise_filter_dto_fail_nested_field():
    # Подготовка
    dto = filter_dto()

    # Действие и проверка
    with pytest.raises(argument_exception):
        dto.field = "items.name"

    with pytest.raises(argument_exception):
        dto.field = "base.address"

"""
Проверить разбор filter_dto из словаря (тела REST-запроса).
Включая вариант сравнения строкой LIKE
"""
def test_not_empty_filter_dto_from_dict():
    # Подготовка
    source = {
        "field": "base.name",
        "value": "Грамм",
        "type": "LIKE",
    }

    # Действие
    dto = filter_dto.from_dict(source)

    # Проверки
    assert dto.field == "base.name"
    assert dto.value == "Грамм"
    assert dto.type == filter_type_enum.LIKE
    assert dto.entity == ""

"""
Проверить фильтрацию единиц измерения по вложенной базовой единице (base.name).
Коллограмм ссылается на базовую единицу Грамм
"""
def test_not_empty_filter_service_apply_nested_base_name():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.range_key()]

    condition = filter_dto()
    condition.entity = storage_manager.range_key()
    condition.field = "base.name"
    condition.value = "Грамм"
    condition.type = filter_type_enum.EQUALS

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) >= 1
    assert all(item.base is not None and item.base.name == "Грамм" for item in result)
    assert any(item.name == "Коллограмм" for item in result)

"""
Проверить фильтрацию единиц измерения по вхождению в базовую единицу (base.name, LIKE)
"""
def test_not_empty_filter_service_apply_nested_base_name_like():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.range_key()]

    condition = filter_dto()
    condition.entity = storage_manager.range_key()
    condition.field = "base.name"
    condition.value = "грамм"
    condition.type = filter_type_enum.LIKE

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) >= 1
    assert any("грамм" in item.base.name.lower() for item in result)

"""
Проверить фильтрацию номенклатуры по вложенной группе (group.name)
"""
def test_not_empty_filter_service_apply_nested_group_name():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "group.name"
    condition.value = "Ингредиенты"
    condition.type = filter_type_enum.EQUALS

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) > 0
    assert all(item.group is not None and item.group.name == "Ингредиенты" for item in result)

"""
Проверить фильтрацию групп по вложенной группе-владельцу (parent.name)
"""
def test_not_empty_filter_service_apply_nested_parent_name():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.group_key()]

    condition = filter_dto()
    condition.entity = storage_manager.group_key()
    condition.field = "parent.name"
    condition.value = "Продукты"
    condition.type = filter_type_enum.EQUALS

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) == 1
    assert result[0].name == "Ингредиенты"
    assert result[0].parent.name == "Продукты"

"""
Проверить фильтрацию номенклатуры по вложенной единице измерения (range.name)
"""
def test_not_empty_filter_service_apply_nested_range_name():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "range.name"
    condition.value = "Коллограмм"
    condition.type = filter_type_enum.EQUALS

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) > 0
    assert all(item.range is not None and item.range.name == "Коллограмм" for item in result)

"""
Проверить фильтрацию через прототип по вложенному полю.
Нет исключения
"""
def test_not_empty_filter_prototype_apply_nested_field():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.range_key()]

    prototype = filter_prototype().configure(
        entity=storage_manager.range_key(),
        field="base.name",
        value="Грамм",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    result = prototype.apply(items)

    # Проверки
    assert len(result) >= 1
