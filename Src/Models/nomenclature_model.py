from Src.Core.entity_model import entity_model
from Src.Core.filter_schema import filter_schema
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.validator import validator

"""
Модель номенклатуры
"""
class nomenclature_model(entity_model):
    __group: group_model = None
    __range: range_model = None

    def __init__(self):
        super().__init__()

    """
    Схема фильтрации: листовые поля базы + ссылки на группу и единицу измерения
    """
    @classmethod
    def filter_schema(cls) -> filter_schema:
        return filter_schema.base().with_links({
            "group": group_model,
            "range": range_model,
        })

    """
    Группа номенклатуры
    """
    @property
    def group(self) -> group_model:
        return self.__group

    @group.setter
    def group(self, value: group_model):
        validator.validate(value,entity_model )
        self.__group = value    

    """
    Единица измерения
    """
    @property
    def range(self) -> range_model:
        return self.__range
    
    @range.setter
    def range(self, value: range_model):
        validator.validate(value, range_model)
        self.__range = value







        
    