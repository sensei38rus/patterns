from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_step_model import recipe_step_model
from Src.Models.storage_model import storage_model


class recipe_model(abs_mod):
    """
    Модель технологической карты (рецептуры).
    Описывает состав, нормы расхода и технологический процесс приготовления
    блюда или полуфабриката. Поддерживает составные рецептуры (п. 2.5 ТЗ):
    одна технологическая карта может входить в состав другой.
    """

    # Максимальная длина описания карты
    __max_description_length = 1000

    def __init__(self, name="", cooking_time=0, portions=0, pieces=None, description="",
                 items=None, steps=None, sub_recipes=None):
        """
        Конструктор технологической карты.

        Параметры:
            name: Наименование блюда / полуфабриката (до 50 символов)
            cooking_time: Время приготовления в минутах (целое, больше нуля)
            portions: Выход готового продукта в порциях (целое, больше нуля)
            pieces: Выход в штуках (целое больше нуля или None, если не задан)
            description: Общее описание карты (до 1000 символов)
            items: Строки состава — ингредиенты (список recipe_item_model)
            steps: Шаги технологического процесса (список recipe_step_model)
            sub_recipes: Вложенные карты — составная рецептура (список recipe_model)
        """
        super().__init__()
        self.name = name
        self.cooking_time = cooking_time
        self.portions = portions
        self.pieces = pieces
        self.description = description
        self.items = items if items is not None else []
        self.steps = steps if steps is not None else []
        self.sub_recipes = sub_recipes if sub_recipes is not None else []

    @property
    def cooking_time(self):
        """
        Возвращает время приготовления в минутах.
        """
        return self.__cooking_time

    @cooking_time.setter
    def cooking_time(self, value):
        """
        Задаёт время приготовления. Целое число минут, больше нуля.
        """
        if not isinstance(value, int):
            raise argument_exception("cooking_time", "Время приготовления должно быть целым числом")

        if value <= 0:
            raise argument_exception("cooking_time", "Время приготовления должно быть больше нуля")

        self.__cooking_time = value

    @property
    def portions(self):
        """
        Возвращает выход готового продукта в порциях.
        """
        return self.__portions

    @portions.setter
    def portions(self, value):
        """
        Задаёт выход в порциях. Целое число, больше нуля.
        """
        if not isinstance(value, int):
            raise argument_exception("portions", "Выход в порциях должен быть целым числом")

        if value <= 0:
            raise argument_exception("portions", "Выход в порциях должен быть больше нуля")

        self.__portions = value

    @property
    def pieces(self):
        """
        Возвращает выход готового продукта в штуках. None, если не задан.
        """
        return self.__pieces

    @pieces.setter
    def pieces(self, value):
        """
        Задаёт выход в штуках. Допускается None, иначе — целое число больше нуля.
        """
        if value is None:
            self.__pieces = None
            return

        if not isinstance(value, int):
            raise argument_exception("pieces", "Выход в штуках должен быть целым числом или None")

        if value <= 0:
            raise argument_exception("pieces", "Выход в штуках должен быть больше нуля")

        self.__pieces = value

    @property
    def description(self):
        """
        Возвращает общее описание технологической карты.
        """
        return self.__description

    @description.setter
    def description(self, value):
        """
        Задаёт описание карты. Строка до 1000 символов, может быть пустой.
        """
        if not isinstance(value, str):
            raise argument_exception("description", "Описание карты должно быть строкой")

        value = value.strip()
        if len(value) > self.__max_description_length:
            raise max_length_exception("description", len(value), self.__max_description_length)

        self.__description = value

    @property
    def items(self):
        """
        Возвращает строки состава карты (ингредиенты).
        """
        return self.__items

    @items.setter
    def items(self, value):
        """
        Задаёт строки состава. Список экземпляров recipe_item_model.
        """
        self.__validate_collection(value, recipe_item_model, "items")
        self.__items = list(value)

    @property
    def steps(self):
        """
        Возвращает шаги технологического процесса.
        """
        return self.__steps

    @steps.setter
    def steps(self, value):
        """
        Задаёт шаги технологического процесса. Список экземпляров recipe_step_model.
        """
        self.__validate_collection(value, recipe_step_model, "steps")
        self.__steps = list(value)

    @property
    def sub_recipes(self):
        """
        Возвращает вложенные технологические карты (составная рецептура).
        """
        return self.__sub_recipes

    @sub_recipes.setter
    def sub_recipes(self, value):
        """
        Задаёт вложенные карты. Список экземпляров recipe_model без циклических ссылок и дубликатов.
        """
        self.__validate_collection(value, recipe_model, "sub_recipes")

        for element in value:
            if element.__contains_recipe(self):
                raise argument_exception("sub_recipes", "Составная рецептура не должна содержать циклических ссылок")

        if len({str(element.id) for element in value}) != len(value):
            raise argument_exception("sub_recipes", "Составная рецептура не должна содержать дубликатов")

        self.__sub_recipes = list(value)

    @property
    def is_composite(self) -> bool:
        """
        Флаг составной рецептуры: карта содержит вложенные технологические карты.
        """
        return len(self.__sub_recipes) > 0

    @property
    def weight_netto(self):
        """
        Вес Нетто — сумма весов ингредиентов без упаковки в базовой единице измерения.
        Вес вложенных карт (полуфабрикатов) суммируется рекурсивно.
        """
        return self.__calculate_weight(include_packaging=False)

    @property
    def weight_brutto(self):
        """
        Вес Брутто — сумма весов всех ингредиентов, включая упаковку,
        в базовой единице измерения. Вес вложенных карт суммируется рекурсивно.
        """
        return self.__calculate_weight(include_packaging=True)

    def add_item(self, item) -> bool:
        """
        Добавляет строку состава в карту.

        Возвращает True, если строка добавлена;
        False, если неверный тип или дубликат по идентификатору.
        """
        if not isinstance(item, recipe_item_model):
            return False

        if any(existing == item for existing in self.__items):
            return False

        self.__items.append(item)
        return True

    def remove_item(self, item) -> bool:
        """
        Удаляет строку состава из карты.

        Возвращает True, если строка удалена;
        False, если неверный тип или строка не найдена.
        """
        if not isinstance(item, recipe_item_model):
            return False

        for existing in self.__items:
            if existing == item:
                self.__items.remove(existing)
                return True

        return False

    def add_step(self, step) -> bool:
        """
        Добавляет шаг технологического процесса.

        Возвращает True, если шаг добавлен;
        False, если неверный тип или дубликат по идентификатору.
        """
        if not isinstance(step, recipe_step_model):
            return False

        if any(existing == step for existing in self.__steps):
            return False

        self.__steps.append(step)
        return True

    def add_sub_recipe(self, recipe) -> bool:
        """
        Добавляет вложенную технологическую карту (составная рецептура, п. 2.5 ТЗ).

        Возвращает True, если карта добавлена; False, если неверный тип,
        дубликат либо вложение привело бы к циклической ссылке.
        """
        if not isinstance(recipe, recipe_model):
            return False

        if any(existing == recipe for existing in self.__sub_recipes):
            return False

        if recipe.__contains_recipe(self):
            return False

        self.__sub_recipes.append(recipe)
        return True

    @staticmethod
    def __validate_collection(value, element_type, field) -> None:
        """
        Проверяет, что значение является списком экземпляров указанного типа.

        Параметры:
            value: Проверяемое значение
            element_type: Ожидаемый тип элементов списка
            field: Наименование проверяемого поля (для сообщения об ошибке)
        """
        if not isinstance(value, list):
            raise argument_exception(field, "Коллекция должна быть списком")

        for element in value:
            if not isinstance(element, element_type):
                raise argument_exception(field, f"Элемент должен быть типа {element_type.__name__}")

    def __calculate_weight(self, include_packaging: bool):
        """
        Суммирует веса ингредиентов карты и её вложенных карт.

        Параметры:
            include_packaging: Учитывать ли строки с признаком упаковки
        """
        total = 0

        for item in self.__items:
            if item.is_packaging and not include_packaging:
                continue
            total += item.weight

        for sub in self.__sub_recipes:
            total += sub.__calculate_weight(include_packaging)

        return total

    def __contains_recipe(self, target) -> bool:
        """
        Проверяет, содержится ли целевая карта в поддереве составных карт (включая саму карту).

        Параметры:
            target: Целевая технологическая карта
        """
        if self == target:
            return True

        return any(child.__contains_recipe(target) for child in self.__sub_recipes)

    @staticmethod
    def create_cottage_cheese_filling(nomenclatures=None, ranges=None, storages=None):
        """
        Фабричный метод - создать полуфабрикат "Творожная масса" (Docs/Recipe.md).

        Параметры:
            nomenclatures: Справочник номенклатуры {наименование: nomenclature_model}
            ranges: Справочник единиц измерения {наименование: range_model}
            storages: Справочник складов {наименование: storage_model}
        Справочники необязательны: при отсутствии создаются локальные объекты.
        """
        nomenclatures = nomenclatures or {}
        ranges = ranges or {}
        storages = storages or {}

        gram = ranges.get("грамм") or range_model.create_gram()
        piece = ranges.get("штука") or range_model.create_piece()
        fridge = storages.get("Холодильник цеха") or storage_model.create_fridge()
        main_storage = storages.get("Основной склад") or storage_model.create_main_storage()

        flour = nomenclatures.get("Мука пшеничная") or nomenclature_model.create_flour()
        eggs = nomenclatures.get("Яйца куриные") or nomenclature_model.create_eggs()
        sugar = nomenclatures.get("Сахар") or nomenclature_model.create_sugar()
        salt = nomenclatures.get("Соль") or nomenclature_model.create_salt()
        cottage_cheese = nomenclatures.get("Творог 9%") or nomenclature_model.create_cottage_cheese()

        return recipe_model(
            name="Творожная масса",
            cooking_time=10,
            portions=2,
            pieces=6,
            description="Полуфабрикат для сырников.",
            items=[
                recipe_item_model.create(cottage_cheese, 300, gram, fridge),
                recipe_item_model.create(eggs, 1, piece, fridge),
                recipe_item_model.create(sugar, 30, gram, main_storage),
                recipe_item_model.create(salt, 2, gram, main_storage),
                recipe_item_model.create(flour, 30, gram, main_storage, "В тесто"),
            ],
            steps=[
                recipe_step_model(
                    "Замес творожной массы",
                    1,
                    "Перетереть творог с яйцом, сахаром и солью, ввести муку и вымесить однородное тесто."
                ),
            ],
        )

    @staticmethod
    def create_syrniki(filling=None, nomenclatures=None, ranges=None, storages=None):
        """
        Фабричный метод - создать технологическую карту "Сырники из творога классические"
        (Docs/Recipe.md). Включает полуфабрикат и упаковку.

        Параметры:
            filling: Вложенная карта полуфабриката (по умолчанию создаётся "Творожная масса")
            nomenclatures: Справочник номенклатуры {наименование: nomenclature_model}
            ranges: Справочник единиц измерения {наименование: range_model}
            storages: Справочник складов {наименование: storage_model}
        Справочники необязательны: при отсутствии создаются локальные объекты.
        """
        nomenclatures = nomenclatures or {}
        ranges = ranges or {}
        storages = storages or {}

        gram = ranges.get("грамм") or range_model.create_gram()
        milliliter = ranges.get("миллилитр") or range_model.create_milliliter()
        piece = ranges.get("штука") or range_model.create_piece()
        main_storage = storages.get("Основной склад") or storage_model.create_main_storage()

        flour = nomenclatures.get("Мука пшеничная") or nomenclature_model.create_flour()
        oil = nomenclatures.get("Масло подсолнечное") or nomenclature_model.create_sunflower_oil()
        box = nomenclatures.get("Коробка для завтраков") or nomenclature_model.create_breakfast_box()

        if filling is None:
            filling = recipe_model.create_cottage_cheese_filling(nomenclatures, ranges, storages)

        result = recipe_model(
            name="Сырники из творога классические",
            cooking_time=30,
            portions=2,
            pieces=6,
            description="Подавать горячими по 3 штуки на порцию, не ниже 65 градусов; при доставке — в бумажной коробке.",
            items=[
                recipe_item_model.create(flour, 20, gram, main_storage, "На подпыл при формовке"),
                recipe_item_model.create(oil, 20, milliliter, main_storage),
                recipe_item_model.create_packaging(
                    box, 1, piece, main_storage, "Одноразовая упаковка для доставки"
                ),
            ],
            steps=[
                recipe_step_model(
                    "Подготовка сырья",
                    1,
                    "Проверить сроки годности, муку просеять, творог протереть через сито."
                ),
                recipe_step_model(
                    "Формовка и тепловая обработка",
                    2,
                    "Сформовать сырники, обжарить по 2-3 минуты с каждой стороны до золотистой корочки."
                ),
            ],
        )
        result.add_sub_recipe(filling)
        return result
