from Src.Core.exception import argument_exception
from Src.Dtos.report_table_dto import report_table_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model

"""
Преобразование доменных сущностей в нейтральную табличную структуру для отчетов
"""
class report_source_builder:
    """
    Преобразует поддерживаемые сущности (рецепт, номенклатура, единица измерения)
    в нейтральную табличную структуру report_table_dto, форматируемую отчетами.
    """

    @staticmethod
    def build(source) -> report_table_dto:
        """
        Построить табличное представление сущности.
        :param source: recipe_model / nomenclature_model / range_model
        :return: report_table_dto с колонками и строками
        """
        if isinstance(source, recipe_model):
            return report_source_builder.__build_recipe(source)

        if isinstance(source, nomenclature_model):
            return report_source_builder.__build_nomenclature(source)

        if isinstance(source, range_model):
            return report_source_builder.__build_range(source)

        raise argument_exception("source", f"Тип источника {type(source).__name__} не поддерживается отчетами!")

    @staticmethod
    def __build_recipe(source: recipe_model) -> report_table_dto:
        """
        Табличное представление технологической карты (состав ингредиентов).
        """
        result = report_table_dto(
            tag="recipe",
            title=source.name,
            attributes={
                "cooking_time": str(source.cooking_time),
                "portions": str(source.portions),
            },
            columns=[
                ("code", "Код"),
                ("name", "Наименование"),
                ("quantity", "Брутто"),
                ("weight", "Нетто"),
            ],
        )

        for item in source.items:
            result.rows.append({
                "code": str(item.unique_code),
                "name": str(item.nomenclature.name),
                "quantity": str(item.quantity),
                "weight": str(item.weight),
            })

        return result

    @staticmethod
    def __build_nomenclature(source: nomenclature_model) -> report_table_dto:
        """
        Табличное представление позиции номенклатуры.
        """
        return report_table_dto(
            tag="nomenclature",
            title=source.name,
            attributes={"full_name": str(source.full_name)},
            columns=[
                ("code", "Код"),
                ("name", "Наименование"),
                ("group", "Группа"),
                ("unit", "Единица измерения"),
            ],
            rows=[{
                "code": str(source.unique_code),
                "name": str(source.name),
                "group": str(source.group.name) if source.group else "",
                "unit": str(source.range.name) if source.range else "",
            }],
        )

    @staticmethod
    def __build_range(source: range_model) -> report_table_dto:
        """
        Табличное представление единицы измерения.
        """
        return report_table_dto(
            tag="unit",
            title=source.name,
            attributes={"conversion_factor": str(source.conversion_factor)},
            columns=[
                ("code", "Код"),
                ("name", "Наименование"),
                ("factor", "Коэффициент"),
                ("base", "Базовая единица"),
            ],
            rows=[{
                "code": str(source.unique_code),
                "name": str(source.name),
                "factor": str(source.conversion_factor),
                "base": str(source.base.name) if source.base else "",
            }],
        )


ReportSourceBuilder = report_source_builder
