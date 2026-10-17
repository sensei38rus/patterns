from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model

"""
Реализация отчета по рецепту в формате Markdown
"""
class markdown_report(abstract_report):

    # Заголовок таблицы и разделитель колонок
    __header:str = "| Код | Наименование | Брутто | Нетто |"
    __separator:str = "| --- | --- | --- | --- |"

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source) -> report_result_dto:
        validator.validate(source, recipe_model)

        data = ""

        for item in source.items:
            code = self.__escape(item.unique_code)
            name = self.__escape(item.nomenclature.name)
            data += f"\n| {code} | {name} | {item.quantity} | {item.weight} |"

        result = report_result_dto()
        result.text = f"{self.__header}\n{self.__separator}{data}"

        return result

    @staticmethod
    def __escape(value) -> str:
        """
        Экранирование специальных символов ячейки таблицы Markdown.
        """
        return str(value).replace("\\", "\\\\").replace("|", "\\|")


MarkdownReport = markdown_report
