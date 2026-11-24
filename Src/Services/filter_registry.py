from Src.Core.filter_schema import filter_schema
from Src.Core.validator import argument_exception
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model

"""
Реестр схем фильтрации доменных сущностей (Registry).
Единый источник истины: ключ сущности -> filter_schema.
Модели регистрируют свои схемы; filter_dto и filter_service
не знают о конкретных сущностях и полях (Open/Closed:
новая сущность = регистрация, без правки фильтрации)
"""
class filter_registry:
    # Маппинг: ключ сущности -> схема фильтрации
    __schemas: dict = {}

    """
    Зарегистрировать схему фильтрации по ключу сущности
    """
    @staticmethod
    def register(entity: str, schema: filter_schema) -> None:
        if not isinstance(entity, str) or entity.strip() == "":
            raise argument_exception("Некорректный ключ доменной сущности!")
        if not isinstance(schema, filter_schema):
            raise argument_exception("Ожидается схема фильтрации filter_schema!")

        filter_registry.__schemas[entity.strip()] = schema

    """
    Зарегистрировать фильтруемую модель по её имени типа.
    Модели без схемы (filter_schema() is None) пропускаются
    """
    @staticmethod
    def register_model(model_type) -> None:
        if model_type is None or not hasattr(model_type, "filter_schema"):
            return

        schema = model_type.filter_schema()
        if schema is None:
            return

        filter_registry.register(model_type.__name__, schema)

    """
    Сущность зарегистрирована в реестре
    """
    @staticmethod
    def is_registered(entity: str) -> bool:
        return isinstance(entity, str) and entity in filter_registry.__schemas

    """
    Получить схему фильтрации сущности. None, если не зарегистрирована
    """
    @staticmethod
    def schema_for(entity: str) -> filter_schema:
        if not isinstance(entity, str):
            return None

        return filter_registry.__schemas.get(entity)

    """
    Проверить, что ключ сущности допустим для фильтрации
    """
    @staticmethod
    def validate_entity(entity: str) -> None:
        if not filter_registry.is_registered(entity):
            raise argument_exception(
                f"Недопустимая доменная сущность для фильтрации: {entity}!"
            )

    """
    Проверить путь поля.
    С указанной сущностью — по её схеме; без нее —
    по объединению всех зарегистрированных схем
    """
    @staticmethod
    def validate_field(path: str, entity: str = "") -> None:
        if not isinstance(path, str):
            raise argument_exception(f"Некорректное поле для фильтрации: {path}!")

        parts = path.split(".")
        if len(parts) < 1 or any(part.strip() == "" for part in parts):
            raise argument_exception(f"Некорректное поле для фильтрации: {path}!")

        if entity:
            filter_registry.validate_entity(entity)
            filter_registry.__schemas[entity].validate_path(path)
            return

        for schema in filter_registry.__schemas.values():
            if schema.is_valid_path(path):
                return

        raise argument_exception(f"Недопустимое поле для фильтрации: {path}!")

    """
    Регистрация фильтруемых доменных моделей.
    Выполняется при импорте модуля: тесты и приложение
    работают без ручной инициализации реестра
    """
    @staticmethod
    def bootstrap() -> None:
        for model_type in (
            nomenclature_model,
            group_model,
            range_model,
            receipt_model,
        ):
            filter_registry.register_model(model_type)


filter_registry.bootstrap()
