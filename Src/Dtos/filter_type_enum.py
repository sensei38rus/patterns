from enum import Enum

"""
Варианты сравнения при фильтрации данных
"""
class filter_type_enum(Enum):

    """
    Полное совпадение
    """
    EQUALS = 1

    """
    Вхождение строки (подстрока)
    """
    LIKE = 2
