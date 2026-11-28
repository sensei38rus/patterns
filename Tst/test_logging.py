import pytest
import main
from Src.Core.abstract_subject import abstract_subject
from Src.Core.abstract_observer import abstract_observer
from Src.Core.validator import argument_exception, operation_exception
from Src.Dtos.log_category_enum import log_category_enum
from Src.Dtos.log_event_dto import log_event_dto
from Src.Logics.log_publisher import log_publisher
from Src.Logics.log_observer import log_observer
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Models.receipt_model import receipt_model
from Src.Models.storage_model import storage_model
from Src.Services.osv_service import osv_service
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

"""
Наблюдатель-шпион: накапливает события журнала в памяти.
Используется для проверки рассылки событий без обращения к файлу
"""
class spy_observer(abstract_observer):
    def __init__(self):
        self.events = []

    """
    Получить уведомление наблюдаемого объекта
    """
    def update(self, event) -> None:
        self.events.append(event)

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
Подписать наблюдателя на издатель событий журнала
"""
def __subscribe(observer) -> None:
    log_publisher().subscribe(observer)

"""
Отписать шпиона от издатель событий
"""
def __unsubscribe(observer) -> None:
    log_publisher().unsubscribe(observer)


"""
Проверить рассылку события подписанным наблюдателям.
Подписанный наблюдатель получает событие
"""
def test_notify_observer_abstract_subject_subscribe():
    # Подготовка
    subject = abstract_subject()
    observer = spy_observer()
    subject.subscribe(observer)

    # Действие
    subject.notify(log_event_dto(log_category_enum.CRUD, "create"))

    # Проверки
    assert len(observer.events) == 1
    assert observer.events[0].operation == "create"

"""
Проверить рассылку события после отписки наблюдателя.
Отписанный наблюдатель событие не получает
"""
def test_not_notify_observer_abstract_subject_unsubscribe():
    # Подготовка
    subject = abstract_subject()
    observer = spy_observer()
    subject.subscribe(observer)
    subject.unsubscribe(observer)

    # Действие
    subject.notify(log_event_dto(log_category_enum.CRUD, "create"))

    # Проверки
    assert len(observer.events) == 0
    assert len(subject.observers) == 0

"""
Проверить повторную подписку наблюдателя.
Однако событие доставляется наблюдателю один раз
"""
def test_not_duplicate_observer_abstract_subject_subscribe():
    # Подготовка
    subject = abstract_subject()
    observer = spy_observer()
    subject.subscribe(observer)
    subject.subscribe(observer)

    # Действие
    subject.notify(log_event_dto(log_category_enum.WEB, "get_entities"))

    # Проверки
    assert len(subject.observers) == 1
    assert len(observer.events) == 1

"""
Проверить журнал при добавлении складской сущности.
Событие фиксируется в категориях WAREHOUSE и CRUD
"""
def test_contains_warehouse_event_storage_manager_add():
    # Подготовка
    manager = __create_manager()
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        new_storage = storage_model()
        new_storage.name = "Склад журнала"
        manager.add(storage_manager.storage_key(), new_storage)

        # Проверки
        events = [item for item in observer.events if item.operation == "create"]
        assert len(events) == 1
        assert events[0].category == log_category_enum.WAREHOUSE
        assert events[0].belongs_to(log_category_enum.WAREHOUSE)
        assert events[0].belongs_to(log_category_enum.CRUD)
        assert events[0].entity == storage_manager.storage_key()
        assert events[0].unique_code == new_storage.unique_code
        assert events[0].status == "success"
    finally:
        __unsubscribe(observer)

"""
Проверить журнал при добавлении производственной сущности.
Событие фиксируется в категории CRUD
"""
def test_contains_crud_event_storage_manager_add():
    # Подготовка
    manager = __create_manager()
    model = receipt_model()
    model.name = "Рецепт журнала"
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        manager.add(storage_manager.receipt_key(), model)

        # Проверки
        events = [item for item in observer.events if item.operation == "create"]
        assert len(events) == 1
        assert events[0].category == log_category_enum.CRUD
        assert events[0].belongs_to(log_category_enum.CRUD)
        assert not events[0].belongs_to(log_category_enum.WAREHOUSE)
        assert events[0].entity == storage_manager.receipt_key()
    finally:
        __unsubscribe(observer)

"""
Проверить журнал при изменении складской сущности.
Событие фиксируется с операцией update и списком измененных полей
"""
def test_contains_warehouse_event_storage_manager_update():
    # Подготовка
    manager = __create_manager()
    target = manager.data[storage_manager.nomenclature_key()][0]
    source = manager.data[storage_manager.nomenclature_key()][1]
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        manager.update(storage_manager.nomenclature_key(), target.unique_code, source, ["name"])

        # Проверки
        events = [item for item in observer.events if item.operation == "update"]
        assert len(events) == 1
        assert events[0].category == log_category_enum.WAREHOUSE
        assert events[0].belongs_to(log_category_enum.CRUD)
        assert events[0].unique_code == target.unique_code
        assert "name" in events[0].details["fields"]
    finally:
        __unsubscribe(observer)

"""
Проверить журнал при удалении складской сущности.
Событие фиксируется с операцией delete
"""
def test_contains_warehouse_event_storage_manager_remove():
    # Подготовка
    manager = __create_manager()
    target = manager.data[storage_manager.nomenclature_key()][-1]
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        manager.remove(storage_manager.nomenclature_key(), target.unique_code)

        # Проверки
        events = [item for item in observer.events if item.operation == "delete"]
        assert len(events) == 1
        assert events[0].category == log_category_enum.WAREHOUSE
        assert events[0].status == "success"
        assert events[0].unique_code == target.unique_code
    finally:
        __unsubscribe(observer)

"""
Проверить журнал неудачной операции с данными.
Ошибка фиксируется со статусом error, исключение пробрасывается
"""
def test_contains_error_event_storage_manager_remove():
    # Подготовка
    manager = __create_manager()
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        with pytest.raises(operation_exception):
            manager.remove(storage_manager.nomenclature_key(), "not_found")

        # Проверки
        events = [item for item in observer.events if item.operation == "delete"]
        assert len(events) == 1
        assert events[0].status == "error"
        assert events[0].message != ""
    finally:
        __unsubscribe(observer)

"""
Проверить журнал изменения параметров настроек.
Событие фиксируется в категории SETTINGS со списком измененных полей
"""
def test_contains_settings_event_settings_manager_update():
    # Подготовка
    # Используется экземпляр приложения: повторное создание синглтона
    # сбрасывает модель настроек, что недопустимо в рамках проверки
    manager = main.settings_manager
    previous = manager.settings.boss_name
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        result = manager.update({"boss_name": "Директор журнала"})

        # Проверки
        events = [item for item in observer.events if item.category == log_category_enum.SETTINGS]
        assert len(events) == 1
        assert events[0].operation == "update"
        assert events[0].status == "success"
        assert "boss_name" in events[0].details["changed"]
        assert events[0].details["after"]["boss_name"] == "Директор журнала"
        assert result.boss_name == "Директор журнала"
    finally:
        __unsubscribe(observer)
        if previous.strip():
            manager.update({"boss_name": previous})

"""
Проверить журнал при некорректном изменении настроек.
Ошибка фиксируется со статусом error, параметры не изменяются
"""
def test_contains_error_event_settings_manager_update():
    # Подготовка
    manager = main.settings_manager
    previous = manager.settings.boss_name
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        with pytest.raises(argument_exception):
            manager.update({"unknown_parameter": "value"})

        # Проверки
        events = [item for item in observer.events if item.category == log_category_enum.SETTINGS]
        assert len(events) == 1
        assert events[0].operation == "update"
        assert events[0].status == "error"
        assert manager.settings.boss_name == previous
    finally:
        __unsubscribe(observer)

"""
Проверить журнал складской операции построения ОСВ.
Событие фиксируется в категории WAREHOUSE с операцией osv
"""
def test_contains_warehouse_event_osv_service_build():
    # Подготовка
    manager = __create_manager()
    condition = filter_dto()
    condition.entity = storage_manager.nomenclature_key()
    condition.field = "name"
    condition.value = "Сахар"
    condition.type = filter_type_enum.EQUALS

    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        report = osv_service.build(manager, condition)

        # Проверки
        events = [item for item in observer.events if item.operation == "osv"]
        assert len(events) == 1
        assert events[0].category == log_category_enum.WAREHOUSE
        assert events[0].entity == storage_manager.nomenclature_key()
        assert events[0].details["rows"] == len(report.rows)
    finally:
        __unsubscribe(observer)

"""
Проверить запись события наблюдателем журнала в Json-файл.
Файл содержит событие в формате Json Lines
"""
def test_contains_file_log_observer_update(tmp_path):
    # Подготовка
    file_path = str(tmp_path / "journal.jsonl")
    observer = log_observer(file_path)
    __subscribe(observer)

    try:
        # Действие
        log_publisher().crud(
            "create", entity=storage_manager.receipt_key(),
            unique_code="unique", message="Сущность создана"
        )

        # Проверки
        assert observer.count >= 1
        assert observer.failures == 0
        assert observer.file_path == file_path

        records = observer.read()
        assert len(records) >= 1

        last = records[-1]
        assert last["category"] == log_category_enum.CRUD.value
        assert last["operation"] == "create"
        assert last["entity"] == storage_manager.receipt_key()
        assert last["unique_code"] == "unique"
        assert last["status"] == "success"
        assert last["timestamp"] != ""
    finally:
        __unsubscribe(observer)

"""
Проверить отбор событий наблюдателем журнала.
События выбираются по категории, операции и статусу
"""
def test_contains_records_log_observer_records(tmp_path):
    # Подготовка
    observer = log_observer(str(tmp_path / "journal.jsonl"))

    # Действие
    observer.update(log_event_dto(log_category_enum.CRUD, "create"))
    observer.update(log_event_dto(log_category_enum.WAREHOUSE, "osv"))
    failed = log_event_dto(log_category_enum.WAREHOUSE, "osv")
    failed.status = "error"
    observer.update(failed)

    # Проверки
    assert observer.count == 3
    assert len(observer.records(category=log_category_enum.WAREHOUSE)) == 2
    assert len(observer.records(operation="create")) == 1
    assert len(observer.records(status="error")) == 1
    assert len(observer.records(category="WEB")) == 0

"""
Проверить журнал вызова web метода.
Запрос к API фиксируется в категории WEB с кодом ответа
"""
def test_contains_web_event_api_get_entities():
    # Подготовка
    client = main.api.test_client()
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        response = client.get("/api/entities")

        # Проверки
        assert response.status_code == 200

        events = [item for item in observer.events if item.operation == "get_entities"]
        assert len(events) == 1
        assert events[0].category == log_category_enum.WEB
        assert events[0].status == "success"
        assert events[0].details["status_code"] == 200
        assert events[0].details["http_method"] == "GET"
        assert events[0].details["http_path"] == "/api/entities"
    finally:
        __unsubscribe(observer)

"""
Проверить журнал неудачного вызова web метода.
Ответ с кодом 4xx фиксируется со статусом error
"""
def test_contains_error_event_api_get_entity():
    # Подготовка
    client = main.api.test_client()
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        response = client.get("/api/entities/range_model/not_found")

        # Проверки
        assert response.status_code == 404

        events = [item for item in observer.events if item.operation == "get_entity"]
        assert len(events) == 1
        assert events[0].category == log_category_enum.WEB
        assert events[0].status == "error"
        assert events[0].entity == "range_model"
        assert events[0].details["status_code"] == 404
    finally:
        __unsubscribe(observer)

"""
Проверить журнал создания складской сущности через API.
Фиксируются два события: вызов web метода и складская операция
"""
def test_contains_warehouse_event_api_create_entity():
    # Подготовка
    client = main.api.test_client()
    observer = spy_observer()
    __subscribe(observer)
    unique_code = ""

    try:
        # Действие
        response = client.post("/api/entities/storage_model", json={"name": "Склад журнала"})

        # Проверки
        assert response.status_code == 201, response.text
        unique_code = response.json()["unique_code"]

        web_events = [item for item in observer.events if item.operation == "create_entity"]
        assert len(web_events) == 1
        assert web_events[0].category == log_category_enum.WEB
        assert web_events[0].details["status_code"] == 201

        warehouse_events = [
            item for item in observer.events
            if item.operation == "create" and item.entity == storage_manager.storage_key()
        ]
        assert len(warehouse_events) == 1
        assert warehouse_events[0].category == log_category_enum.WAREHOUSE
        assert warehouse_events[0].belongs_to(log_category_enum.CRUD)
        assert warehouse_events[0].unique_code == unique_code
    finally:
        __unsubscribe(observer)
        if unique_code:
            client.delete(f"/api/entities/storage_model/{unique_code}")

"""
Проверить журнал изменения настроек через API.
Изменение фиксируется в категориях SETTINGS и WEB
"""
def test_contains_settings_event_api_put_settings():
    # Подготовка
    client = main.api.test_client()
    previous = main.settings_manager.settings.boss_name
    observer = spy_observer()
    __subscribe(observer)

    try:
        # Действие
        response = client.put("/api/settings", json={"boss_name": "Директор API"})

        # Проверки
        assert response.status_code == 200, response.text
        assert response.json()["boss_name"] == "Директор API"

        settings_events = [item for item in observer.events if item.category == log_category_enum.SETTINGS]
        assert len(settings_events) == 1
        assert settings_events[0].operation == "update"
        assert settings_events[0].details["after"]["boss_name"] == "Директор API"

        web_events = [item for item in observer.events if item.operation == "put_settings"]
        assert len(web_events) == 1
        assert web_events[0].category == log_category_enum.WEB
        assert web_events[0].details["status_code"] == 200
    finally:
        __unsubscribe(observer)
        if previous.strip():
            client.put("/api/settings", json={"boss_name": previous})
