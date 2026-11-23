from datetime import date, datetime
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator, argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.osv_dto import osv_dto
from Src.Dtos.osv_row_dto import osv_row_dto
from Src.Logics.filter_prototype import filter_prototype
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model

"""
Сервис оборотно-сальдовой ведомости (ОСВ).
Поток построения:
1) исходные данные берутся из менеджера хранилища;
2) определяется дата начала периода и вычисляются начальные остатки;
3) на исходные данные натравливается универсальный прототип
   фильтрации (filter_prototype) — получается отбор строк;
4) по отфильтрованным данным считаются движения (приход, расход);
5) формируется DTO ведомости и выполняется сериализация (to_dict).
Сам прототип ОСВ не нужен: прототип один и он универсальный
"""
class osv_service:

    """
    Построить ОСВ по условию фильтрации.
    manager — менеджер хранилища (источник исходных данных);
    condition — условие отбора (entity обязателен);
    date_from — дата начала периода для начальных остатков (опционально)
    """
    @staticmethod
    def build(manager, condition: filter_dto, date_from=None) -> osv_dto:
        if manager is None or not hasattr(manager, "data"):
            raise argument_exception("Ожидается менеджер хранилища!")
        if not isinstance(condition, filter_dto):
            raise argument_exception("Ожидается условие фильтрации filter_dto!")

        entity = condition.entity
        if not entity:
            raise argument_exception("Условие фильтрации должно содержать entity!")
        if entity not in manager.data:
            raise argument_exception(f"Неизвестная доменная сущность {entity}!")

        # Шаг 1: исходные данные из менеджера
        items = manager.data[entity]

        # Шаг 2: дата начала и начальные остатки
        opening = osv_service.__opening_balances(entity, date_from)

        # Шаг 3: отбор строк универсальным прототипом фильтрации
        filtered = osv_service.__select(items, condition)

        # Шаг 4: движения (приход, расход) по отфильтрованным данным
        rows = [
            osv_service.__movement(item, opening.get(item.unique_code))
            for item in filtered
            if isinstance(item, abstact_model)
        ]

        # Шаг 5: сборка DTO ведомости
        report = osv_dto()
        report.entity = entity
        for row in rows:
            report.add_row(row)
        report.refresh_totals()

        return report

    """
    Начальные остатки на дату начала периода.
    Реестр остатков по датам в системе не ведется:
    пока возвращается пустой набор (остатки равны нулю).
    date_from зарезервирован для отбора периода
    """
    @staticmethod
    def __opening_balances(entity: str, date_from=None) -> dict:
        if date_from is not None and not isinstance(date_from, (date, datetime)):
            raise argument_exception("Некорректная дата начала периода!")

        return {}

    """
    Отобрать строки условием фильтрации через прототип.
    При пустом условии (нет field/value) возвращаются исходные данные
    """
    @staticmethod
    def __select(items: list, condition: filter_dto) -> list:
        if condition.field and condition.value:
            return filter_prototype(condition).apply(items)

        return list(items)

    """
    Сформировать строку ОСВ: начальные остатки + движения.
    Движения берутся из показателей модели:
    - рецепт: приход = брутто, расход = нетто;
    - единица измерения: приход = коэффициент пересчета;
    - номенклатура: приход = коэффициент единицы измерения;
    - группа: движения отсутствуют
    """
    @staticmethod
    def __movement(item: abstact_model, opening=None) -> osv_row_dto:
        row = osv_row_dto()
        row.entity = type(item).__name__
        row.unique_code = item.unique_code
        row.name = str(getattr(item, "name", "") or "")

        # Начальные остатки (сейчас всегда нулевые — реестра нет)
        row.opening_debit = float(opening[0]) if opening else 0.0
        row.opening_credit = float(opening[1]) if opening else 0.0

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
