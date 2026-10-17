from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model

"""
Реализация отчета по рецепту в формате CSV
"""
class csv_report(abstract_report):

    # Заголовок таблицы
    __header:str = "Код,Наименование,Брутто,Нетто"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        validator.validate(source, recipe_model)

        data = ""

        for item in source.items:
            code = self.__escape(item.unique_code)
            name = self.__escape(item.nomenclature.name)
            data += f"\n{code},{name},{item.quantity},{item.weight}"

        result = report_result_dto()
        result.text = f"{self.__header}{data}"

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
