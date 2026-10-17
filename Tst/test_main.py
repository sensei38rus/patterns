import main


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
