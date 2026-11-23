from Src.Core.entity_model import entity_model
from Src.Core.filter_schema import filter_schema
from Src.Core.validator import validator, argument_exception

"""
Модель группы номенклатуры
"""
class group_model(entity_model):
    # Группа-владелец (родительская группа)
    __parent: "group_model" = None

    def __init__(self):
       super().__init__()

    """
    Схема фильтрации: листовые поля базы + ссылка на родительскую группу
    """
    @classmethod
    def filter_schema(cls) -> filter_schema:
        return filter_schema.base().with_links({
            "parent": group_model,
        })

    """
    Группа-владелец (родительская группа)
    """
    @property
    def parent(self) -> "group_model":
        return self.__parent

    @parent.setter
    def parent(self, value: "group_model"):
        if value is None:
            self.__parent = None
            return

        validator.validate(value, group_model)
        if value.unique_code == self.unique_code:
            raise argument_exception("Группа не может быть владельцем самой себя!")

        self.__parent = value

    """
    Фабричный метод - создать группу по умолчанию
    """
    @staticmethod
    def create_default_group() -> "group_model":
        result = group_model()
        result.name = "Ингредиенты"

        return result
