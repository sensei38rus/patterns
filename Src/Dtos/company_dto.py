from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto

"""
Dto для описания организации
"""
class company_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # ИНН
    __inn: int = 0

    # БИК
    __bik: str = ""

    # Корреспондентский счет
    __corr_account: int = 0

    # Банковский счет
    __account: int = 0

    # Вид собственности
    __ownership: str = ""

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
    Наименование
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value.strip()

    """
    ИНН
    """
    @property
    def inn(self) -> int:
        return self.__inn

    @inn.setter
    def inn(self, value) -> None:
        self.__inn = int(value)

    """
    БИК
    """
    @property
    def bik(self) -> str:
        return self.__bik

    @bik.setter
    def bik(self, value: str) -> None:
        self.__bik = value.strip()

    """
    Корреспондентский счет
    """
    @property
    def corr_account(self) -> int:
        return self.__corr_account

    @corr_account.setter
    def corr_account(self, value) -> None:
        self.__corr_account = int(value)

    """
    Банковский счет
    """
    @property
    def account(self) -> int:
        return self.__account

    @account.setter
    def account(self, value) -> None:
        self.__account = int(value)

    """
    Вид собственности
    """
    @property
    def ownership(self) -> str:
        return self.__ownership

    @ownership.setter
    def ownership(self, value: str) -> None:
        self.__ownership = value.strip()

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: company_model) -> "company_dto":
        validator.validate(source, company_model)
        
        dto = company_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.inn = source.inn
        dto.bik = source.bik
        dto.corr_account = source.corr_account
        dto.account = source.account
        dto.ownership = source.ownership
        
        return dto