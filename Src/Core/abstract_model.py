from abc import ABC
import uuid

class name_id(ABC):
    # Конструктор абстрактного класса
    def __init__(self):
        self.__name = ""
        self.__id = uuid.uuid4()

    # Возвращает id 
    @property
    def id(self):
        return self.__id
    # Возвращает имя
    @property
    def name(self) -> str:
        return self.__name
    # Задает новое имя
    @name.setter
    def name(self, new_name: str):
        if new_name is not None and len(new_name) > 0:
            self.__name = new_name
        else:
            raise ValueError("Name is empty")