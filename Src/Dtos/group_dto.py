from Src.Models.group_model import group_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto

"""
Dto для описания группы номенклатуры
"""
class group_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # Код группы-владельца
    __parent_code: str = ""

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
    Код группы-владельца
    """
    @property
    def parent_code(self) -> str:
        return self.__parent_code

    @parent_code.setter
    def parent_code(self, value: str) -> None:
        self.__parent_code = value.strip()

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: group_model) -> "group_dto":
        validator.validate(source, group_model)

        dto = group_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name

        if source.parent is not None:
            dto.parent_code = source.parent.unique_code

        return dto
