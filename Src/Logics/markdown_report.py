from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder

"""
Реализация отчета в формате Markdown.
Результат формируется в виде бинарных данных (кодировка UTF-8) для скачивания файла.
"""
class markdown_report(abstract_report):

    @property
    def content_type(self) -> str:
        """
        MIME-тип содержимого Markdown-отчета.
        """
        return "text/markdown; charset=utf-8"

    @property
    def file_extension(self) -> str:
        """
        Расширение файла Markdown-отчета.
        """
        return "md"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        table = report_source_builder.build(source)

        header = "| " + " | ".join(self.__escape(title) for key, title in table.columns) + " |"
        separator = "| " + " | ".join("---" for key, title in table.columns) + " |"
        data = ""

        for row in table.rows:
            data += "\n| " + " | ".join(self.__escape(row[key]) for key in table.keys) + " |"

        result = report_result_dto()
        result.binary = list(f"{header}\n{separator}{data}".encode("utf-8"))

        return result

    @staticmethod
    def __escape(value) -> str:
        """
        Экранирование специальных символов ячейки таблицы Markdown.
        """
        return str(value).replace("\\", "\\\\").replace("|", "\\|")


MarkdownReport = markdown_report
