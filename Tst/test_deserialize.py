import json
from pathlib import Path

import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Logics.convertor import convertor
from Src.Core.validator import operation_exception
from Src.Core.abstract_model import abstact_model
from Src.Core.common import common
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.receipt_model import receipt_model
from Src.Models.storage_model import storage_model


"""
Сравнить ссылку на доменную модель (или None) по уникальному коду
"""
def assert_reference_equal(expected, actual):
    if expected is None:
        assert actual is None
    else:
        assert actual is not None
        assert actual.unique_code == expected.unique_code


"""
Рекурсивно сравнить ожидаемую и загруженную доменные модели по всем полям.
Свойства сравниваются полным перебором через common.get_fields,
чтобы ни одно поле модели не осталось без проверки
"""
def assert_model_equal(expected, actual):
    assert actual is not None
    assert type(actual) is type(expected)

    # Модель не должна накапливать посторонних (публичных) атрибутов при загрузке
    stray = [key for key in list(expected.__dict__.keys()) + list(actual.__dict__.keys())
             if not key.startswith("_")]
    assert stray == []

    # Все простые свойства (type, unique_code, name, value, address, brutto, ...)
    for field in common.get_fields(expected, is_common=True):
        expected_value = getattr(expected, field)
        actual_value = getattr(actual, field)

        if isinstance(expected_value, abstact_model):
            assert_reference_equal(expected_value, actual_value)
        else:
            assert actual_value == expected_value

    # Вложенные списки (состав рецепта)
    for field in common.get_fields(expected, is_common=False):
        expected_value = getattr(expected, field)
        if not isinstance(expected_value, list):
            continue

        actual_value = getattr(actual, field)
        assert len(actual_value) == len(expected_value)
        for expected_item, actual_item in zip(expected_value, actual_value):
            if isinstance(expected_item, abstact_model):
                assert_model_equal(expected_item, actual_item)
            else:
                assert actual_item == expected_item


"""
Собрать все доменные модели набора данных по уникальному коду,
включая вложенные (состав рецепта)
"""
def collect_models(data: dict) -> dict:
    registry = {}

    for items in data.values():
        for model in items:
            registry[ model.unique_code ] = model

            for field in common.get_fields(model, is_common=False):
                value = getattr(model, field)
                if not isinstance(value, list):
                    continue

                for element in value:
                    if isinstance(element, abstact_model):
                        registry[ element.unique_code ] = element

    return registry


"""
Проверить, что все ссылки загруженных моделей разрешены
на объекты из того же загруженного набора данных
"""
def assert_references_resolved(data: dict) -> None:
    registry = collect_models(data)

    for model in registry.values():
        for field in common.get_fields(model, is_common=True):
            value = getattr(model, field)

            if isinstance(value, abstact_model):
                assert value is registry.get(value.unique_code), \
                    f"Ссылка {field} модели {model.unique_code} не разрешена в наборе данных"


"""
Проверить десериализацию одной группы из Json строки в доменную модель.
Ожидается: модель группы восстановлена с тем же кодом и наименованием
"""
def test_return_group_convertor_deserialize_from_json():
    # Подготовка
    group = group_model.create_default_group()
    json_text = json.dumps(convertor().serialize(group), ensure_ascii=False)

    # Действие
    loaded = convertor().deserialize(json_text)

    # Проверки
    assert isinstance(loaded, dict)
    assert_model_equal(group, loaded["result"])


"""
Проверить десериализацию единиц измерения с разрешением ссылки на базовую единицу.
Ожидается: базовая единица восстановлена по уникальному коду из того же набора
"""
def test_return_ranges_convertor_deserialize_resolve_base():
    # Подготовка
    killogramm = range_model.create_killogramm()
    thing = range_model.create_thing()
    source = {
        storage_manager.range_key(): [killogramm.base, killogramm, thing]
    }
    json_text = json.dumps(convertor().serialize(source), ensure_ascii=False)

    # Действие
    loaded = convertor().deserialize(json_text)["result"][storage_manager.range_key()]

    # Проверки
    assert len(loaded) == 3
    for expected, actual in zip(source[storage_manager.range_key()], loaded):
        assert_model_equal(expected, actual)

    # Ссылка на базовую единицу указывает на объект из загруженного набора
    assert loaded[1].base is loaded[0]


"""
Проверить десериализацию номенклатуры с разрешением ссылок на группу и единицу измерения.
Ожидается: ссылки восстановлены по уникальным кодам из того же набора данных
"""
def test_return_nomenclature_convertor_deserialize_resolve_links():
    # Подготовка
    group = group_model.create_default_group()
    killogramm = range_model.create_killogramm()

    flour = nomenclature_model()
    flour.name = "Пшеничная мука"
    flour.group = group
    flour.range = killogramm

    source = {
        storage_manager.group_key(): [group],
        storage_manager.range_key(): [killogramm.base, killogramm],
        storage_manager.nomenclature_key(): [flour]
    }
    json_text = json.dumps(convertor().serialize(source), ensure_ascii=False)

    # Действие
    loaded = convertor().deserialize(json_text)["result"]

    # Проверки
    actual = loaded[storage_manager.nomenclature_key()][0]
    assert_model_equal(flour, actual)
    assert actual.group is loaded[storage_manager.group_key()][0]
    assert actual.range is loaded[storage_manager.range_key()][1]


"""
Проверить десериализацию рецепта с вложенными ингредиентами (вход - словарь).
Ожидается: состав восстановлен рекурсивно, веса брутто/нетто пересчитаны,
ссылки ингредиентов на группу и единицу измерения разрешены
"""
def test_return_receipt_convertor_deserialize_with_items():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    receipt = manager.data[storage_manager.receipt_key()][0]

    source = {
        storage_manager.group_key(): manager.data[storage_manager.group_key()],
        storage_manager.range_key(): manager.data[storage_manager.range_key()],
        storage_manager.receipt_key(): [receipt]
    }

    # Действие
    loaded = convertor().deserialize(convertor().serialize(source))["result"]

    # Проверки
    actual = loaded[storage_manager.receipt_key()][0]
    assert_model_equal(receipt, actual)
    assert actual.brutto == 256
    assert actual.netto == 256
    assert all(isinstance(item, ingredient_model) for item in actual.items)
    assert actual.items[0].group is loaded[storage_manager.group_key()][0]
    assert actual.items[0].range is not None


"""
Проверить полный цикл: выгрузить все данные storage_manager в Json,
загрузить обратно и сравнить.
Ожидается: структура, все модели по всем полям и ссылки совпадают с исходными,
повторная выгрузка загруженных данных дает тот же Json
"""
def test_return_storage_data_convertor_deserialize_storage_manager():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Выгрузка всех данных в Json строку
    dump_text = json.dumps(convertor().serialize(manager.data), ensure_ascii=False, sort_keys=True, indent=2)

    # Загрузка всех данных
    loaded = convertor().deserialize(dump_text)
    assert isinstance(loaded, dict)
    # convertor().serialize оборачивает результат в поле "result"
    loaded = loaded["result"]

    # Сравнение структуры: ключи наборов и количество моделей
    assert set(loaded.keys()) == set(manager.data.keys())
    for key, expected_items in manager.data.items():
        assert len(loaded[key]) == len(expected_items)

    # Сравнение всех моделей по всем полям (включая вложенные ингредиенты)
    expected_models = collect_models(manager.data)
    loaded_models = collect_models(loaded)
    assert set(loaded_models.keys()) == set(expected_models.keys())

    for key, expected_items in manager.data.items():
        for expected, actual in zip(expected_items, loaded[key]):
            assert_model_equal(expected, actual)

    # Все ссылки разрешены на объекты из того же загруженного набора
    assert_references_resolved(loaded)

    # Повторная выгрузка загруженных данных совпадает с исходной выгрузкой
    redump_text = json.dumps(convertor().serialize(loaded), ensure_ascii=False, sort_keys=True, indent=2)
    assert redump_text == dump_text


"""
Проверить загрузку сохраненного дампа Dumps/storage_data.json.
Ожидается: все данные читаются из файла, ссылки разрешены,
повторная выгрузка совпадает с содержимым файла
"""
def test_return_dump_file_convertor_deserialize_storage_data():
    # Подготовка
    dump_path = Path(__file__).parent.parent / "Dumps" / "storage_data.json"
    json_text = dump_path.read_text(encoding="utf-8")

    # Действие
    loaded = convertor().deserialize(json_text)
    assert isinstance(loaded, dict)
    loaded = loaded["result"]

    # Проверки структуры файла
    assert set(loaded.keys()) == set(storage_manager.domains().keys())
    assert len(loaded[storage_manager.group_key()]) == 1
    assert len(loaded[storage_manager.range_key()]) == 3
    assert len(loaded[storage_manager.nomenclature_key()]) == 5
    assert len(loaded[storage_manager.receipt_key()]) == 1
    assert len(loaded[storage_manager.storage_key()]) == 1

    # Рецепт загружен с составом и пересчитанными весами
    receipt = loaded[storage_manager.receipt_key()][0]
    assert isinstance(receipt, receipt_model)
    assert len(receipt.items) == 5
    assert receipt.brutto == 256
    assert receipt.netto == 256
    assert all(isinstance(item, ingredient_model) for item in receipt.items)

    # Все ссылки разрешены на объекты из загруженного набора
    assert_references_resolved(loaded)

    # Повторная выгрузка совпадает с содержимым файла (без учета форматирования пробелов)
    expected_text = json.dumps(json.loads(json_text), ensure_ascii=False, sort_keys=True, indent=2)
    redump_text = json.dumps(convertor().serialize(loaded), ensure_ascii=False, sort_keys=True, indent=2)
    assert redump_text == expected_text


"""
Проверить десериализацию некорректной Json строки.
Ожидается: operation_exception
"""
def test_raise_operation_exception_convertor_deserialize_invalid_json():
    # Подготовка и действие
    with pytest.raises(operation_exception):
        convertor().deserialize("{не является json")

    # Проверки - исключение выброшено (выполнено выше)


"""
Проверить десериализацию значения, не являющегося словарем или Json строкой.
Ожидается: operation_exception
"""
def test_raise_operation_exception_convertor_deserialize_unsupported_source():
    # Подготовка и действие
    with pytest.raises(operation_exception):
        convertor().deserialize([1, 2, 3])

    # Проверки - исключение выброшено (выполнено выше)
