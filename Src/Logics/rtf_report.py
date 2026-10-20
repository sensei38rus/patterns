from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder

"""
Реализация отчета в формате RTF
"""
class rtf_report(abstract_report):

    # Заголовок и шрифт RTF документа
    __rtf_header:str = "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0 Calibri;}}"
    __font_settings:str = "\\f0\\fs22 "
    __paragraph_break:str = "\\par"

    @property
    def content_type(self) -> str:
        """
        MIME-тип содержимого RTF-отчета.
        """
        return "application/rtf"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        table = report_source_builder.build(source)

        header = self.__escape(" | ".join(title for key, title in table.columns))
        data = ""

        for row in table.rows:
            data += "\n" + self.__escape(" | ".join(row[key] for key in table.keys)) + self.__paragraph_break

        result = report_result_dto()
        result.text = f"{self.__rtf_header}\n{self.__font_settings}{header}{self.__paragraph_break}{data}\n}}"

        return result

    @staticmethod
    def __escape(value) -> str:
        """
        Экранирование специальных символов RTF.
        """
        return (str(value)
            .replace("\\", "\\\\")
            .replace("{", "\\{")
            .replace("}", "\\}"))


RtfReport = rtf_report
