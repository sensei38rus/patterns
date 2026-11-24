from Src.Core.validator import validator

"""
Строка оборотно-сальдовой ведомости (ОСВ)
"""
class osv_row_dto:
    # Тип доменной сущности
    __entity: str = ""

    # Уникальный код сущности
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # Сальдо на начало, дебет
    __opening_debit: float = 0.0

    # Сальдо на начало, кредит
    __opening_credit: float = 0.0

    # Оборот за период, дебет
    __turnover_debit: float = 0.0

    # Оборот за период, кредит
    __turnover_credit: float = 0.0

    # Сальдо на конец, дебет
    __closing_debit: float = 0.0

    # Сальдо на конец, кредит
    __closing_credit: float = 0.0

    """
    Тип доменной сущности
    """
    @property
    def entity(self) -> str:
        return self.__entity

    @entity.setter
    def entity(self, value: str) -> None:
        validator.validate(value, str)
        self.__entity = value.strip()

    """
    Уникальный код сущности
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        validator.validate(value, str)
        self.__unique_code = value.strip()

    """
    Наименование
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value is None:
            self.__name = ""
            return
        self.__name = str(value).strip()

    """
    Сальдо на начало, дебет
    """
    @property
    def opening_debit(self) -> float:
        return self.__opening_debit

    @opening_debit.setter
    def opening_debit(self, value) -> None:
        self.__opening_debit = float(value)

    """
    Сальдо на начало, кредит
    """
    @property
    def opening_credit(self) -> float:
        return self.__opening_credit

    @opening_credit.setter
    def opening_credit(self, value) -> None:
        self.__opening_credit = float(value)

    """
    Оборот за период, дебет
    """
    @property
    def turnover_debit(self) -> float:
        return self.__turnover_debit

    @turnover_debit.setter
    def turnover_debit(self, value) -> None:
        self.__turnover_debit = float(value)

    """
    Оборот за период, кредит
    """
    @property
    def turnover_credit(self) -> float:
        return self.__turnover_credit

    @turnover_credit.setter
    def turnover_credit(self, value) -> None:
        self.__turnover_credit = float(value)

    """
    Сальдо на конец, дебет
    """
    @property
    def closing_debit(self) -> float:
        return self.__closing_debit

    @closing_debit.setter
    def closing_debit(self, value) -> None:
        self.__closing_debit = float(value)

    """
    Сальдо на конец, кредит
    """
    @property
    def closing_credit(self) -> float:
        return self.__closing_credit

    @closing_credit.setter
    def closing_credit(self, value) -> None:
        self.__closing_credit = float(value)

    """
    Пересчитать сальдо на конец по формуле:
    конечное = начальное + оборот Дт - оборот Кт (в сторону Дт или Кт)
    """
    def refresh_closing(self) -> None:
        debit = self.__opening_debit + self.__turnover_debit - self.__turnover_credit
        credit = self.__opening_credit + self.__turnover_credit - self.__turnover_debit
        self.__closing_debit = max(0.0, debit)
        self.__closing_credit = max(0.0, credit)

    """
    Представление строки в виде словаря (для Json)
    """
    def to_dict(self) -> dict:
        return {
            "entity": self.__entity,
            "unique_code": self.__unique_code,
            "name": self.__name,
            "opening_debit": self.__opening_debit,
            "opening_credit": self.__opening_credit,
            "turnover_debit": self.__turnover_debit,
            "turnover_credit": self.__turnover_credit,
            "closing_debit": self.__closing_debit,
            "closing_credit": self.__closing_credit,
        }

    """
    Создать копию строки
    """
    def clone(self) -> "osv_row_dto":
        row = osv_row_dto()
        row.entity = self.__entity
        row.unique_code = self.__unique_code
        row.name = self.__name
        row.opening_debit = self.__opening_debit
        row.opening_credit = self.__opening_credit
        row.turnover_debit = self.__turnover_debit
        row.turnover_credit = self.__turnover_credit
        row.closing_debit = self.__closing_debit
        row.closing_credit = self.__closing_credit
        return row
