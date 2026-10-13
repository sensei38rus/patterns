from Src.Core.abstract_manager import abstract_manager
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.recipe_model import recipe_model


class recipe_manager(abstract_manager):
    """
    Менеджер хранения технологических карт (рецептов).
    При первом старте (is_first_start == True) генерирует рецепты по Docs/Recipe.md.
    Реализует шаблон Singleton; данные хранятся в памяти по аналогии с storage_manager.
    """

    _recipes: dict = None
    __is_initialized: bool = False

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(recipe_manager, cls).__new__(cls)
            cls.instance._recipes = {}
            cls.instance.__is_initialized = False
        return cls.instance

    def convert(self, settings=None) -> bool:
        """
        Переопределенный метод abstract_manager.
        Если запуск первый (is_first_start == True) — генерирует технологические карты.
        При передаче settings извне — использует переданный объект (для тестов).
        """
        if self.__is_initialized:
            return True

        try:
            if settings is None:
                s_manager = settings_manager()
                if not s_manager.is_loaded:
                    s_manager.load()
                settings = s_manager.settings

            # Справочники (номенклатура, единицы, склады) — первичный источник для рецептов
            s_storage = storage_manager()
            if not s_storage.is_initialized:
                s_storage.convert(settings)

            if settings and settings.is_first_start:
                self._initialize_primary_data()

            self.__is_initialized = True
            return True
        except Exception:
            return False

    def _initialize_primary_data(self) -> None:
        """
        Инициализация первичных данных.
        Порядок важен: рецепты зависят от номенклатуры, единиц и складов storage_manager.
        """
        self.__create_recipes()

    def __create_recipes(self) -> None:
        """Генерация технологических карт по Docs/Recipe.md через фабричные методы recipe_model."""
        storage = storage_manager()
        references = {
            "nomenclatures": {n.name: n for n in storage.nomenclatures.values()},
            "ranges": {r.name: r for r in storage.ranges.values()},
            "storages": {s.name: s for s in storage.storages.values()},
        }

        filling = recipe_model.create_cottage_cheese_filling(**references)
        recipe = recipe_model.create_syrniki(filling=filling, **references)

        self.add_recipe(filling)
        self.add_recipe(recipe)

    def add_recipe(self, item: recipe_model) -> bool:
        """
        Добавляет технологическую карту в хранилище.

        Возвращает True, если карта добавлена;
        False, если неверный тип или дубликат по идентификатору.
        """
        if not isinstance(item, recipe_model) or item.id in self._recipes:
            return False

        self._recipes[item.id] = item
        return True

    def get_recipe(self, recipe_id):
        """
        Возвращает технологическую карту по идентификатору. None, если не найдена.
        """
        if recipe_id is None:
            return None

        return self._recipes.get(str(recipe_id).strip())

    @property
    def recipes(self) -> dict:
        """
        Словарь технологических карт {id: recipe_model}.
        """
        return self._recipes

    @property
    def is_initialized(self) -> bool:
        """Флаг завершения инициализации."""
        return self.__is_initialized

    @property
    def is_loaded(self) -> bool:
        """Флаг готовности данных (переопределение abstract_manager)."""
        return self.__is_initialized
