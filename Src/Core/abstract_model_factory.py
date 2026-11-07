from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstact_model
from Src.Core.abstract_dto import abstract_dto

"""
Абстрактный класс фабрики для создания доменных моделей и Dto по имени типа
"""
class abstract_model_factory(ABC):

    """
    Создать пустую доменную модель по имени типа
    """
    @abstractmethod
    def create(self, type_name: str) -> abstact_model:
        pass

    """
    Создать пустую Dto по имени типа
    """
    @abstractmethod
    def create_dto(self, type_name: str) -> abstract_dto:
        pass
