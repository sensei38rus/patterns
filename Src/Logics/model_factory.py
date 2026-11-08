from typing import Dict, Tuple, Type
from Src.Core.abstract_model_factory import abstract_model_factory
from Src.Core.abstract_model import abstact_model
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import operation_exception
from Src.Dtos.receipt_dto import receipt_dto
from Src.Models.receipt_model import receipt_model
from Src.Dtos.range_dto import range_dto
from Src.Models.range_model import range_model
from Src.Dtos.group_dto import group_dto
from Src.Models.group_model import group_model
from Src.Dtos.ingredient_dto import ingredient_dto
from Src.Models.ingredient_model import ingredient_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Dtos.storage_dto import storage_dto
from Src.Models.storage_model import storage_model
from Src.Dtos.company_dto import company_dto
from Src.Models.company_model import company_model

"""
Реализация фабрики для создания доменных моделей и Dto по имени типа.
Имя типа берется из маркера 'type' при десериализации Json
"""
class model_factory(abstract_model_factory):
    # Маппинг: имя типа (доменной модели или Dto) -> (класс Dto, класс доменной модели)
    __mapping: Dict[str, Tuple[Type[abstract_dto], Type[abstact_model]]] = {}

    def __init__(self):
        super().__init__()
        # Синглтон: повторная инициализация не сбрасывает зарегистрированные пары
        if self.__mapping:
            return

        self.__mapping = {}
        pairs = [
            (receipt_dto, receipt_model),
            (range_dto, range_model),
            (group_dto, group_model),
            (ingredient_dto, ingredient_model),
            (nomenclature_dto, nomenclature_model),
            (storage_dto, storage_model),
            (company_dto, company_model),
        ]
        for dto_type, model_type in pairs:
            self.register(dto_type, model_type)

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(model_factory, cls).__new__(cls)
        return cls.instance

    """
    Зарегистрировать пару Dto и доменной модели по всем вариантам имени типа
    """
    def register(self, dto_type: Type[abstract_dto], model_type: Type[abstact_model]) -> None:
        variants = [
            model_type.__qualname__,
            f"{model_type.__module__}.{model_type.__qualname__}",
            dto_type.__qualname__,
            f"{dto_type.__module__}.{dto_type.__qualname__}",
        ]
        for name in variants:
            self.__mapping[name] = (dto_type, model_type)

    """
    Создать пустую доменную модель по имени типа
    """
    def create(self, type_name: str) -> abstact_model:
        entry = self.__get_entry(type_name)
        return entry[1]()

    """
    Создать пустую Dto по имени типа
    """
    def create_dto(self, type_name: str) -> abstract_dto:
        entry = self.__get_entry(type_name)
        return entry[0]()

    """
    Найти зарегистрированную пару Dto и доменной модели
    """
    def __get_entry(self, type_name: str) -> Tuple[Type[abstract_dto], Type[abstact_model]]:
        if not isinstance(type_name, str) or type_name.strip() == "":
            raise operation_exception("Не указан тип доменной модели для десериализации!")

        entry = self.__mapping.get(type_name.strip())
        if entry is None:
            raise operation_exception(f"Тип {type_name} не зарегистрирован в фабрике моделей!")

        return entry
