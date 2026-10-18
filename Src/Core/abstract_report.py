from abc import ABC, abstractmethod
from Src.Dtos.report_result_dto import report_result_dto


"""
Абстрактный класс для формирования отчета
"""
class abstract_report(ABC):
    """
    Базовый абстрактный класс стратегии/компонента формирования отчета.
    Каждый наследник знает свой MIME-тип и способ отдачи результата (текстом или файлом).
    """

    @abstractmethod
    def build(self, source) -> report_result_dto:
        """
        Сформировать отчет по переданному источнику данных.
        :param source: Доменная модель-источник данных для отчета
        :return: Экземпляр report_result_dto с результатом
        """
        pass

    @property
    @abstractmethod
    def content_type(self) -> str:
        """
        MIME-тип содержимого отчета (Content-Type HTTP ответа).
        """
        pass

    @property
    def file_extension(self) -> str:
        """
        Расширение файла отчета.
        Пустая строка, если отчет отдаётся текстом, а не скачивается файлом.
        """
        return ""

    @property
    def is_download(self) -> bool:
        """
        Флаг: отчет формируется в бинарном виде и скачивается файлом.
        """
        return self.file_extension != ""


AbstractReport = abstract_report