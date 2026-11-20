from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto
from Src.Models.settings_model import settings_model
from Src.Models.company_model import company_model

"""
Dto для описания настроек приложения
"""
class settings_dto(abstract_dto):
    # Код
    __unique_code: str = ""

    # Карточка организации
    __company: company_model = None

    # Наименование директора
    __boss_name: str = ""

    # Наименование главного бухгалтера
    __account_name: str = ""

    # Первый старт
    __first_start: bool = True

    # Формат отчетов по умолчанию
    __default_report_type: int = 1

    """
    Код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = value.strip()

    """
    Карточка организации
    """
    @property
    def company(self) -> company_model:
        return self.__company

    @company.setter
    def company(self, value) -> None:
        if value is None:
            self.__company = None
            return

        validator.validate(value, company_model)
        self.__company = value

    """
    Наименование директора
    """
    @property
    def boss_name(self) -> str:
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        self.__boss_name = value.strip()

    """
    Наименование главного бухгалтера
    """
    @property
    def account_name(self) -> str:
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        self.__account_name = value.strip()

    """
    Флаг. Первый старт
    """
    @property
    def first_start(self) -> bool:
        return self.__first_start

    @first_start.setter
    def first_start(self, value: bool) -> None:
        validator.validate(value, bool)
        self.__first_start = value

    """
    Формат отчетов по умолчанию
    """
    @property
    def default_report_type(self) -> int:
        return self.__default_report_type

    @default_report_type.setter
    def default_report_type(self, value) -> None:
        self.__default_report_type = int(value)

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: settings_model) -> "settings_dto":
        validator.validate(source, settings_model)

        dto = settings_dto()
        dto.unique_code = source.unique_code
        dto.company = source.company
        dto.boss_name = source.boss_name
        dto.account_name = source.account_name
        dto.first_start = source.first_start
        dto.default_report_type = source.default_report_type.value

        return dto
