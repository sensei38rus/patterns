import main
from Src.Logics.markdown_report import markdown_report


def __create_client():
    """
    Вспомогательный метод: тестовый клиент Flask.
    """
    main.app.config["TESTING"] = True
    return main.app.test_client()


def __first_recipe_code() -> str:
    """
    Вспомогательный метод: код первого рецепта из менеджера приложения.
    """
    return next(iter(main.recipes.recipes.values())).id


def __first_nomenclature_code() -> str:
    """
    Вспомогательный метод: код первой позиции номенклатуры из менеджера приложения.
    """
    return next(iter(main.storage.nomenclatures.values())).id


def __first_unit_code() -> str:
    """
    Вспомогательный метод: код первой единицы измерения из менеджера приложения.
    """
    return next(iter(main.storage.ranges.values())).id


def test_success_api_index():
    client = __create_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "API" in response.get_data(as_text=True)


def test_success_api_get_report_recipe_markdown():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "markdown", "type": "recipe", "code": __first_recipe_code()},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "text/markdown; charset=utf-8"
    assert response.headers["Content-Disposition"] == 'attachment; filename="report.md"'
    assert "| Код | Наименование | Брутто | Нетто |" in data
    assert "| --- | --- | --- | --- |" in data


def test_success_api_get_report_recipe_xml():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "xml", "type": "рецепт", "code": __first_recipe_code()},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "application/xml; charset=utf-8"
    assert "Content-Disposition" not in response.headers
    assert data.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<recipe " in data


def test_success_api_get_report_nomenclature_text():
    client = __create_client()
    nomenclature = next(iter(main.storage.nomenclatures.values()))

    response = client.get(
        "/api/get_report",
        query_string={"format": "txt", "type": "nomenclature", "code": nomenclature.id},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Content-Disposition" not in response.headers
    assert "Код | Наименование | Группа | Единица измерения" in data
    assert nomenclature.name in data
    assert nomenclature.group.name in data


def test_success_api_get_report_nomenclature_csv_by_russian_type():
    client = __create_client()
    nomenclature = next(iter(main.storage.nomenclatures.values()))

    response = client.get(
        "/api/get_report",
        query_string={"format": "csv", "type": "номенклатура", "code": nomenclature.id},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "text/csv; charset=utf-8"
    assert response.headers["Content-Disposition"] == 'attachment; filename="report.csv"'
    assert data.startswith("Код,Наименование,Группа,Единица измерения")


def test_success_api_get_report_download_is_binary_utf8():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "csv", "type": "recipe", "code": __first_recipe_code()},
    )

    raw = response.get_data()
    assert response.status_code == 200
    assert isinstance(raw, bytes)
    assert len(raw) > 0
    assert raw.decode("utf-8").startswith("Код,Наименование,Брутто,Нетто")


def test_success_api_get_report_unit_html():
    client = __create_client()
    unit = next(iter(main.storage.ranges.values()))

    response = client.get(
        "/api/get_report",
        query_string={"format": "html", "type": "единица измерения", "code": unit.id},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"
    assert data.startswith("<table>")
    assert unit.name in data


def test_success_api_get_report_default_format_from_settings():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"type": "recipe", "code": __first_recipe_code()},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"
    assert "<table>" in data


def test_fail_api_get_report_unknown_format():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "unknown", "type": "recipe", "code": __first_recipe_code()},
    )

    assert response.status_code == 400


def test_fail_api_get_report_unknown_type():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "txt", "type": "склад", "code": __first_recipe_code()},
    )

    assert response.status_code == 400


def test_fail_api_get_report_missing_type():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "txt", "code": __first_recipe_code()},
    )

    assert response.status_code == 400


def test_fail_api_get_report_missing_code():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "txt", "type": "recipe"},
    )

    assert response.status_code == 400


def test_fail_api_get_report_unknown_code():
    client = __create_client()

    response = client.get(
        "/api/get_report",
        query_string={"format": "txt", "type": "recipe", "code": "00000000-0000-0000-0000-000000000000"},
    )

    assert response.status_code == 404


def test_success_api_get_report_default_recipe():
    client = __create_client()

    response = client.get(
        "/api/get_report_default",
        query_string={"type": "recipe", "code": __first_recipe_code()},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"
    assert "Content-Disposition" not in response.headers
    assert "<table>" in data


def test_success_api_get_report_default_nomenclature_by_russian_type():
    client = __create_client()
    nomenclature = next(iter(main.storage.nomenclatures.values()))

    response = client.get(
        "/api/get_report_default",
        query_string={"type": "номенклатура", "code": nomenclature.id},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<table>" in data
    assert nomenclature.name in data
    assert nomenclature.group.name in data


def test_success_api_get_report_default_unit():
    client = __create_client()
    unit = next(iter(main.storage.ranges.values()))

    response = client.get(
        "/api/get_report_default",
        query_string={"type": "единица измерения", "code": unit.id},
    )

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<table>" in data
    assert unit.name in data


def test_success_api_get_report_default_download_markdown_from_settings():
    client = __create_client()
    original_format = main.factory.settings.response_format

    try:
        main.factory.settings.response_format = "markdown"

        response = client.get(
            "/api/get_report_default",
            query_string={"type": "recipe", "code": __first_recipe_code()},
        )

        data = response.get_data(as_text=True)
        assert response.status_code == 200
        assert response.content_type == "text/markdown; charset=utf-8"
        assert response.headers["Content-Disposition"] == 'attachment; filename="report.md"'
        assert "| --- | --- | --- | --- |" in data
    finally:
        main.factory.settings.response_format = original_format


def test_fail_api_get_report_default_missing_type():
    client = __create_client()

    response = client.get(
        "/api/get_report_default",
        query_string={"code": __first_recipe_code()},
    )

    assert response.status_code == 400


def test_fail_api_get_report_default_missing_code():
    client = __create_client()

    response = client.get(
        "/api/get_report_default",
        query_string={"type": "recipe"},
    )

    assert response.status_code == 400


def test_fail_api_get_report_default_unknown_code():
    client = __create_client()

    response = client.get(
        "/api/get_report_default",
        query_string={"type": "recipe", "code": "00000000-0000-0000-0000-000000000000"},
    )

    assert response.status_code == 404


def test_success_api_get_report_by_path_xml_recipe():
    client = __create_client()

    response = client.get("/api/get_report/xml/recipe/0")

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "application/xml; charset=utf-8"
    assert data.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<recipe " in data


def test_success_api_get_report_by_path_markdown_recipe_second():
    client = __create_client()
    second_recipe = list(main.recipes.recipes.values())[1]
    expected = bytes(markdown_report().build(second_recipe).binary).decode("utf-8")

    response = client.get("/api/get_report/markdown/recipe/1")

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == 'attachment; filename="report.md"'
    assert data == expected


def test_success_api_get_report_by_path_txt_unit():
    client = __create_client()

    response = client.get("/api/get_report/txt/unit/0")

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Код | Наименование | Коэффициент | Базовая единица" in data


def test_success_api_get_report_by_path_with_full_code():
    client = __create_client()
    recipe_code = __first_recipe_code()

    response = client.get(f"/api/get_report/txt/recipe/{recipe_code}")

    assert response.status_code == 200


def test_success_api_get_report_default_by_path():
    client = __create_client()

    response = client.get("/api/get_report_default/recipe/0")

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"
    assert "<table>" in data


def test_fail_api_get_report_by_path_unknown_format():
    client = __create_client()

    response = client.get("/api/get_report/bad/recipe/0")

    assert response.status_code == 400


def test_fail_api_get_report_by_path_unknown_type():
    client = __create_client()

    response = client.get("/api/get_report/txt/склад/0")

    assert response.status_code == 400


def test_fail_api_get_report_by_path_unknown_index():
    client = __create_client()

    response = client.get("/api/get_report/txt/recipe/99")

    assert response.status_code == 404
