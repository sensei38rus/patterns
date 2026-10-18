from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder

"""
Реализация отчета в формате XML
"""
class xml_report(abstract_report):

    # Заголовок XML документа
    __xml_header:str = '<?xml version="1.0" encoding="utf-8"?>'

    @property
    def content_type(self) -> str:
        """
        MIME-тип содержимого XML-отчета.
        """
        return "application/xml; charset=utf-8"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        table = report_source_builder.build(source)

        attributes = f' name="{self.__escape(table.title)}"'
        for key, value in table.attributes.items():
            attributes += f' {key}="{self.__escape(value)}"'

        data = ""

        for row in table.rows:
            row_attributes = ""
            for key in table.keys:
                row_attributes += f' {key}="{self.__escape(row[key])}"'
            data += f"\n  <item{row_attributes} />"

        result = report_result_dto()
        result.text = (
            f"{self.__xml_header}\n"
            f"<{table.tag}{attributes}>"
            f"{data}\n</{table.tag}>"
        )

        return result

    @staticmethod
    def __escape(value) -> str:
        """
        Экранирование специальных символов XML.
        """
        return (str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


XmlReport = xml_report
