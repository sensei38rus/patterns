from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception, max_length_exception


class recipe_step_model(abs_mod):
    """
    Модель шага технологического процесса приготовления.
    Нумерованный этап описания технологии (например, "Замес творожной массы").
    """

    # Максимальная длина описания шага
    __max_description_length = 1000

    def __init__(self, name="", order=1, description=""):
        """
        Конструктор шага технологического процесса.

        Параметры:
            name: Наименование шага (до 50 символов)
            order: Порядковый номер шага (целое число, начиная с 1)
            description: Текст описания действий (1-1000 символов)
        """
        super().__init__()
        self.name = name
        self.order = order
        self.description = description

    @property
    def order(self):
        """
        Возвращает порядковый номер шага в технологическом процессе.
        """
        return self.__order

    @order.setter
    def order(self, value):
        """
        Задаёт порядковый номер шага. Целое число, начиная с 1.
        """
        if not isinstance(value, int):
            raise argument_exception("order", "Порядковый номер должен быть целым числом")

        if value < 1:
            raise argument_exception("order", "Порядковый номер должен начинаться с 1")

        self.__order = value

    @property
    def description(self):
        """
        Возвращает текст описания шага.
        """
        return self.__description

    @description.setter
    def description(self, value):
        """
        Задаёт текст описания шага. Обязательная строка до 1000 символов.
        """
        if not isinstance(value, str):
            raise argument_exception("description", "Описание шага должно быть строкой")

        value = value.strip()
        if value == "":
            raise argument_exception("description", "Описание шага не должно быть пустым")

        if len(value) > self.__max_description_length:
            raise max_length_exception("description", len(value), self.__max_description_length)

        self.__description = value
