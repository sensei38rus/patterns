from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model

"""
Реализация отчета по рецепту в формате HTML
"""
class html_report(abstract_report):

    # Шапка таблицы
    __header:str = "\n    <tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        validator.validate(source, recipe_model)

        data = ""

        for item in source.items:
            code = self.__escape(item.unique_code)
            name = self.__escape(item.nomenclature.name)
            data += f"\n    <tr><td>{code}</td><td>{name}</td><td>{item.quantity}</td><td>{item.weight}</td></tr>"

        result = report_result_dto()
        result.text = (
            "<table>\n"
            "  <thead>"
            f"{self.__header}\n"
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
