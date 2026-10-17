from flask import Flask, Response, request
from Src.Core.exception import argument_exception
from Src.Dtos.report_type_enum import report_type_enum
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

# Content-Type ответа в зависимости от формата отчета
RESPONSE_CONTENT_TYPES = {
    report_type_enum.TXT: "text/plain; charset=utf-8",
    report_type_enum.CSV: "text/csv; charset=utf-8",
    report_type_enum.MARKDOWN: "text/markdown; charset=utf-8",
    report_type_enum.XML: "application/xml; charset=utf-8",
    report_type_enum.HTML: "text/html; charset=utf-8",
    report_type_enum.RTF: "application/rtf",
}

# Форматы, для которых отчет формируется в виде бинарных данных и скачивается файлом
DOWNLOAD_REPORT_TYPES = (report_type_enum.CSV, report_type_enum.MARKDOWN)

# Расширение файла отчета для скачиваемых форматов
REPORT_FILE_EXTENSIONS = {
    report_type_enum.CSV: "csv",
    report_type_enum.MARKDOWN: "md",
}


def find_entity(entity_type: str, code: str):
    """
    Найти сущность по типу и коду (идентификатору).
    Возвращает None, если сущность не найдена.
    """
    if entity_type == "recipe":
        return recipes.get_recipe(code)

    if entity_type == "nomenclature":
        return storage.nomenclatures.get(code)

    if entity_type == "unit":
        return storage.ranges.get(code)

    return None


@app.route("/")
def index():
    """
    Корневой маршрут - справка по API.
    """
    return Response(
        "API формирования отчетов. "
        "Пример запроса: /api/get_report?format=markdown&type=recipe&code=<код сущности>",
        status=200,
        content_type="text/plain; charset=utf-8",
    )


@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    GET endpoint формирования отчета.

    Параметры запроса:
        format - формат отчета (txt, csv, markdown, xml, html, rtf);
                 если не указан - формат из настроек приложения
        type   - тип сущности (рецепт, номенклатура, единица измерения)
        code   - код (идентификатор) сущности

    Для markdown и csv отчет формируется в виде бинарных данных и скачивается файлом,
    для остальных форматов возвращается структурированный текст.
    """
    format_value = (request.args.get("format") or "").strip()
    type_value = (request.args.get("type") or "").strip()
    code = (request.args.get("code") or "").strip()

    # Тип сущности
    if not type_value:
        return Response(
            "Не указан параметр type (рецепт, номенклатура, единица измерения)",
            status=400, content_type="text/plain; charset=utf-8",
        )

    entity_type = ENTITY_TYPES.get(type_value.lower())
    if entity_type is None:
        return Response(
            f"Указанный тип сущности '{type_value}' не поддерживается",
            status=400, content_type="text/plain; charset=utf-8",
        )

    # Код сущности
    if not code:
        return Response(
            "Не указан параметр code (код сущности)",
            status=400, content_type="text/plain; charset=utf-8",
        )

    entity = find_entity(entity_type, code)
    if entity is None:
        return Response(
            f"Сущность '{entity_type}' с кодом '{code}' не найдена",
            status=404, content_type="text/plain; charset=utf-8",
        )

    # Формат отчета: явный параметр либо формат из настроек
    try:
        if format_value:
            report_type = settings_manager.convert_report_type(format_value)
        else:
            report_type = factory.settings.response_format

        report = factory.create(report_type)
    except argument_exception:
        return Response(
            f"Указанный формат '{format_value}' не поддерживается",
            status=400, content_type="text/plain; charset=utf-8",
        )

    result = report.build(entity)

    # Markdown и CSV: бинарные данные, отчет скачивается файлом
    if report_type in DOWNLOAD_REPORT_TYPES:
        file_name = f"report.{REPORT_FILE_EXTENSIONS[report_type]}"

        return Response(
            bytes(result.binary),
            status=200,
            content_type=RESPONSE_CONTENT_TYPES.get(report_type, "application/octet-stream"),
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

    # Остальные форматы: структурированный текст в теле ответа
    return Response(
        result.text,
        status=200,
        content_type=RESPONSE_CONTENT_TYPES.get(report_type, "text/plain; charset=utf-8"),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
