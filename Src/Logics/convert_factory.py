from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor

"""
Фабрика конвертеров типов.
Подбирает подходящий конвертер по типу объекта и формирует
набор словарей согласно исходной структуре источника.
"""
class convert_factory:

    # Набор доступных конвертеров
    __convertors: list[abstract_convertor]

    def __init__(self):
        """
        Конструктор фабрики. Инициализирует набор поддерживаемых конвертеров:
        базовый (int, float, str), дата/время и конвертер ссылочных моделей.
        """
        self.__convertors = [
            basic_convertor(),
            datetime_convertor(),
            reference_convertor(),
        ]

    @property
    def convertors(self) -> list[abstract_convertor]:
        """
        Возвращает копию набора конвертеров фабрики.
        """
        return list(self.__convertors)

    def convert(self, source) -> list[dict]:
        """
        Конвертировать объект любого типа в набор словарей согласно исходной структуре.

        Примитивы и дата/время конвертируются соответствующим конвертером в один словарь.
        Модели (наследники abs_mod) конвертируются в словарь полей; вложенные модели
        добавляются отдельными словарями после словаря родителя (обход в глубину),
        ссылки на них заменяются идентификаторами. Списки и словари обрабатываются
        поэлементно.

        :param source: Исходный объект (примитив, дата/время, модель, список, словарь)
        :return: Список словарей согласно исходной структуре
        """
        if source is None:
            raise argument_exception("source", "Источник не должен быть None")

        if isinstance(source, (list, tuple)):
            result = []
            for item in source:
                result.extend(self.convert(item))
            return result

        if isinstance(source, dict):
            return self.__convert_pairs(source.items())

        return self.__convert(source)

    def __convert(self, source) -> list[dict]:
        """
        Конвертировать одиночный объект, подобрав конвертер по его типу.
        """
        convertor = self.__select(source)

        if isinstance(convertor, reference_convertor):
            return self.__convert_entity(source, set())

        return [convertor.Convert(source)]

    def __select(self, source) -> abstract_convertor:
        """
        Подобрать первый конвертер, который поддерживает указанный тип.
        """
        for convertor in self.__convertors:
            if convertor.convertable(source):
                return convertor

        raise argument_exception(
            "source",
            f"Тип {type(source).__name__} не поддерживается фабрикой конвертеров!"
        )

    def __convert_entity(self, entity: abs_mod, visited: set) -> list[dict]:
        """
        Конвертировать модель в словарь её полей и словари вложенных моделей.

        :param entity: Экземпляр модели (наследник abs_mod)
        :param visited: Идентификаторы уже посещённых моделей (защита от циклов)
        :return: Список словарей: словарь родителя, затем словари вложенных моделей
        """
        if entity.id in visited:
            return []

        visited.add(entity.id)

        pairs = []

        for name in dir(type(entity)):
            if name.startswith("_"):
                continue

            if not isinstance(getattr(type(entity), name, None), property):
                continue

            try:
                pairs.append((name, getattr(entity, name)))
            except Exception as error:
                raise argument_exception("source", f"property '{name}' cannot be read: {error}")

        return self.__convert_pairs(pairs, visited)

    def __convert_pairs(self, pairs, visited: set = None) -> list[dict]:
        """
        Конвертировать набор пар "ключ-значение" в словарь полей и
        словари вложенных моделей.

        :param pairs: Итерируемый набор пар (ключ, значение)
        :param visited: Идентификаторы уже посещённых моделей (защита от циклов)
        :return: Список словарей: словарь родителя, затем словари вложенных моделей
        """
        if visited is None:
            visited = set()

        fields = {}
        result = []

        for name, value in pairs:
            if isinstance(value, abs_mod):
                fields[name] = value.id
                result.extend(self.__convert_entity(value, visited))
            elif isinstance(value, (list, tuple)):
                collection = []
                for item in value:
                    if isinstance(item, abs_mod):
                        collection.append(item.id)
                        result.extend(self.__convert_entity(item, visited))
                    else:
                        collection.append(self.__convert_value(item))
                fields[name] = collection
            else:
                fields[name] = self.__convert_value(value)

        result.insert(0, fields)
        return result

    def __convert_value(self, value):
        """
        Конвертировать одиночное значение поля (примитив или дата/время)
        соответствующим конвертером. None и неподдерживаемые типы возвращаются как есть.
        """
        if value is None:
            return None

        for convertor in self.__convertors:
            if isinstance(convertor, reference_convertor):
                continue

            if convertor.convertable(value):
                return convertor.Convert(value)

        return value


ConvertFactory = convert_factory
