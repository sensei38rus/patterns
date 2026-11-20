from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.osv_dto import osv_dto
from Src.Dtos.osv_row_dto import osv_row_dto
from Src.Logics.filter_prototype import filter_prototype
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model

"""
Прототип построения оборотно-сальдовой ведомости (ОСВ).
Один прототип используется для всех DOMAIN-моделей:
номенклатура, группа, единица измерения, рецепт.
Фильтрация выполняется через filter_prototype; копия - методом clone()
"""
class osv_prototype(abstract_prototype):
    # Прототип фильтрации (условие отбора строк)
    __filter: filter_prototype = None

    """
    Конструктор.
    При отсутствии условия создается пустой filter_dto
    """
    def __init__(self, condition: filter_dto = None) -> None:
        if condition is not None and not isinstance(condition, filter_dto):
            raise argument_exception("Ожидается условие фильтрации filter_dto!")

        self.__filter = filter_prototype(condition)

    """
    Условие фильтрации
    """
    @property
    def condition(self) -> filter_dto:
        return self.__filter.condition

    @condition.setter
    def condition(self, value: filter_dto) -> None:
        self.__filter.condition = value

    """
    Задать условие фильтрации по полям.
    Возвращает текущий прототип для построения цепочки вызовов
    """
    def configure(
        self,
        entity: str,
        field: str,
        value: str,
        type: filter_type_enum = filter_type_enum.EQUALS,
    ) -> "osv_prototype":
        self.__filter.configure(entity, field, value, type)
        return self

    """
    Построить ОСВ по списку доменных сущностей.
    Строки отбираются фильтром, сальдо и обороты рассчитываются
    по показателям модели, итоги суммируются
    """
    def build(self, items: list) -> osv_dto:
        if not isinstance(items, list):
            raise argument_exception("Ожидается список данных для построения ОСВ!")

        condition = self.condition
        filtered = self.__filter.apply(items) if condition.field and condition.value else list(items)

        report = osv_dto()
        report.entity = condition.entity

        for item in filtered:
            if not isinstance(item, abstact_model):
                continue
            report.add_row(osv_prototype.__row_from(item))

        report.refresh_totals()
        return report

    """
    Создать независимую копию прототипа.
    Условие фильтрации копируется глубоко
    """
    def clone(self) -> "osv_prototype":
        return osv_prototype(self.condition)

    """
    Сформировать строку ОСВ из доменной сущности.
    Обороты берутся из показателей модели:
    - рецепт: брутто (Дт) и нетто (Кт);
    - единица измерения: коэффициент (Дт);
    - номенклатура: коэффициент единицы измерения (Дт);
    - группа: обороты отсутствуют
    """
    @staticmethod
    def __row_from(item: abstact_model) -> osv_row_dto:
        row = osv_row_dto()
        row.entity = type(item).__name__
        row.unique_code = item.unique_code
        row.name = str(getattr(item, "name", "") or "")

        # Регистр начальных остатков в системе не ведется
        row.opening_debit = 0.0
        row.opening_credit = 0.0

        if isinstance(item, receipt_model):
            row.turnover_debit = float(item.brutto)
            row.turnover_credit = float(item.netto)
        elif isinstance(item, range_model):
            row.turnover_debit = float(item.value)
            row.turnover_credit = 0.0
        elif isinstance(item, nomenclature_model) and item.range is not None:
            row.turnover_debit = float(item.range.value)
            row.turnover_credit = 0.0
        else:
            row.turnover_debit = 0.0
            row.turnover_credit = 0.0

        row.refresh_closing()
        return row
