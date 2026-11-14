from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Logics.convertor import convertor
from Src.Logics.model_factory import model_factory
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import argument_exception, operation_exception, conflict_exception
import connexion
import uuid
import os

# Необходимо установить pip install "connexion[flask,uvicorn,swagger-ui]"
# Описание API (Swagger) находится в файле openapi.yaml

api = connexion.FlaskApp(__name__, specification_dir="./")
settings_manager = settings_manager()
settings_manager.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json"))

storage_manager = storage_manager(settings_manager.settings)
storage_manager.build()

"""
Сформировать ответ с описанием ошибки
"""
def __error(message: str, status: int):
    return {"message": message}, status

"""
Сериализовать доменную сущность в Json
"""
def __to_dict(model: abstact_model) -> dict:
    return convertor().serialize(model)["result"]

"""
Определить полное имя типа доменной сущности по ключу коллекции
"""
def __entity_type(entity: str) -> str:
    return model_factory().create(entity).type

"""
Подготовить тело запроса: при отсутствии маркеров типа и уникального кода
проставить их по ключу запрашиваемой коллекции
"""
def __prepare_body(body, entity: str):
    if not isinstance(body, dict):
        return body

    result = dict(body)
    if not result.get("type"):
        result["type"] = __entity_type(entity)
    if not result.get("unique_code"):
        result["unique_code"] = uuid.uuid4().hex

    return result

"""
Получить список полей модели по ключам тела запроса.
Ключ, оканчивающийся на "_code", означает ссылку на другую сущность
"""
def __model_fields(body: dict) -> list:
    result = []
    for key in body.keys():
        if key == "type":
            continue
        field = key[ : -len("_code") ] if key.endswith("_code") else key
        result.append(field)
    return result

"""
Проверить ссылки ("*_code") тела запроса: каждая ссылка должна
разрешаться в существующую доменную сущность
"""
def __check_references(body: dict, model: abstact_model) -> str:
    if not isinstance(body, dict):
        return ""

    for key, value in body.items():
        if not key.endswith("_code") or not isinstance(value, str) or value.strip() == "":
            continue

        reference = key[ : -len("_code") ]
        descriptor = getattr(type(model), reference, None)
        if not isinstance(descriptor, property) or descriptor.fset is None:
            continue

        current = getattr(model, reference, None)
        if not isinstance(current, abstact_model) or current.unique_code != value.strip():
            return f"Ссылка {key} = {value} не найдена среди доменных сущностей!"

    return ""

"""
Десериализовать тело запроса в доменную модель.
Возвращает (модель, тело, ошибка): ошибка заполнена, если данные некорректны
"""
def __parse_body(body, entity: str):
    body = __prepare_body(body, entity)

    try:
        model = convertor().deserialize(body, registry=storage_manager.registry())
    except (argument_exception, operation_exception, ValueError, TypeError, AttributeError) as ex:
        return None, body, __error(f"Некорректные данные сущности: {ex}", 400)

    if not isinstance(model, abstact_model) or type(model).__name__ != entity:
        return None, body, __error(f"Ожидается тип сущности {entity}!", 400)

    error = __check_references(body, model)
    if error:
        return None, body, __error(error, 400)

    return model, body, None


"""
Получить отчет в формате по умолчанию
"""
def get_default_report(entity: str, unique_code: str):
    if entity not in storage_manager.domains():
        return f"Неизвестная доменная сущность {entity}!", 404

    item = storage_manager.find(entity, unique_code)
    if item is None:
        return f"Сущность {entity} с кодом {unique_code} не найдена!", 404

    try:
        factory = report_factory(settings_manager.settings)
        report_type = factory.create_default()
        result = report_type().build(item)

        return result.text, 200, {'Content-Type': result.format}
    except Exception as ex:
        return  f"Ошибка: {ex}!", 500

"""
Получить список доменных сущностей
"""
def get_entities():
    result = [
        {"key": key, "description": description}
        for key, description in storage_manager.domains().items()
    ]
    return result, 200

"""
Получить список форматов для построения отчетов
"""
def get_formats():
    factory = report_factory(settings_manager.settings)
    return factory.formats(), 200

"""
Получить список сущностей указанного типа
"""
def get_entity_list(entity: str):
    if entity not in storage_manager.domains():
        return __error(f"Неизвестная доменная сущность {entity}!", 404)

    items = storage_manager.data[ entity ]
    return [__to_dict(item) for item in items], 200

"""
Получить сущность по уникальному коду
"""
def get_entity(entity: str, unique_code: str):
    if entity not in storage_manager.domains():
        return __error(f"Неизвестная доменная сущность {entity}!", 404)

    model = storage_manager.find(entity, unique_code)
    if model is None:
        return __error(f"Сущность {entity} с кодом {unique_code} не найдена!", 404)

    return __to_dict(model), 200

"""
Добавить новую сущность
"""
def create_entity(entity: str, body):
    if entity not in storage_manager.domains():
        return __error(f"Неизвестная доменная сущность {entity}!", 404)

    parsed = __parse_body(body, entity)
    if parsed[2] is not None:
        return parsed[2]
    model = parsed[0]

    if not model.name.strip():
        return __error("Не указано наименование сущности!", 400)

    try:
        storage_manager.add(entity, model)
    except conflict_exception as ex:
        return __error(str(ex), 409)
    except (argument_exception, operation_exception) as ex:
        return __error(str(ex), 400)

    return __to_dict(model), 201

"""
Изменить существующую сущность
"""
def update_entity(entity: str, unique_code: str, body):
    if entity not in storage_manager.domains():
        return __error(f"Неизвестная доменная сущность {entity}!", 404)

    target = storage_manager.find(entity, unique_code)
    if target is None:
        return __error(f"Сущность {entity} с кодом {unique_code} не найдена!", 404)

    # Код из тела запроса. Если не передан - код не меняется
    new_code = None
    if isinstance(body, dict):
        raw_code = body.get("unique_code")
        if isinstance(raw_code, str) and raw_code.strip() != "":
            new_code = raw_code.strip()

    parsed = __parse_body(body, entity)
    if parsed[2] is not None:
        return parsed[2]
    model, body = parsed[0], parsed[1]

    fields = __model_fields(body)
    try:
        storage_manager.update(entity, unique_code, model, fields, new_code)
    except conflict_exception as ex:
        return __error(str(ex), 409)
    except (argument_exception, operation_exception) as ex:
        return __error(str(ex), 400)

    return __to_dict(target), 200

"""
Удалить сущность
"""
def delete_entity(entity: str, unique_code: str):
    if entity not in storage_manager.domains():
        return __error(f"Неизвестная доменная сущность {entity}!", 404)

    try:
        storage_manager.remove(entity, unique_code)
    except conflict_exception as ex:
        return __error(str(ex), 409)
    except (argument_exception, operation_exception) as ex:
        return __error(str(ex), 404)

    return None, 204


api.add_api("openapi.yaml", validate_responses=False, strict_validation=False)

if __name__ == "__main__":
    api.run(host = "0.0.0.0", port = 8080)
