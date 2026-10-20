from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder

"""
Реализация текстового представления отчета
"""
class text_report(abstract_report):

    @property
    def content_type(self) -> str:
        """
        MIME-тип содержимого текстового отчета.
        """
        return "text/plain; charset=utf-8"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        table = report_source_builder.build(source)

        header = " | ".join(title for key, title in table.columns)
        data = ""

        for row in table.rows:
            data += "\n" + " | ".join(row[key] for key in table.keys)

        result = report_result_dto()
        result.text = f"{header}{data}"

        return result


TextReport = text_report
