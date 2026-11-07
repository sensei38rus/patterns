from abc import ABC, abstractmethod


"""
Абстрактный класс для конвертации объекта в словарь полей
"""
class abstract_convertor(ABC):
    """
    Базовый абстрактный класс конвертера.
    """


    @staticmethod
    def convertable(obj)->bool:
        pass

    @abstractmethod
    def Convert(self, source: object) -> object:
        pass