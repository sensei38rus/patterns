from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


class nomenclature_model(abs_mod):
    """
    Модель номенклатуры.
    Позиция учёта с кратким и полным наименованием, группой и единицей измерения.
    """

    # Максимальная длина полного наименования
    __max_full_name_length = 255

    def __init__(self, name="", full_name="", group=None, range=None):
        """
        Конструктор номенклатуры.

        Параметры:
            name: Краткое наименование (до 50 символов)
            full_name: Полное наименование (до 255 символов)
            group: Группа номенклатуры (экземпляр nomenclature_group_model)
            range: Единица измерения (экземпляр range_model)
        """
        super().__init__()
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range

    @property
    def full_name(self):
        """
        Возвращает полное наименование номенклатуры.
        """
        return self.__full_name

    @full_name.setter
    def full_name(self, value):
        """
        Задаёт полное наименование номенклатуры. Максимальная длина — 255 символов.
        """
        if value is None or str(value).strip() == "":
            raise argument_exception("full_name", "Полное наименование не должно быть пустым")

        value = str(value).strip()

        if len(value) > self.__max_full_name_length:
            raise max_length_exception("full_name", len(value), self.__max_full_name_length)

        self.__full_name = value

    @property
    def group(self):
        """
        Возвращает группу номенклатуры.
        """
        return self.__group

    @group.setter
    def group(self, value):
        """
        Задаёт группу номенклатуры. Должен быть экземпляром nomenclature_group_model.
        """
        if not isinstance(value, nomenclature_group_model):
            raise argument_exception("group", "Группа должна быть типа nomenclature_group_model")

        self.__group = value

    @property
    def range(self):
        """
        Возвращает единицу измерения номенклатуры.
        """
        return self.__range

    @range.setter
    def range(self, value):
        """
        Задаёт единицу измерения номенклатуры. Должен быть экземпляром range_model.
        """
        if not isinstance(value, range_model):
            raise argument_exception("range", "Единица измерения должна быть типа range_model")

        self.__range = value

    @staticmethod
    def create_flour(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Мука пшеничная".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Мука пшеничная", "Мука пшеничная высший сорт", group, range)

    @staticmethod
    def create_milk(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Молоко 3.2%".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - литр)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_liter()
        return nomenclature_model("Молоко 3.2%", "Молоко коровье пастеризованное 3.2%", group, range)

    @staticmethod
    def create_eggs(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Яйца куриные".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - штука)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_piece()
        return nomenclature_model("Яйца куриные", "Яйца куриные столовые С0", group, range)

    @staticmethod
    def create_butter(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Масло сливочное".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Масло сливочное", "Масло сливочное крестьянское 72.5%", group, range)

    @staticmethod
    def create_sugar(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Сахар".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Сахар", "Сахар белый кристаллический", group, range)

    @staticmethod
    def create_salt(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Соль".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Соль", "Соль поваренная пищевая", group, range)

    @staticmethod
    def create_cottage_cheese(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Творог 9%".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Творог 9%", "Творог 9% протёртый", group, range)

    @staticmethod
    def create_sunflower_oil(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Масло подсолнечное".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - литр)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_liter()
        return nomenclature_model("Масло подсолнечное", "Масло подсолнечное рафинированное", group, range)

    @staticmethod
    def create_breakfast_box(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Коробка для завтраков".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Упаковка")
            range: Единица измерения (по умолчанию - штука)
        """
        group = group or nomenclature_group_model.create_packaging()
        range = range or range_model.create_piece()
        return nomenclature_model("Коробка для завтраков", "Коробка бумажная для завтраков", group, range)

    @staticmethod
    def create_pancakes(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Блины классические".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Блюда")
            range: Единица измерения (по умолчанию - штука)
        """
        group = group or nomenclature_group_model.create_dishes()
        range = range or range_model.create_piece()
        return nomenclature_model("Блины классические", "Блины классические тонкие", group, range)