import uuid
import main

# Необходимо установить pip install pytest в терминале с подключенным Environment
# Интеграционные тесты проверяют работу REST API через тестовый клиент Connexion

"""
Создать тестовый клиент приложения
"""
def __create_client():
    return main.api.test_client()

"""
Создать доменную сущность через API. Ожидается успешный результат (201)
"""
def __create_entity(client, entity: str, payload: dict) -> dict:
    response = client.post(f"/api/entities/{entity}", json=payload)
    assert response.status_code == 201, response.text
    return response.json()

"""
Удалить доменную сущность через API
"""
def __delete_entity(client, entity: str, unique_code: str) -> None:
    client.delete(f"/api/entities/{entity}/{unique_code}")


"""
Проверить получение списка форматов отчетов в формате Json
"""
def test_success_api_get_formats():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.get("/api/formats")

    # Проверки
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert isinstance(data, list)
    assert {item["name"] for item in data} == {"TXT", "CSV", "MARKDOWN"}
    assert [item["code"] for item in data] == [1, 2, 3]
    assert all(item["content_type"] for item in data)
    assert len([item for item in data if item["is_default"]]) == 1

"""
Проверить получение списка доменных сущностей в формате Json
"""
def test_success_api_get_entities():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.get("/api/entities")

    # Проверки
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert isinstance(data, list)

    keys = [item["key"] for item in data]
    assert "group_model" in keys
    assert "receipt_model" in keys
    assert all(item["description"] for item in data)

"""
Проверить получение отчета по умолчанию для существующей сущности
"""
def test_success_api_get_default_report():
    # Подготовка
    client = __create_client()
    items = client.get("/api/entities/receipt_model").json()
    assert len(items) > 0
    unique_code = items[0]["unique_code"]

    # Действие
    response = client.get(
        "/api/get_default_report",
        params={"entity": "receipt_model", "unique_code": unique_code}
    )

    # Проверки
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text != ""

"""
Проверить запрос отчета без обязательных параметров.
Ожидается: 400 - параметры проверяются по спецификации OpenAPI
"""
def test_fail_api_get_default_report_without_params():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.get("/api/get_default_report")

    # Проверки
    assert response.status_code == 400

"""
Проверить запрос отчета для несуществующей сущности.
Ожидается: 404
"""
def test_fail_api_get_default_report_unknown_entity():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.get(
        "/api/get_default_report",
        params={"entity": "unknown_model", "unique_code": "0" * 32}
    )

    # Проверки
    assert response.status_code == 404

"""
Проверить полный цикл CRUD для доменной сущности (создание, чтение,
изменение, удаление)
"""
def test_success_api_crud_storage_model():
    # Подготовка
    client = __create_client()

    # Действие. Создание
    created = __create_entity(client, "storage_model", {
        "name": "Интеграционный склад",
        "address": "Иркутск, ул. Тестовая, д.1"
    })
    unique_code = created["unique_code"]

    # Проверки. Сущность попала в список
    items = client.get("/api/entities/storage_model").json()
    assert unique_code in [item["unique_code"] for item in items]

    # Действие. Чтение
    response = client.get(f"/api/entities/storage_model/{unique_code}")

    # Проверки
    assert response.status_code == 200
    assert response.json()["name"] == "Интеграционный склад"

    # Действие. Изменение
    response = client.put(
        f"/api/entities/storage_model/{unique_code}",
        json={"address": "Ангарск, ул. Ленина, д.2"}
    )

    # Проверки. Изменилось только переданное поле
    assert response.status_code == 200
    assert response.json()["address"] == "Ангарск, ул. Ленина, д.2"
    assert response.json()["name"] == "Интеграционный склад"

    # Действие. Удаление
    response = client.delete(f"/api/entities/storage_model/{unique_code}")

    # Проверки
    assert response.status_code == 204
    assert client.get(f"/api/entities/storage_model/{unique_code}").status_code == 404

"""
Проверить чтение несуществующей сущности.
Ожидается: 404
"""
def test_fail_api_get_entity_unknown_code():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.get("/api/entities/storage_model/" + uuid.uuid4().hex)

    # Проверки
    assert response.status_code == 404

"""
Проверить обращение к неизвестной коллекции доменных сущностей.
Ожидается: 404 для операций чтения, изменения и удаления
"""
def test_fail_api_unknown_collection():
    # Подготовка
    client = __create_client()
    code = uuid.uuid4().hex

    # Действие и проверки
    assert client.get("/api/entities/unknown_model").status_code == 404
    assert client.get(f"/api/entities/unknown_model/{code}").status_code == 404
    assert client.post("/api/entities/unknown_model", json={"name": "X"}).status_code == 404
    assert client.put(f"/api/entities/unknown_model/{code}", json={"name": "X"}).status_code == 404
    assert client.delete(f"/api/entities/unknown_model/{code}").status_code == 404

"""
Проверить создание сущности с некорректным типом.
Ожидается: 400 - тип тела запроса не соответствует ключу коллекции
"""
def test_fail_api_create_entity_wrong_type():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.post("/api/entities/storage_model", json={
        "type": "Src.Models.group_model.group_model",
        "name": "Группа вместо склада"
    })

    # Проверки
    assert response.status_code == 400

"""
Проверить создание сущности без наименования.
Ожидается: 400 - проверка корректности данных
"""
def test_fail_api_create_entity_without_name():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.post("/api/entities/storage_model", json={"address": "Иркутск"})

    # Проверки
    assert response.status_code == 400

"""
Проверить создание сущности с некорректной ссылкой на другую сущность.
Ожидается: 400 - ссылка не разрешается в существующую сущность
"""
def test_fail_api_create_entity_dangling_reference():
    # Подготовка
    client = __create_client()

    # Действие
    response = client.post("/api/entities/nomenclature_model", json={
        "name": "Несуществующая номенклатура",
        "group_code": uuid.uuid4().hex
    })

    # Проверки
    assert response.status_code == 400

"""
Проверить создание двух сущностей с одинаковым кодом.
Ожидается: 409 - конфликт уникальности
"""
def test_fail_api_create_entity_duplicate_code():
    # Подготовка
    client = __create_client()
    unique_code = uuid.uuid4().hex
    __create_entity(client, "storage_model", {"unique_code": unique_code, "name": "Первый склад"})

    # Действие
    response = client.post("/api/entities/storage_model", json={
        "unique_code": unique_code,
        "name": "Второй склад"
    })

    # Проверки
    assert response.status_code == 409

    # Очистка
    __delete_entity(client, "storage_model", unique_code)

"""
Проверить запрет удаления сущности, на которую ссылаются другие сущности.
Ожидается: 409 - проверка ссылочной целостности.
После удаления ссылки удаление разрешается
"""
def test_fail_api_delete_referenced_entity():
    # Подготовка
    client = __create_client()
    group = __create_entity(client, "group_model", {"name": "Группа для удаления"})
    nomenclature = __create_entity(client, "nomenclature_model", {
        "name": "Номенклатура группы",
        "group_code": group["unique_code"]
    })

    # Действие
    response = client.delete(f"/api/entities/group_model/{group['unique_code']}")

    # Проверки
    assert response.status_code == 409
    assert client.get(f"/api/entities/group_model/{group['unique_code']}").status_code == 200

    # Снимаем ссылку
    __delete_entity(client, "nomenclature_model", nomenclature["unique_code"])

    # Действие. Ссылок больше нет
    response = client.delete(f"/api/entities/group_model/{group['unique_code']}")

    # Проверки
    assert response.status_code == 204

"""
Проверить запрет изменения кода сущности, на которую ссылаются другие сущности.
Ожидается: 409. Изменение наименования при этом разрешено
"""
def test_fail_api_update_referenced_entity_code():
    # Подготовка
    client = __create_client()
    group = __create_entity(client, "group_model", {"name": "Группа для изменения"})
    nomenclature = __create_entity(client, "nomenclature_model", {
        "name": "Номенклатура группы",
        "group_code": group["unique_code"]
    })

    # Действие. Попытка изменить код
    response = client.put(
        f"/api/entities/group_model/{group['unique_code']}",
        json={"unique_code": uuid.uuid4().hex, "name": "Группа для изменения"}
    )

    # Проверки
    assert response.status_code == 409
    assert client.get(f"/api/entities/group_model/{group['unique_code']}").status_code == 200

    # Действие. Изменение наименования разрешено
    response = client.put(
        f"/api/entities/group_model/{group['unique_code']}",
        json={"name": "Новое имя группы"}
    )

    # Проверки
    assert response.status_code == 200
    assert response.json()["name"] == "Новое имя группы"

    # Очистка
    __delete_entity(client, "nomenclature_model", nomenclature["unique_code"])
    __delete_entity(client, "group_model", group["unique_code"])
