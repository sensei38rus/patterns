from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto

"""
Реализация текстового представления отчета по рецепту
"""
class text_report(abstract_report):
    # Рецепт
    __receipt:recipe_model

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        validator.validate(source, recipe_model)
        self.__receipt = source

        header = "Код | Наименование | Брутто | Нетто"
        data = ""

        for item in self.__receipt.items:
            data += f"\n{item.unique_code} | {item.nomenclature.name} | {item.quantity} | {item.weight}"

        result = report_result_dto()
        result.text = f"{header}{data}"

        return result


TextReport = text_report
