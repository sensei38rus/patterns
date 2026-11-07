import json
import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Logics.convertor import convertor
from Src.Core.validator import operation_exception
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
Рекурсивно сравнить ожидаемую и загруженную доменные модели по всем полям
"""
def assert_model_equal(expected, actual):
    assert actual is not None
    assert type(actual) is type(expected)
    assert actual.unique_code == expected.unique_code
    assert actual.name == expected.name

    if isinstance(expected, receipt_model):
        assert actual.comments == expected.comments
        assert actual.brutto == expected.brutto
        assert actual.netto == expected.netto
        assert len(actual.items) == len(expected.items)
        for expected_item, actual_item in zip(expected.items, actual.items):
            assert_model_equal(expected_item, actual_item)

    elif isinstance(expected, ingredient_model):
        assert actual.brutto == expected.brutto
        assert actual.netto == expected.netto
        assert_reference_equal(expected.group, actual.group)
        assert_reference_equal(expected.range, actual.range)
        assert_reference_equal(expected.base, actual.base)

    elif isinstance(expected, nomenclature_model):
        assert_reference_equal(expected.group, actual.group)
        assert_reference_equal(expected.range, actual.range)

    elif isinstance(expected, range_model):
        assert actual.value == expected.value
        assert_reference_equal(expected.base, actual.base)

    elif isinstance(expected, storage_model):
        assert actual.address == expected.address

    elif isinstance(expected, group_model):
        # Дополнительных полей у группы нет, наименование уже проверено
        pass


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
Проверить десериализацию всех данных storage_manager из Json.
Ожидается: загруженные модели совпадают с сформированными менеджером по всем полям
"""
def test_return_storage_data_convertor_deserialize_storage_manager():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    json_text = json.dumps(convertor().serialize(manager.data), ensure_ascii=False)

    # Действие
    loaded = convertor().deserialize(json_text)

    # Проверки
    assert isinstance(loaded, dict)
    # convertor().serialize оборачивает результат в поле "result"
    loaded = loaded["result"]
    assert set(loaded.keys()) == set(manager.data.keys())

    for key, expected_items in manager.data.items():
        actual_items = loaded[key]
        assert len(actual_items) == len(expected_items)
        for expected, actual in zip(expected_items, actual_items):
            assert_model_equal(expected, actual)

    # Ссылки разрешены на объекты из того же загруженного набора
    loaded_nomenclature = loaded[storage_manager.nomenclature_key()][0]
    loaded_group = loaded[storage_manager.group_key()][0]
    assert loaded_nomenclature.group is loaded_group

    loaded_receipt = loaded[storage_manager.receipt_key()][0]
    assert loaded_receipt.items[0].group is loaded_group


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
