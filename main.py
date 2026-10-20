from flask import Flask, Response, request
from Src.Core.exception import argument_exception
from Src.Logics.recipe_manager import recipe_manager
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager


"""
Точка входа веб-приложения API формирования отчетов.
"""
app = Flask(__name__)

# Инициализация менеджеров настроек и данных (первый старт)
settings = settings_manager()
settings.load()

storage = storage_manager()
storage.convert(settings.settings)

recipes = recipe_manager()
recipes.convert(settings.settings)

factory = report_factory(settings.settings)

# Соответствие переданного типа сущности внутреннему типу
ENTITY_TYPES = {
    "рецепт": "recipe",
    "recipe": "recipe",
    "номенклатура": "nomenclature",
    "nomenclature": "nomenclature",
    "единица": "unit",
    "единица измерения": "unit",
    "unit": "unit",
    "range": "unit",
}


def get_entity_collection(entity_type: str) -> dict:
    """
    Получить коллекцию сущностей по типу.
    """
    if entity_type == "recipe":
        return recipes.recipes

    if entity_type == "nomenclature":
        return storage.nomenclatures

    if entity_type == "unit":
        return storage.ranges

    return {}


def find_entity(entity_type: str, code: str):
    """
    Найти сущность по коду.
    Код вида 0, 1, 2 ... - позиция сущности в коллекции; иначе полный код (UUID).
    Возвращает None, если сущность не найдена.
    """
    collection = get_entity_collection(entity_type)
    code = str(code).strip()

    if code.isdigit():
        items = list(collection.values())
        index = int(code)

        return items[index] if 0 <= index < len(items) else None

    return collection.get(code)


def create_error_response(message: str, status: int) -> Response:
    """
    Сформировать ответ об ошибке запроса.
    """
    return Response(message, status=status, content_type="text/plain; charset=utf-8")


def resolve_entity(type_value: str, code: str):
    """
    Проверить тип сущности и код, найти сущность.
    Возвращает кортеж (сущность, ответ об ошибке); ровно одно из значений не None.
    """
    if not type_value:
        return None, create_error_response(
            "Не указан тип сущности (рецепт, номенклатура, единица измерения)", 400,
        )

    entity_type = ENTITY_TYPES.get(type_value.lower())
    if entity_type is None:
        return None, create_error_response(
            f"Указанный тип сущности '{type_value}' не поддерживается", 400,
        )

    if not code:
        return None, create_error_response("Не указан код сущности", 400)

    entity = find_entity(entity_type, code)
    if entity is None:
        return None, create_error_response(
            f"Сущность '{entity_type}' с кодом '{code}' не найдена", 404,
        )

    return entity, None


def create_report_response(report, entity) -> Response:
    """
    Сформировать HTTP ответ с отчетом по сущности.
    MIME-тип, способ отдачи (файлом/текстом) и расширение файла
    определяются самим отчетом (наследником abstract_report).
    """
    result = report.build(entity)

    if report.is_download:
        file_name = f"report.{report.file_extension}"

        return Response(
            bytes(result.binary),
            status=200,
            content_type=report.content_type,
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

    return Response(
        result.text,
        status=200,
        content_type=report.content_type,
    )


def handle_get_report(format_value: str, type_value: str, code: str) -> Response:
    """
    Сформировать ответ endpoint формирования отчета (общая логика для query и path).
    """
    entity, error = resolve_entity(type_value, code)
    if error is not None:
        return error

    # Формат отчета: явный параметр либо формат из настроек
    try:
        if format_value:
            report_type = settings_manager.convert_report_type(format_value)
        else:
            report_type = factory.settings.response_format

        report = factory.create(report_type)
    except argument_exception:
        return create_error_response(f"Указанный формат '{format_value}' не поддерживается", 400)

    return create_report_response(report, entity)


def handle_get_report_default(type_value: str, code: str) -> Response:
    """
    Сформировать ответ endpoint отчета в формате из настроек (общая логика для query и path).
    """
    entity, error = resolve_entity(type_value, code)
    if error is not None:
        return error

    try:
        report = factory.create_default()
    except argument_exception:
        return create_error_response("Формат отчета, заданный в настройках, не поддерживается", 400)

    return create_report_response(report, entity)


@app.route("/")
def index():
    """
    Корневой маршрут - справка по API.
    """
    return Response(
        "API формирования отчетов. "
        "Примеры запросов: "
        "/api/get_report/xml/recipe/0, "
        "/api/get_report?format=markdown&type=recipe&code=0, "
        "/api/get_report_default/recipe/0",
        status=200,
        content_type="text/plain; charset=utf-8",
    )


@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    GET endpoint формирования отчета по параметрам запроса.

    Параметры запроса:
        format - формат отчета (txt, csv, markdown, xml, html, rtf);
                 если не указан - формат из настроек приложения
        type   - тип сущности (рецепт, номенклатура, единица измерения)
        code   - код сущности: позиция (0, 1, 2 ...) или полный код (UUID)

    Для markdown и csv отчет формируется в виде бинарных данных и скачивается файлом,
    для остальных форматов возвращается структурированный текст.
    """
    return handle_get_report(
        (request.args.get("format") or "").strip(),
        (request.args.get("type") or "").strip(),
        (request.args.get("code") or "").strip(),
    )


@app.route("/api/get_report/<format_value>/<type_value>/<code>", methods=["GET"])
def get_report_by_path(format_value: str, type_value: str, code: str):
    """
    GET endpoint формирования отчета по параметрам пути.
    Пример: /api/get_report/xml/recipe/0

    Форматы: txt, csv, markdown, xml, html, rtf.
    Типы: рецепт / recipe, номенклатура / nomenclature, единица измерения / unit.
    Код: позиция сущности (0, 1, 2 ...) или полный код (UUID).
    """
    return handle_get_report(format_value.strip(), type_value.strip(), code.strip())


@app.route("/api/get_report_default", methods=["GET"])
def get_report_default():
    """
    GET endpoint формирования отчета в формате из настроек приложения (create_default)
    по параметрам запроса.

    Параметры запроса:
        type - тип сущности (рецепт, номенклатура, единица измерения)
        code - код сущности: позиция (0, 1, 2 ...) или полный код (UUID)

    Формат отчета определяется настройками (settings.response_format) через report_factory.create_default.
    """
    return handle_get_report_default(
        (request.args.get("type") or "").strip(),
        (request.args.get("code") or "").strip(),
    )


@app.route("/api/get_report_default/<type_value>/<code>", methods=["GET"])
def get_report_default_by_path(type_value: str, code: str):
    """
    GET endpoint формирования отчета в формате из настроек по параметрам пути.
    Пример: /api/get_report_default/recipe/0
    """
    return handle_get_report_default(type_value.strip(), code.strip())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
