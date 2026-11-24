from datetime import date
from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.osv_dto import osv_dto
from Src.Dtos.osv_row_dto import osv_row_dto
from Src.Services.osv_service import osv_service
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
import pytest

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

"""
Создать менеджер хранилища с тестовыми данными
"""
def __create_manager():
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    return manager

"""
Проверить построение ОСВ по номенклатуре с фильтрацией (EQUALS).
Есть строка и итоги
"""
def test_not_empty_osv_service_build_nomenclature():
    # Подготовка
    manager = __create_manager()

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Сахар"
    condition.type = filter_type_enum.EQUALS

    # Действие
    report = osv_service.build(manager, condition)

    # Проверки
    assert isinstance(report, osv_dto)
    assert report.entity == storage_manager.nomenclature_key()
    assert len(report.rows) == 1
    assert report.rows[0].name == "Сахар"
    assert report.total_turnover_debit > 0
    assert report.total_closing_debit == report.total_turnover_debit

"""
Проверить построение ОСВ по единицам измерения с фильтрацией вложенного поля.
Строка и итоги заполнены
"""
def test_not_empty_osv_service_build_nested_range():
    # Подготовка
    manager = __create_manager()

    condition = filter_dto()
    condition.entity = storage_manager.range_key()
    condition.field = "base.name"
    condition.value = "Грамм"
    condition.type = filter_type_enum.EQUALS

    # Действие
    report = osv_service.build(manager, condition)

    # Проверки
    assert len(report.rows) >= 1
    assert all(row.entity == "range_model" for row in report.rows)
    assert all(row.turnover_debit > 0 for row in report.rows)
    assert report.total_turnover_debit > 0

"""
Проверить построение ОСВ по рецептам.
Оборот Дт = брутто, Кт = нетто, сальдо на конец = разница
"""
def test_not_empty_osv_service_build_receipt():
    # Подготовка
    manager = __create_manager()
    expected = manager.data[storage_manager.receipt_key()][0]

    condition = filter_dto()
    condition.entity = storage_manager.receipt_key()
    condition.field = "unique_code"
    condition.value = expected.unique_code
    condition.type = filter_type_enum.EQUALS

    # Действие
    report = osv_service.build(manager, condition)

    # Проверки
    assert len(report.rows) == 1
    row = report.rows[0]
    assert row.entity == "receipt_model"
    assert row.turnover_debit == float(expected.brutto)
    assert row.turnover_credit == float(expected.netto)
    assert row.closing_debit == float(expected.brutto - expected.netto)
    assert row.closing_credit == 0.0
    assert report.total_turnover_debit == row.turnover_debit
    assert report.total_turnover_credit == row.turnover_credit

"""
Проверить построение ОСВ по группам (без оборотов).
Строки есть, обороты равны нулю
"""
def test_not_empty_osv_service_build_group():
    # Подготовка
    manager = __create_manager()

    condition = filter_dto()
    condition.entity = storage_manager.group_key()
    condition.field = "parent.name"
    condition.value = "Продукты"
    condition.type = filter_type_enum.EQUALS

    # Действие
    report = osv_service.build(manager, condition)

    # Проверки
    assert len(report.rows) == 1
    assert report.rows[0].name == "Ингредиенты"
    assert report.total_turnover_debit == 0.0
    assert report.total_turnover_credit == 0.0

"""
Проверить построение ОСВ с несуществующим значением фильтра.
Пустая ведомость, итоги нулевые
"""
def test_empty_osv_service_build_not_found():
    # Подготовка
    manager = __create_manager()

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Несуществующая позиция"
    condition.type = filter_type_enum.EQUALS

    # Действие
    report = osv_service.build(manager, condition)

    # Проверки
    assert len(report.rows) == 0
    assert report.total_opening_debit == 0.0
    assert report.total_turnover_debit == 0.0
    assert report.total_closing_debit == 0.0

"""
Проверить построение ОСВ с датой начала периода.
Начальные остатки нулевые (реестр не ведется), итоги корректны
"""
def test_not_empty_osv_service_build_with_date_from():
    # Подготовка
    manager = __create_manager()

    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Сахар"
    condition.type = filter_type_enum.EQUALS

    # Действие
    report = osv_service.build(manager, condition, date_from=date(2026, 1, 1))

    # Проверки
    assert len(report.rows) == 1
    assert report.rows[0].opening_debit == 0.0
    assert report.rows[0].opening_credit == 0.0

"""
Проверить сериализацию ОСВ в словарь.
Структура содержит entity, rows и totals
"""
def test_not_empty_osv_dto_to_dict():
    # Подготовка
    row = osv_row_dto()
    row.entity = "receipt_model"
    row.unique_code = "abc"
    row.name = "Тест"
    row.turnover_debit = 100
    row.turnover_credit = 90
    row.refresh_closing()

    report = osv_dto()
    report.entity = "receipt_model"
    report.add_row(row)
    report.refresh_totals()

    # Действие
    result = report.to_dict()

    # Проверки
    assert result["entity"] == "receipt_model"
    assert len(result["rows"]) == 1
    assert result["rows"][0]["closing_debit"] == 10.0
    assert result["totals"]["turnover_debit"] == 100.0
    assert result["totals"]["turnover_credit"] == 90.0
    assert result["totals"]["closing_debit"] == 10.0

"""
Проверить передачу некорректного менеджера в osv_service.build.
Есть исключение argument_exception
"""
def test_raise_osv_service_build_fail_manager():
    # Подготовка
    condition = filter_dto()
    condition.entity = "nomenclature_model"
    condition.field = "name"
    condition.value = "Сахар"

    # Действие и проверка
    with pytest.raises(argument_exception):
        osv_service.build(None, condition)

"""
Проверить передачу некорректного условия в osv_service.build.
Есть исключение argument_exception
"""
def test_raise_osv_service_build_fail_condition():
    # Подготовка
    manager = __create_manager()

    # Действие и проверка
    with pytest.raises(argument_exception):
        osv_service.build(manager, "не filter_dto")

"""
Проверить построение ОСВ без entity в условии.
Есть исключение argument_exception
"""
def test_raise_osv_service_build_fail_empty_entity():
    # Подготовка
    manager = __create_manager()
    condition = filter_dto()
    condition.field = "name"
    condition.value = "Сахар"

    # Действие и проверка
    with pytest.raises(argument_exception):
        osv_service.build(manager, condition)

"""
Проверить построение ОСВ с некорректной датой начала периода.
Есть исключение argument_exception
"""
def test_raise_osv_service_build_fail_date_from():
    # Подготовка
    manager = __create_manager()
    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Сахар"

    # Действие и проверка
    with pytest.raises(argument_exception):
        osv_service.build(manager, condition, date_from="не дата")
