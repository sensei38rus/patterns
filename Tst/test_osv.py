from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.osv_dto import osv_dto
from Src.Dtos.osv_row_dto import osv_row_dto
from Src.Logics.osv_prototype import osv_prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Models.receipt_model import receipt_model
import pytest

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

"""
Проверить создание osv_prototype без условия.
Условие по умолчанию: пустой filter_dto
"""
def test_empty_osv_prototype_create():
    # Подготовка

    # Действие
    prototype = osv_prototype()

    # Проверки
    assert prototype.condition is not None
    assert prototype.condition.entity == ""
    assert prototype.condition.field == ""
    assert prototype.condition.value == ""

"""
Проверить клонирование osv_prototype.
Копия независима: изменение копии не затрагивает оригинал
"""
def test_not_equal_osv_prototype_clone():
    # Подготовка
    prototype = osv_prototype().configure(
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
    assert prototype.condition.value == "Сахар"
    assert copy.condition.entity == "receipt_model"
    assert copy.condition.value == "fff"

"""
Проверить построение ОСВ по номенклатуре с фильтрацией (EQUALS).
Есть строка и итоги
"""
def test_not_empty_osv_prototype_build_nomenclature():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    prototype = osv_prototype().configure(
        entity=storage_manager.nomenclature_key(),
        field="name",
        value="Сахар",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    report = prototype.build(items)

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
def test_not_empty_osv_prototype_build_nested_range():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.range_key()]

    prototype = osv_prototype().configure(
        entity=storage_manager.range_key(),
        field="base.name",
        value="Грамм",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    report = prototype.build(items)

    # Проверки
    assert len(report.rows) >= 1
    assert all(row.entity == "range_model" for row in report.rows)
    assert all(row.turnover_debit > 0 for row in report.rows)
    assert report.total_turnover_debit > 0

"""
Проверить построение ОСВ по рецептам.
Оборот Дт = брутто, Кт = нетто, сальдо на конец = разница
"""
def test_not_empty_osv_prototype_build_receipt():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.receipt_key()]
    expected = items[0]

    prototype = osv_prototype().configure(
        entity=storage_manager.receipt_key(),
        field="unique_code",
        value=expected.unique_code,
        type=filter_type_enum.EQUALS,
    )

    # Действие
    report = prototype.build(items)

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
def test_not_empty_osv_prototype_build_group():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.group_key()]

    prototype = osv_prototype().configure(
        entity=storage_manager.group_key(),
        field="parent.name",
        value="Продукты",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    report = prototype.build(items)

    # Проверки
    assert len(report.rows) == 1
    assert report.rows[0].name == "Ингредиенты"
    assert report.total_turnover_debit == 0.0
    assert report.total_turnover_credit == 0.0

"""
Проверить построение ОСВ с несуществующим значением фильтра.
Пустая ведомость, итоги нулевые
"""
def test_empty_osv_prototype_build_not_found():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    items = manager.data[storage_manager.nomenclature_key()]

    prototype = osv_prototype().configure(
        entity=storage_manager.nomenclature_key(),
        field="name",
        value="Несуществующая позиция",
        type=filter_type_enum.EQUALS,
    )

    # Действие
    report = prototype.build(items)

    # Проверки
    assert len(report.rows) == 0
    assert report.total_opening_debit == 0.0
    assert report.total_turnover_debit == 0.0
    assert report.total_closing_debit == 0.0

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
Проверить передачу некорректного условия в конструктор osv_prototype.
Есть исключение argument_exception
"""
def test_raise_osv_prototype_fail_condition():
    # Подготовка

    # Действие и проверка
    with pytest.raises(argument_exception):
        osv_prototype("не filter_dto")

"""
Проверить передачу некорректного списка в osv_prototype.build.
Есть исключение argument_exception
"""
def test_raise_osv_prototype_build_fail_items():
    # Подготовка
    prototype = osv_prototype().configure(
        entity="nomenclature_model",
        field="name",
        value="Сахар",
    )

    # Действие и проверка
    with pytest.raises(argument_exception):
        prototype.build(None)
