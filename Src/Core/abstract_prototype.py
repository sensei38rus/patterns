from abc import ABC, abstractmethod

"""
Абстрактный класс для реализации паттерна «Прототип»
"""
class abstract_prototype(ABC):

    """
    Создать независимую копию прототипа
    """
    @abstractmethod
    def clone(self) -> "abstract_prototype":
        pass
