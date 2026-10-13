from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class recipe_item_model(abs_mod):
    """
    Модель строки состава технологической карты (рецепта).
    Связывает номенклатуру-ингредиент с нормой расхода, единицей измерения
    и местом хранения сырья.
    """

    # Максимальная длина примечания к строке состава
    __max_note_length = 255

    def __init__(self, nomenclature=None, quantity=0, range=None, storage=None, note="",
                 is_packaging=False):
        """
        Конструктор строки состава технологической карты.

        Параметры:
            nomenclature: Ингредиент (экземпляр nomenclature_model)
            quantity: Норма расхода на выход рецепта (положительное число)
            range: Единица измерения нормы расхода (экземпляр range_model)
            storage: Место хранения сырья (экземпляр storage_model или None)
            note: Примечание к строке (до 255 символов)
            is_packaging: Признак упаковки (True - строка не входит в вес Нетто)
        """
        super().__init__()
        self.nomenclature = nomenclature
        self.quantity = quantity
        self.range = range
        self.storage = storage
        self.note = note
        self.is_packaging = is_packaging

    @property
    def nomenclature(self):
        """
        Возвращает ингредиент (номенклатуру), входящий в состав карты.
        """
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value):
        """
        Задаёт ингредиент. Обязательный реквизит, тип — nomenclature_model.
        """
        if not isinstance(value, nomenclature_model):
            raise argument_exception("nomenclature", "Ингредиент должен быть типа nomenclature_model")
        self.__nomenclature = value

    @property
    def quantity(self):
        """
        Возвращает норму расхода ингредиента на выход рецепта.
        """
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        """
        Задаёт норму расхода. Должна быть положительным числом.
        """
        if not isinstance(value, (int, float)):
            raise argument_exception("quantity", "Норма расхода должна быть числом")

        if value <= 0:
            raise argument_exception("quantity", "Норма расхода должна быть больше нуля")

        self.__quantity = value

    @property
    def range(self):
        """
        Возвращает единицу измерения нормы расхода.
        """
        return self.__range

    @range.setter
    def range(self, value):
        """
        Задаёт единицу измерения. Обязательный реквизит, тип — range_model.
        """
        if not isinstance(value, range_model):
            raise argument_exception("range", "Единица измерения должна быть типа range_model")
        self.__range = value

    @property
    def storage(self):
        """
        Возвращает место хранения сырья. Может отсутствовать (None).
        """
        return self.__storage

    @storage.setter
    def storage(self, value):
        """
        Задаёт место хранения сырья. Допускается None, иначе — storage_model.
        """
        if value is not None and not isinstance(value, storage_model):
            raise argument_exception("storage", "Место хранения должно быть типа storage_model")
        self.__storage = value

    @property
    def note(self):
        """
        Возвращает примечание к строке состава.
        """
        return self.__note

    @note.setter
    def note(self, value):
        """
        Задаёт примечание. Строка до 255 символов, может быть пустой.
        """
        if not isinstance(value, str):
            raise argument_exception("note", "Примечание должно быть строкой")

        value = value.strip()
        if len(value) > self.__max_note_length:
            raise max_length_exception("note", len(value), self.__max_note_length)

        self.__note = value

    @property
    def is_packaging(self) -> bool:
        """
        Возвращает признак упаковки: True, если строка относится к упаковке.
        """
        return self.__is_packaging

    @is_packaging.setter
    def is_packaging(self, value):
        """
        Задаёт признак упаковки. Должен быть булевым значением.
        """
        if not isinstance(value, bool):
            raise argument_exception("is_packaging", "Признак упаковки должен быть булевым значением")

        self.__is_packaging = value

    @property
    def weight(self):
        """
        Возвращает вес ингредиента, пересчитанный в базовую единицу измерения
        (например, 2 килограмма -> 2000 граммов).
        """
        total = self.quantity
        current = self.range

        while current is not None:
            total = total * current.conversion_factor
            current = current.base_range

        return total

    @staticmethod
    def create(nomenclature, quantity, range, storage=None, note=""):
        """
        Фабричный метод - создать строку состава (ингредиент).

        Параметры:
            nomenclature: Ингредиент (экземпляр nomenclature_model)
            quantity: Норма расхода на выход рецепта (положительное число)
            range: Единица измерения нормы расхода (экземпляр range_model)
            storage: Место хранения сырья (экземпляр storage_model или None)
            note: Примечание к строке (до 255 символов)
        """
        return recipe_item_model(nomenclature, quantity, range, storage, note, False)

    @staticmethod
    def create_packaging(nomenclature, quantity, range, storage=None, note=""):
        """
        Фабричный метод - создать строку состава с признаком упаковки.

        Параметры:
            nomenclature: Позиция упаковки (экземпляр nomenclature_model)
            quantity: Норма расхода упаковки на выход рецепта (положительное число)
            range: Единица измерения нормы расхода (экземпляр range_model)
            storage: Место хранения (экземпляр storage_model или None)
            note: Примечание к строке (до 255 символов)
        """
        return recipe_item_model(nomenclature, quantity, range, storage, note, True)
