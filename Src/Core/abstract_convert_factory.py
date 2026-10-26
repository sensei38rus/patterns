from abc import ABC, abstractmethod
from Src.Core.abstract_convertor import abstract_convertor


"""
Абстрактная фабрика конвертеров типов.
Объявляет интерфейс создания семейства связанных конвертеров:
базовый (int, float, str), дата/время и ссылочный (модели).
"""
class abstract_convert_factory(ABC):
    """
    Базовая абстрактная фабрика для создания семейства конвертеров типов.
    """

    @abstractmethod
    def create_convertors(self) -> list[abstract_convertor]:
        """
        Создать семейство связанных конвертеров типов.
        :return: Список конвертеров, образующих семейство фабрики
        """
        pass


AbstractConvertFactory = abstract_convert_factory
