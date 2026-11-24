from Src.Core.filter_schema import filter_schema
from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Services.filter_registry import filter_registry
import pytest

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

"""
Проверить регистрацию новой фильтруемой сущности в реестре.
filter_dto не изменяется — Open/Closed
"""
def test_not_empty_filter_registry_register_new_entity():
    # Подготовка
    class demo_model:
        @classmethod
        def filter_schema(cls):
            return filter_schema.base()

    # Действие
    filter_registry.register_model(demo_model)

    dto = filter_dto()
    dto.entity = "demo_model"
    dto.field = "name"

    # Проверки
    assert filter_registry.is_registered("demo_model")
    assert dto.entity == "demo_model"
    assert dto.field == "name"

"""
Проверить, что модель без схемы фильтрации не регистрируется
"""
def test_empty_filter_registry_skip_model_without_schema():
    # Подготовка

    # Действие
    filter_registry.register_model(type("unknown_model", (), {}))

    # Проверки
    assert not filter_registry.is_registered("unknown_model")

"""
Проверить строгую проверку поля по схеме указанной сущности.
Поле, допустимое для другой сущности, отклоняется
"""
def test_raise_filter_dto_fail_field_not_in_entity_schema():
    # Подготовка
    dto = filter_dto()

    # Действие и проверка: у группы нет ссылки base
    with pytest.raises(argument_exception):
        dto.entity = "group_model"
        dto.field = "base.name"

"""
Проверить повторную проверку поля при смене сущности.
Некорректное для новой сущности поле вызывает исключение,
entity не изменяется
"""
def test_raise_filter_dto_fail_revalidate_field_on_entity_change():
    # Подготовка
    dto = filter_dto()
    dto.field = "parent.name"

    # Действие и проверка
    with pytest.raises(argument_exception):
        dto.entity = "range_model"

    # Проверки
    assert dto.entity == ""
    assert dto.field == "parent.name"

"""
Проверить корректную повторную проверку поля при смене сущности.
Допустимое поле сохраняется, entity устанавливается
"""
def test_not_empty_filter_dto_revalidate_field_on_entity_change():
    # Подготовка
    dto = filter_dto()
    dto.field = "parent.name"

    # Действие
    dto.entity = "group_model"

    # Проверки
    assert dto.entity == "group_model"
    assert dto.field == "parent.name"
