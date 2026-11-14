from Src.Core.abstract_manager import abstract_manager
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.settings_model import settings_model
from Src.Core.validator import validator, operation_exception, argument_exception, conflict_exception
from Src.Models.ingredient_model import ingredient_model
from Src.Models.receipt_model import receipt_model
from Src.Core.abstract_model import abstact_model
from Src.Core.common import common

"""
Реализация менеджера для управления и кеширования доменных сущностей
"""
class storage_manager(abstract_manager):
    # Набор данных
    __data = {}
    # Текущие настройки
    __settings:settings_model = None

    @staticmethod
    def range_key():
        """
        Единица измерений
        """
        return "range_model"
    

    @staticmethod
    def group_key():
        """
        Категория
        """
        return "group_model"
    
    @staticmethod
    def storage_key():
        """
        Склад
        """
        return "storage_model"

    @staticmethod
    def nomenclature_key():
        """
        Номенклатура
        """
        return "nomenclature_model"

    @staticmethod
    def receipt_key():
        """
        Рецепты
        """
        return "receipt_model"


    @staticmethod
    def domains() -> dict:
        """
        Возвращает словарь всех доступных ключей и их описаний.
        Ключ — значение, возвращаемое методом (например, "nomenclature_model").
        Значение — описание из docstring метода (например, "Номенклатура").
        """
        result = {}
        
        # Получаем список имен всех статических методов, заканчивающихся на '_key'
        method_names = [
            name for name in dir(storage_manager) 
            if callable(getattr(storage_manager, name)) and name.endswith('_key')
        ]

        for method_name in method_names:
            # Получаем сам объект метода
            method = getattr(storage_manager, method_name)
            
            # Получаем значение ключа (например, "nomenclature_model")
            key_value = method()
            
            # Получаем описание из документации (первая строка docstring)
            docstring = method.__doc__
            description = docstring.strip().split('\n')[0] if docstring else method_name
            
            result[key_value] = description
            
        return result
    


    """
    Получить набор данных
    """
    @property
    def data(self):
        return self.__data


    """
    Получить реестр всех хранимых сущностей (код -> модель).
    Используется при десериализации запросов для разрешения ссылок
    на существующие сущности
    """
    def registry(self) -> dict:
        result = {}
        for items in self.__data.values():
            for item in items:
                if isinstance(item, abstact_model):
                    result[ item.unique_code ] = item
        return result


    """
    Найти сущность по ключу коллекции и уникальному коду.
    Возвращает None, если сущность не найдена
    """
    def find(self, key: str, unique_code: str):
        self.__check_collection(key)
        items = self.__data[ key ]
        return next((item for item in items if item.unique_code == unique_code), None)


    """
    Добавить новую сущность в коллекцию.
    Проверяется корректность типа и уникальность кода
    """
    def add(self, key: str, model: abstact_model) -> None:
        self.__check_collection(key)

        if not isinstance(model, abstact_model):
            raise argument_exception("Ожидается доменная модель!")
        if type(model).__name__ != key:
            raise argument_exception(f"Ожидается тип сущности {key}, получен {type(model).__name__}!")
        if self.find(key, model.unique_code) is not None:
            raise conflict_exception(f"Сущность {key} с кодом {model.unique_code} уже существует!")

        self.__data[ key ].append(model)


    """
    Обновить сущность в коллекции.
    Изменяются только переданные поля (fields).
    Код (unique_code) можно менять только если сущность ни с кем не связана
    """
    def update(self, key: str, unique_code: str, model: abstact_model, fields: list, new_code: str = None) -> abstact_model:
        target = self.find(key, unique_code)
        if target is None:
            raise operation_exception(f"Сущность {key} с кодом {unique_code} не найдена!")

        if not isinstance(model, abstact_model):
            raise argument_exception("Ожидается доменная модель!")

        # Проверка ссылочной целостности при изменении кода
        if new_code is not None and new_code != unique_code:
            references = self.references(target)
            if len(references) > 0:
                raise conflict_exception(
                    f"Запрещено менять код сущности {key}: она связана с другими доменными сущностями!"
                )
            if self.find(key, new_code) is not None:
                raise conflict_exception(f"Код {new_code} уже используется в коллекции {key}!")

        for field in fields:
            if field == "unique_code":
                continue

            descriptor = getattr(type(target), field, None)
            if isinstance(descriptor, property) and descriptor.fset is not None:
                setattr(target, field, getattr(model, field))

        if new_code is not None:
            target.unique_code = new_code

        return target


    """
    Удалить сущность из коллекции.
    Удаление запрещено, если на сущность ссылаются другие доменные сущности
    """
    def remove(self, key: str, unique_code: str) -> None:
        target = self.find(key, unique_code)
        if target is None:
            raise operation_exception(f"Сущность {key} с кодом {unique_code} не найдена!")

        references = self.references(target)
        if len(references) > 0:
            linked = ", ".join([f"{item['entity']}({item['unique_code']})" for item in references])
            raise conflict_exception(
                f"Невозможно удалить сущность {key}: на нее ссылаются {linked}!"
            )

        self.__data[ key ].remove(target)


    """
    Найти все сущности хранилища, которые ссылаются на указанную.
    Проверяются свойства-модели, списки и вложенные структуры
    """
    def references(self, target: abstact_model) -> list:
        result = []
        if not isinstance(target, abstact_model):
            return result

        visited = set()
        for key, items in self.__data.items():
            for item in items:
                if item is target:
                    continue
                if storage_manager.__has_reference(item, target.unique_code, visited):
                    result.append({
                        "entity": key,
                        "unique_code": item.unique_code,
                        "name": str(getattr(item, "name", ""))
                    })

        return result


    """
    Проверить, содержит ли значение ссылку на сущность с указанным кодом
    """
    @staticmethod
    def __has_reference(value, target_code: str, visited: set) -> bool:
        if isinstance(value, abstact_model):
            if value.unique_code == target_code:
                return True

            if id(value) in visited:
                return False
            visited.add(id(value))

            for field in common.get_fields(value, is_common=False):
                if storage_manager.__has_reference(getattr(value, field, None), target_code, visited):
                    return True
            return False

        if isinstance(value, (list, tuple, set)):
            return any(storage_manager.__has_reference(item, target_code, visited) for item in value)

        if isinstance(value, dict):
            return any(storage_manager.__has_reference(item, target_code, visited) for item in value.values())

        return False


    """
    Проверить, что ключ коллекции существует
    """
    def __check_collection(self, key: str) -> None:
        if not isinstance(key, str) or key not in self.__data:
            raise operation_exception(f"Неизвестная доменная сущность {key}!")



    """
    Конструктор
    """
    def __init__(self, settings:settings_model):
        validator.validate(settings, settings_model)
        self.__settings = settings
        
        keys = storage_manager.domains().keys()
        for key in keys:
            self.__data[ key ] = []

    """
    Генерация данных
    """        
    def build(self):

        if self.__settings.first_start == False or self.is_loaded == True:
            return False
        
        # Единицы измерения
        range_killogramm = range_model.create_killogramm()

        range_item = range_model()
        range_item.name = "Штуки"

        self.data[ storage_manager.range_key() ] = [range_killogramm.base, range_killogramm, range_item]

        # Группы
        group = group_model.create_default_group()
        self.data[ storage_manager.group_key() ] = [group]

        # Склады
        storage = storage_model()
        storage.name = "Основной склад"
        storage.address = "Иркутск, ул. Высокого Полета, д.100"

        self.data[ storage_manager.storage_key() ] = [storage]

        # Номенклатура
        nomenclature_flour = nomenclature_model()
        nomenclature_flour.name = "Пшеничная мука"
        nomenclature_flour.group = group
        nomenclature_flour.range = range_killogramm

        nomenclature_sugar = nomenclature_model()
        nomenclature_sugar.name = "Сахар"
        nomenclature_sugar.group = group
        nomenclature_sugar.range = range_killogramm

        nomenclature_oil = nomenclature_model()
        nomenclature_oil.name = "Сливочное масло"
        nomenclature_oil.group = group
        nomenclature_oil.range = range_killogramm

        nomenclature_egg = nomenclature_model()
        nomenclature_egg.name = "Яйцо (шт)"
        nomenclature_egg.group = group
        nomenclature_egg.range = range_item

        nomenclature_vanilin = nomenclature_model()
        nomenclature_vanilin.name = "Ванилин"
        nomenclature_vanilin.group = group
        nomenclature_vanilin.range = range_killogramm.base

        self.data[ storage_manager.nomenclature_key() ] = [nomenclature_flour, nomenclature_sugar, nomenclature_oil, nomenclature_egg, nomenclature_vanilin]

        # Создание рецепта "Вафли хрустящие в вафельнице" (10 порций)
        receipt = receipt_model()

        # Ингредиент 1: Пшеничная мука (100 гр)
        ingredient_flour = ingredient_model()
        ingredient_flour.name = "Пшеничная мука"
        ingredient_flour.group = group
        ingredient_flour.range = range_killogramm
        ingredient_flour.brutto = 100
        ingredient_flour.netto = 100
        receipt.add(ingredient_flour)

        # Ингредиент 2: Сахар (80 гр)
        ingredient_sugar = ingredient_model()
        ingredient_sugar.name = "Сахар"
        ingredient_sugar.group = group
        ingredient_sugar.range = range_killogramm
        ingredient_sugar.brutto = 80
        ingredient_sugar.netto = 80
        receipt.add(ingredient_sugar)

        # Ингредиент 3: Сливочное масло (70 гр)
        ingredient_butter = ingredient_model()
        ingredient_butter.name = "Сливочное масло"
        ingredient_butter.group = group
        ingredient_butter.range = range_killogramm
        ingredient_butter.brutto = 70
        ingredient_butter.netto = 70
        receipt.add(ingredient_butter)

        # Ингредиент 4: Яйца (1 шт)
        ingredient_egg = ingredient_model()
        ingredient_egg.name = "Яйца"
        ingredient_egg.group = group
        ingredient_egg.range = range_item
        ingredient_egg.brutto = 1
        ingredient_egg.netto = 1
        receipt.add(ingredient_egg)

        # Ингредиент 5: Ванилин (5 гр)
        ingredient_vanilin = ingredient_model()
        ingredient_vanilin.name = "Ванилин"
        ingredient_vanilin.group = group
        ingredient_vanilin.range = range_killogramm.base
        ingredient_vanilin.brutto = 5
        ingredient_vanilin.netto = 5
        receipt.add(ingredient_vanilin)

        # Сохранение рецепта в кеш
        self.data[ storage_manager.receipt_key() ] = [receipt]

        return True

    

        




