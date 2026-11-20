from Src.Dtos.osv_row_dto import osv_row_dto
from Src.Core.validator import validator, argument_exception

"""
Оборотно-сальдовая ведомость (ОСВ) с итогами по строкам
"""
class osv_dto:
    # Ключ доменной сущности
    __entity: str = ""

    # Строки ведомости
    __rows: list = None

    # Итоговое сальдо на начало, дебет
    __total_opening_debit: float = 0.0

    # Итоговое сальдо на начало, кредит
    __total_opening_credit: float = 0.0

    # Итоговый оборот, дебет
    __total_turnover_debit: float = 0.0

    # Итоговый оборот, кредит
    __total_turnover_credit: float = 0.0

    # Итоговое сальдо на конец, дебет
    __total_closing_debit: float = 0.0

    # Итоговое сальдо на конец, кредит
    __total_closing_credit: float = 0.0

    def __init__(self) -> None:
        if self.__rows is None:
            self.__rows = []

    """
    Ключ доменной сущности
    """
    @property
    def entity(self) -> str:
        return self.__entity

    @entity.setter
    def entity(self, value: str) -> None:
        validator.validate(value, str)
        self.__entity = value.strip()

    """
    Строки ведомости
    """
    @property
    def rows(self) -> list:
        return self.__rows

    @rows.setter
    def rows(self, value: list) -> None:
        if value is None:
            self.__rows = []
            return

        if not isinstance(value, list):
            raise argument_exception("Ожидается список строк ОСВ!")

        for item in value:
            if not isinstance(item, osv_row_dto):
                raise argument_exception("Ожидается osv_row_dto!")

        self.__rows = list(value)

    """
    Итоговое сальдо на начало, дебет
    """
    @property
    def total_opening_debit(self) -> float:
        return self.__total_opening_debit

    """
    Итоговое сальдо на начало, кредит
    """
    @property
    def total_opening_credit(self) -> float:
        return self.__total_opening_credit

    """
    Итоговый оборот, дебет
    """
    @property
    def total_turnover_debit(self) -> float:
        return self.__total_turnover_debit

    """
    Итоговый оборот, кредит
    """
    @property
    def total_turnover_credit(self) -> float:
        return self.__total_turnover_credit

    """
    Итоговое сальдо на конец, дебет
    """
    @property
    def total_closing_debit(self) -> float:
        return self.__total_closing_debit

    """
    Итоговое сальдо на конец, кредит
    """
    @property
    def total_closing_credit(self) -> float:
        return self.__total_closing_credit

    """
    Добавить строку ведомости
    """
    def add_row(self, row: osv_row_dto) -> None:
        if not isinstance(row, osv_row_dto):
            raise argument_exception("Ожидается osv_row_dto!")

        self.__rows.append(row)

    """
    Пересчитать итоги по всем строкам
    """
    def refresh_totals(self) -> None:
        self.__total_opening_debit = 0.0
        self.__total_opening_credit = 0.0
        self.__total_turnover_debit = 0.0
        self.__total_turnover_credit = 0.0
        self.__total_closing_debit = 0.0
        self.__total_closing_credit = 0.0

        for row in self.__rows:
            self.__total_opening_debit += row.opening_debit
            self.__total_opening_credit += row.opening_credit
            self.__total_turnover_debit += row.turnover_debit
            self.__total_turnover_credit += row.turnover_credit
            self.__total_closing_debit += row.closing_debit
            self.__total_closing_credit += row.closing_credit

    """
    Представление ведомости в виде словаря (для Json)
    """
    def to_dict(self) -> dict:
        return {
            "entity": self.__entity,
            "rows": [row.to_dict() for row in self.__rows],
            "totals": {
                "opening_debit": self.__total_opening_debit,
                "opening_credit": self.__total_opening_credit,
                "turnover_debit": self.__total_turnover_debit,
                "turnover_credit": self.__total_turnover_credit,
                "closing_debit": self.__total_closing_debit,
                "closing_credit": self.__total_closing_credit,
            },
        }

    """
    Создать независимую копию ведомости
    """
    def clone(self) -> "osv_dto":
        result = osv_dto()
        result.entity = self.__entity
        result.rows = [row.clone() for row in self.__rows]
        result.refresh_totals()
        return result
