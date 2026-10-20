from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception, operation_exception
from Src.Core.validator import validator
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.rtf_report import rtf_report
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.settings_model import settings_model

"""
Реализация фабрики для построения отчетов
"""
class report_factory(abstract_report_factory):

    # Маппинг тип отчета и его реализация
    __mapping:dict[report_type_enum, type[abstract_report]]

    # Настройки приложения, определяющие формат ответа по умолчанию
    __settings:settings_model

    def __init__(self, settings: settings_model = None):
        """
        Конструктор фабрики.

        Настройки инкапсулированы в фабрике: если явный settings не передан,
        настройки берутся из settings_manager (с ленивой загрузкой файла настроек).

        :param settings: Настройки приложения (settings_model)
        """
        self.__mapping = {}
        self.__mapping[ report_type_enum.TXT ] = text_report
        self.__mapping[ report_type_enum.CSV ] = csv_report
        self.__mapping[ report_type_enum.MARKDOWN ] = markdown_report
        self.__mapping[ report_type_enum.XML ] = xml_report
        self.__mapping[ report_type_enum.HTML ] = html_report
        self.__mapping[ report_type_enum.RTF ] = rtf_report

        if settings is None:
            settings = self.__load_settings()

        validator.validate(settings, settings_model)
        self.__settings = settings

    def create(self, report_type) -> abstract_report:
        """
        Создать отчет по переданному типу.
        Тип нормализуется через settings_manager.convert_report_type,
        поэтому поддерживаются report_type_enum, report_type_dto, имя или код формата.
        """
        report_type = settings_manager.convert_report_type(report_type)

        if report_type not in self.__mapping:
            raise argument_exception("report_type", f"Указанный тип отчета {report_type} не реализован!")

        return self.__mapping[ report_type ]()

    def create_default(self) -> abstract_report:
        """
        Создать отчет в формате, заданном в настройках (settings.response_format).
        Если формат из настроек не реализован - argument_exception.
        """
        return self.create(self.__settings.response_format)

    @property
    def settings(self) -> settings_model:
        """Настройки приложения, используемые фабрикой."""
        return self.__settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        """Задать настройки приложения."""
        validator.validate(value, settings_model)
        self.__settings = value

    @staticmethod
    def __load_settings() -> settings_model:
        """
        Получить настройки из settings_manager (singleton).
        При ошибке загрузки файла настроек возвращаются настройки по умолчанию.
        """
        manager = settings_manager()

        if not manager.is_loaded:
            try:
                manager.load()
            except operation_exception:
                pass

        return manager.settings


ReportFactory = report_factory
