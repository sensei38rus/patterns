import pytest
from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.exception import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_dto import report_type_dto, ReportTypeEnum
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.csv_report import csv_report, CsvReport
from Src.Logics.html_report import html_report, HtmlReport
from Src.Logics.markdown_report import markdown_report, MarkdownReport
from Src.Logics.report_factory import report_factory, ReportFactory
from Src.Logics.rtf_report import rtf_report, RtfReport
from Src.Logics.text_report import text_report, TextReport
from Src.Logics.xml_report import xml_report, XmlReport
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.settings_model import settings_model


def __create_sample_recipe() -> recipe_model:
    """
    Вспомогательный метод: сформировать технологическую карту с двумя ингредиентами.
    """
    group = nomenclature_group_model.create_grocery()
    gram = range_model.create_gram()
    flour = nomenclature_model.create_flour(group, gram)
    sugar = nomenclature_model.create_sugar(group, gram)

    recipe = recipe_model("Блинчики классические", 10, 1)
    recipe.add_item(recipe_item_model.create(flour, 100.0, gram))
    recipe.add_item(recipe_item_model.create(sugar, 20.0, gram))

    return recipe


def __get_report_text(result: report_result_dto) -> str:
    """
    Вспомогательный метод: содержимое отчета в виде текста (текстовое или бинарное поле).
    """
    if result.binary:
        return bytes(result.binary).decode("utf-8")

    return result.text


def test_success_report_factory_create_text_report():
    """
    
    Проверка успешного создания инстанса текстового отчета через абстрактную фабрику.
   
    """
    # Arrange
    factory = report_factory()

    # Act
    report = factory.create(report_type_dto.TXT)

    # Assert
    assert report is not None
    assert isinstance(report, abstract_report)
    assert isinstance(report, text_report)


def test_fail_report_factory_create_unsupported_type_raises_argument_exception():
    """
    
    Проверка выброса исключения при попытке запросить нереализованный тип отчета.
    
    """
    # Arrange
    factory = report_factory()

    # Act & Assert
    with pytest.raises(argument_exception):
        factory.create("UNSUPPORTED_TYPE")

    with pytest.raises(argument_exception):
        factory.create(None)


def test_success_full_chain_report_factory_build_recipe():
    """
    
    Сквозной тест генерации отчета по рецепту через фабрику отчетов.
   
    """
    # Arrange
    factory = report_factory()
    group = nomenclature_group_model.create_grocery()
    gram = range_model.create_gram()
    flour = nomenclature_model.create_flour(group, gram)
    sugar = nomenclature_model.create_sugar(group, gram)

    recipe = recipe_model("Блинчики классические", 10, 1)
    row_flour = recipe_item_model.create(flour, 100.0, gram)
    row_sugar = recipe_item_model.create(sugar, 20.0, gram)
    recipe.add_item(row_flour)
    recipe.add_item(row_sugar)

    # Act
    report = factory.create(report_type_dto.TXT)
    result = report.build(recipe)

    # Assert
    assert result is not None
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert "Код | Наименование | Брутто | Нетто" in result.text
    assert f"{row_flour.unique_code} | Мука пшеничная | 100.0 | 100.0" in result.text
    assert f"{row_sugar.unique_code} | Сахар | 20.0 | 20.0" in result.text


def test_success_report_factory_create_by_full_enum_and_name():
    """
   
    Проверка, что фабрика принимает тип из Src.Dtos.report_type_enum и строковое имя формата.
   
    """
    # Arrange
    factory = report_factory()

    # Act
    report_by_enum = factory.create(report_type_enum.TXT)
    report_by_name = factory.create("TEXT")

    # Assert
    assert isinstance(report_by_enum, text_report)
    assert isinstance(report_by_name, text_report)


def test_success_report_factory_settings_encapsulated():
    """
    
    Проверка инкапсуляции настроек в фабрике: через конструктор и через свойство settings.
   
    """
    # Arrange
    settings = settings_model()
    settings.response_format = report_type_enum.TXT

    # Act
    factory = report_factory(settings)

    # Assert
    assert factory.settings is settings
    assert factory.settings.response_format == report_type_enum.TXT

    new_settings = settings_model()
    factory.settings = new_settings
    assert factory.settings is new_settings

    with pytest.raises(argument_exception):
        factory.settings = "NOT_SETTINGS"


def test_success_report_factory_create_default_text_report():
    """
    
    Проверка создания отчета по умолчанию в формате из настроек.
   
    """
    # Arrange
    settings = settings_model()
    settings.response_format = report_type_enum.TXT
    factory = report_factory(settings)

    # Act
    report = factory.create_default()

    # Assert
    assert report is not None
    assert isinstance(report, abstract_report)
    assert isinstance(report, text_report)


def test_success_report_factory_create_all_supported_formats():
    """
   
    Проверка подключения всех поддерживаемых форматов в фабрику отчетов.
    
    """
    # Arrange
    factory = report_factory()
    expected = {
        report_type_enum.TXT: text_report,
        report_type_enum.CSV: csv_report,
        report_type_enum.MARKDOWN: markdown_report,
        report_type_enum.XML: xml_report,
        report_type_enum.HTML: html_report,
        report_type_enum.RTF: rtf_report,
    }

    # Act & Assert
    for report_type, report_class in expected.items():
        report = factory.create(report_type)
        assert isinstance(report, abstract_report)
        assert isinstance(report, report_class)


def test_success_report_factory_create_default_html_report():
    """
    
    Проверка создания отчета по умолчанию в формате из настроек (HTML по умолчанию).
    
    """
    # Arrange
    factory = report_factory(settings_model())

    # Act
    report = factory.create_default()

    # Assert
    assert report is not None
    assert isinstance(report, abstract_report)
    assert isinstance(report, html_report)


def test_success_markdown_report_build():
    """
    Проверка формирования отчета в формате Markdown (бинарные данные).
    """
    # Arrange
    recipe = __create_sample_recipe()
    report = markdown_report()

    # Act
    result = report.build(recipe)

    # Assert
    assert isinstance(result, report_result_dto)
    assert result.text == ""
    assert len(result.binary) > 0

    content = __get_report_text(result)
    assert "| Код | Наименование | Брутто | Нетто |" in content
    assert "| --- | --- | --- | --- |" in content
    assert f"| {recipe.items[0].unique_code} | Мука пшеничная | 100.0 | 100.0 |" in content
    assert f"| {recipe.items[1].unique_code} | Сахар | 20.0 | 20.0 |" in content


def test_success_csv_report_build():
    """
    Проверка формирования отчета в формате CSV (бинарные данные).
    """
    # Arrange
    recipe = __create_sample_recipe()
    report = csv_report()

    # Act
    result = report.build(recipe)

    # Assert
    assert isinstance(result, report_result_dto)
    assert result.text == ""
    assert len(result.binary) > 0

    content = __get_report_text(result)
    assert content.startswith("Код,Наименование,Брутто,Нетто")
    assert f"{recipe.items[0].unique_code},Мука пшеничная,100.0,100.0" in content
    assert f"{recipe.items[1].unique_code},Сахар,20.0,20.0" in content


def test_success_xml_report_build():
    """
    Проверка формирования отчета в формате XML.
    """
    # Arrange
    recipe = __create_sample_recipe()
    report = xml_report()

    # Act
    result = report.build(recipe)

    # Assert
    assert isinstance(result, report_result_dto)
    assert result.text.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert '<recipe name="Блинчики классические" cooking_time="10" portions="1">' in result.text
    assert f'<item code="{recipe.items[0].unique_code}" name="Мука пшеничная" quantity="100.0" weight="100.0" />' in result.text
    assert result.text.endswith("</recipe>")


def test_success_html_report_build():
    """
    Проверка формирования отчета в формате HTML.
    """
    # Arrange
    recipe = __create_sample_recipe()
    report = html_report()

    # Act
    result = report.build(recipe)

    # Assert
    assert isinstance(result, report_result_dto)
    assert result.text.startswith("<table>")
    assert "<th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th>" in result.text
    assert f"<td>{recipe.items[0].unique_code}</td><td>Мука пшеничная</td><td>100.0</td><td>100.0</td>" in result.text
    assert result.text.endswith("</table>")


def test_success_rtf_report_build():
    """
    Проверка формирования отчета в формате RTF.
    """
    # Arrange
    recipe = __create_sample_recipe()
    report = rtf_report()

    # Act
    result = report.build(recipe)

    # Assert
    assert isinstance(result, report_result_dto)
    assert result.text.startswith("{\\rtf1\\ansi")
    assert "\\par" in result.text
    assert "Мука пшеничная" in result.text
    assert result.text.endswith("}")


def test_fail_reports_build_invalid_source_raises_argument_exception():
    """
    Проверка выброса исключения при передаче некорректного источника данных.
    """
    # Arrange
    reports = [text_report(), csv_report(), markdown_report(), xml_report(), html_report(), rtf_report()]

    # Act & Assert
    for report in reports:
        with pytest.raises(argument_exception):
            report.build("NOT_RECIPE")


def test_success_reports_build_nomenclature_in_all_formats():
    """
    Проверка формирования отчета по номенклатуре во всех форматах.
    """
    # Arrange
    group = nomenclature_group_model.create_grocery()
    gram = range_model.create_gram()
    flour = nomenclature_model.create_flour(group, gram)

    reports = [text_report(), csv_report(), markdown_report(), xml_report(), html_report(), rtf_report()]

    # Act & Assert
    for report in reports:
        result = report.build(flour)
        assert isinstance(result, report_result_dto)
        assert __get_report_text(result) != ""

    text = text_report().build(flour).text
    assert "Код | Наименование | Группа | Единица измерения" in text
    assert "Мука пшеничная" in text
    assert "Бакалея" in text

    xml = xml_report().build(flour).text
    assert "<nomenclature " in xml
    assert 'full_name="Мука пшеничная высший сорт"' in xml


def test_success_reports_build_unit_in_all_formats():
    """
    Проверка формирования отчета по единице измерения во всех форматах.
    """
    # Arrange
    kilogram = range_model.create_kilogram()

    reports = [text_report(), csv_report(), markdown_report(), xml_report(), html_report(), rtf_report()]

    # Act & Assert
    for report in reports:
        result = report.build(kilogram)
        assert isinstance(result, report_result_dto)
        assert __get_report_text(result) != ""

    text = text_report().build(kilogram).text
    assert "Код | Наименование | Коэффициент | Базовая единица" in text
    assert "килограмм" in text
    assert "1000" in text
    assert "грамм" in text

    xml = xml_report().build(kilogram).text
    assert "<unit " in xml
    assert 'conversion_factor="1000"' in xml