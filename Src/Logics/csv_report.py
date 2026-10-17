from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder

"""
Реализация отчета в формате CSV
"""
class csv_report(abstract_report):

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        table = report_source_builder.build(source)

        header = ",".join(self.__escape(title) for key, title in table.columns)
        data = ""

        for row in table.rows:
            data += "\n" + ",".join(self.__escape(row[key]) for key in table.keys)

        result = report_result_dto()
        result.text = f"{header}{data}"

        return result

    @staticmethod
    def __escape(value) -> str:
        """
        Экранирование значения по правилам CSV: значения с разделителями
        или кавычками заключаются в кавычки, внутренние кавычки удваиваются.
        """
        text = str(value)

        if any(symbol in text for symbol in (",", '"', "\n", "\r")):
            return f'"{text.replace(chr(34), chr(34) * 2)}"'

        return text


CsvReport = csv_report
