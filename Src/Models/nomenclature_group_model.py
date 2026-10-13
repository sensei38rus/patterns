from Src.Core.abstract_model import abs_mod


class nomenclature_group_model(abs_mod):
    """
    Модель группы номенклатуры.
    Категория для объединения позиций номенклатуры (например, "Мясо", "Овощи", "Молочные продукты").
    """

    def __init__(self, name=""):
        """
        Конструктор группы номенклатуры.

        Параметры:
            name: Наименование группы (до 50 символов)
        """
        super().__init__()
        self.name = name

    @staticmethod
    def create_grocery():
        """
        Фабричный метод - создать группу "Бакалея".
        """
        return nomenclature_group_model("Бакалея")

    @staticmethod
    def create_dairy():
        """
        Фабричный метод - создать группу "Молочные продукты".
        """
        return nomenclature_group_model("Молочные продукты")

    @staticmethod
    def create_dishes():
        """
        Фабричный метод - создать группу "Блюда".
        """
        return nomenclature_group_model("Блюда")

    @staticmethod
    def create_packaging():
        """
        Фабричный метод - создать группу "Упаковка".
        """
        return nomenclature_group_model("Упаковка")