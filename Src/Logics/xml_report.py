from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model

"""
Реализация отчета по рецепту в формате XML
"""
class xml_report(abstract_report):

    # Заголовок XML документа
    __xml_header:str = '<?xml version="1.0" encoding="utf-8"?>'

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        validator.validate(source, recipe_model)

        recipe_name = self.__escape(source.name)
        data = ""

        for item in source.items:
            code = self.__escape(item.unique_code)
            name = self.__escape(item.nomenclature.name)
            data += f'\n  <item code="{code}" name="{name}" quantity="{item.quantity}" weight="{item.weight}" />'

        result = report_result_dto()
        result.text = (
            f"{self.__xml_header}\n"
            f'<recipe name="{recipe_name}" cooking_time="{source.cooking_time}" portions="{source.portions}">'
            f"{data}\n</recipe>"
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
