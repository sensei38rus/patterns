from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Services.filter_service import filter_service
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
import pytest

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

"""
Проверить создание filter_dto.
Значения по умолчанию: пустые поля, тип EQUALS
"""
def test_empty_filter_dto_create():
    # Подготовка
    dto = filter_dto()

    # Действие

    # Проверки
    assert dto.entity == ""
    assert dto.field == ""
    assert dto.value == ""
    assert dto.type == filter_type_enum.EQUALS

"""
Проверить заполнение filter_dto корректными значениями.
Нет исключения
"""
def test_not_empty_filter_dto_create():
    # Подготовка
    dto = filter_dto()

    # Действие
    dto.entity = "nomenclature_model"
    dto.field = "name"
    dto.value = "Сахар"
    dto.type = filter_type_enum.LIKE

    # Проверки
    assert dto.entity == "nomenclature_model"
    assert dto.field == "name"
    assert dto.value == "Сахар"
    assert dto.type == filter_type_enum.LIKE

"""
Проверить установку недопустимой доменной сущности.
Есть исключение argument_exception
"""
def test_raise_filter_dto_fail_entity():
    # Подготовка
    dto = filter_dto()

    # Действие и проверка
    with pytest.raises(argument_exception):
        dto.entity = "storage_model"

"""
Проверить установку недопустимого поля фильтрации.
Есть исключение argument_exception
"""
def test_raise_filter_dto_fail_field():
    # Подготовка
    dto = filter_dto()

    # Действие и проверка
    with pytest.raises(argument_exception):
        dto.field = "address"

"""
Проверить фильтрацию номенклатуры по полному совпадению наименования (EQUALS)
"""
def test_not_empty_filter_service_apply_equals_name():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Сахар"
    condition.type = filter_type_enum.EQUALS

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) == 1
    assert result[0].name == "Сахар"

"""
Проверить фильтрацию номенклатуры по вхождению строки (LIKE)
"""
def test_not_empty_filter_service_apply_like_name():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Сах"
    condition.type = filter_type_enum.LIKE

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) == 1
    assert "Сах" in result[0].name

"""
Проверить фильтрацию по уникальному коду (EQUALS)
"""
def test_not_empty_filter_service_apply_equals_unique_code():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.group_key()]
    expected = items[0]

    condition = filter_dto()
    condition.entity = storage_manager.group_key()
    condition.field = "unique_code"
    condition.value = expected.unique_code
    condition.type = filter_type_enum.EQUALS

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) == 1
    assert result[0].unique_code == expected.unique_code

"""
Проверить фильтрацию единиц измерения по вхождению кода (LIKE)
"""
def test_not_empty_filter_service_apply_like_unique_code():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.range_key()]

    condition = filter_dto()
    condition.entity = storage_manager.range_key()
    condition.field = "unique_code"
    condition.value = items[0].unique_code[:8]
    condition.type = filter_type_enum.LIKE

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) >= 1
    assert any(condition.value in item.unique_code for item in result)

"""
Проверить фильтрацию рецептов по уникальному коду (LIKE).
Есть хотя бы один результат
"""
def test_not_empty_filter_service_apply_receipt_unique_code():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.receipt_key()]

    condition = filter_dto()
    condition.entity = storage_manager.receipt_key()
    condition.field = "unique_code"
    condition.value = items[0].unique_code[:8]
    condition.type = filter_type_enum.LIKE

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) >= 1
    assert any(condition.value in item.unique_code for item in result)

"""
Проверить фильтрацию с несуществующим значением.
Пустой результат
"""
def test_empty_filter_service_apply_not_found():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Несуществующая позиция"
    condition.type = filter_type_enum.EQUALS

    # Действие
    result = filter_service.apply(items, condition)

    # Проверки
    assert len(result) == 0

"""
Проверить передачу некорректного списка в filter_service.apply.
Есть исключение argument_exception
"""
def test_raise_filter_service_apply_fail_items():
    # Подготовка
    condition = filter_dto()
    condition.entity = "nomenclature_model"
    condition.field = "name"
    condition.value = "Сахар"

    # Действие и проверка
    with pytest.raises(argument_exception):
        filter_service.apply(None, condition)
