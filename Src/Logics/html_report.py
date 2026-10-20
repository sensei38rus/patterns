from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder

"""
Реализация отчета в формате HTML
"""
class html_report(abstract_report):

    @property
    def content_type(self) -> str:
        """
        MIME-тип содержимого HTML-отчета.
        """
        return "text/html; charset=utf-8"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        table = report_source_builder.build(source)

        header = "\n    <tr>" + "".join(
            f"<th>{self.__escape(title)}</th>" for key, title in table.columns
        ) + "</tr>"

        data = ""

        for row in table.rows:
            data += "\n    <tr>" + "".join(
                f"<td>{self.__escape(row[key])}</td>" for key in table.keys
            ) + "</tr>"

        result = report_result_dto()
        result.text = (
            "<table>\n"
            "  <thead>"
            f"{header}\n"
            "  </thead>\n"
            "  <tbody>"
            f"{data}\n"
            "  </tbody>\n"
            "</table>"
        )

        return result

    @staticmethod
    def __escape(value) -> str:
        """
        Экранирование специальных символов HTML.
        """
        return (str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


HtmlReport = html_report
