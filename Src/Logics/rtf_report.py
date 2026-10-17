from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model

"""
Реализация отчета по рецепту в формате RTF
"""
class rtf_report(abstract_report):

    # Заголовок и шрифт RTF документа
    __rtf_header:str = "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0 Calibri;}}"
    __font_settings:str = "\\f0\\fs22 "
    __paragraph_break:str = "\\par"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        validator.validate(source, recipe_model)

        header = self.__escape("Код | Наименование | Брутто | Нетто")
        data = ""

        for item in source.items:
            code = self.__escape(item.unique_code)
            name = self.__escape(item.nomenclature.name)
            data += f"\n{code} | {name} | {item.quantity} | {item.weight}{self.__paragraph_break}"

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
