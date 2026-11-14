from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.validator import validator
from Src.Core.abstract_model import abstact_model
from Src.Core.entity_model import entity_model
from Src.Core.common import common
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.validator import operation_exception
from Src.Logics.model_factory import model_factory


"""
Конвертор доменных сущностей
"""
class domain_convertor(abstract_convertor):
    # Фабрика для подбора конвертора
    __convert_factory:abstract_convert_factory = None
    # Фабрика для маппинга 
    __mapping_factory:abstract_mapping_factory = None
    # Фабрика для создания доменных моделей по имени типа
    __model_factory:model_factory = None

    def __init__(self, convert_factory: abstract_convert_factory, mapping_factory: abstract_mapping_factory ):
        super().__init__()
        validator.validate(convert_factory, abstract_convert_factory)
        self.__convert_factory = convert_factory
        validator.validate(mapping_factory, abstract_mapping_factory)
        self.__mapping_factory = mapping_factory
        self.__model_factory = model_factory()


    """
    Абстрактная фабрика для конвертации данных
    """
    @property
    def factory(self) ->   abstract_convert_factory:
        return self.__convert_factory  

    
    """
    Переопределенный метод для сериализации.
    Доменная модель преобразуется в плоскую Dto, ссылки на другие модели
    заменяются их уникальными кодами. Вложенные коллекции (состав рецепта)
    сериализуются целиком для возможности обратной загрузки
    """
    def serialize(self, field: str, object: any) -> dict:
        super().serialize(field, object)
        result = {}

        dto = self.__mapping_factory.to_dto( object )
        if dto is None:
            raise operation_exception(f"Невозможно сопоставить тип {type(object).__name__}!")

        fields = common.get_fields( dto )

        # Маркер типа - используется фабрикой моделей при десериализации
        if isinstance(object, abstact_model):
            result[ "type" ] = object.type

        for item in fields:
            value = getattr( dto, item )

            # Вложенные структуры модели (состав рецепта, вложенные словари)
            # сериализируем полностью, а не кодами, чтобы данные можно
            # было восстановить при загрузке
            model_value = getattr( object, item, None )
            if isinstance(model_value, (list, dict)):
                value = model_value

            # Пустое значение остается пустым. Остальные значения передаются
            # в конвертер как есть: для простых типов это значение поля,
            # для доменных моделей - сама модель (Dto создается внутри)
            if value is None:
                 result[ item ] = None
                 continue

            convertor = self.__convert_factory.create( value )
            inner_result = convertor.serialize( item, value )
            result[ item ] = inner_result[ item ]
 
        return { field: result }   


    """
    Переопределенный метод для десериализации.
    Из словаря создается Dto, затем доменная модель.
    Ссылки на другие модели (по уникальному коду) разрешаются после
    загрузки всех данных через контекст
    """    
    def deserialize(self, source, context: dict = None) -> object:
        super().deserialize(source, context)

        own_context = context is None
        if own_context:
            context = domain_convertor.create_context()

        # Фабрика моделей создает Dto по маркеру типа
        dto = self.__model_factory.create_dto( source.get("type") )

        # Простые поля переносим в Dto. Тип, списки и вложенные словари
        # сюда не попадают: тип читает фабрика моделей, а структуры
        # обрабатываются отдельно после создания модели
        for key, value in source.items():
            if value is None or isinstance(value, (list, dict)):
                continue
            if hasattr(dto, key):
                setattr( dto, key, value )

        # Создаем доменную модель из Dto
        model = self.__mapping_factory.to_model( dto )
        if model is None:
            raise operation_exception(f"Невозможно сопоставить тип {source.get('type')}!")

        # Одна и та же модель может встречаться в дампе несколько раз
        # (в общем наборе и в составе другого объекта) - используем уже
        # загруженный экземпляр, чтобы все ссылки вели на один объект
        registered = context["registry"].get( model.unique_code )
        if registered is None:
            context["registry"][ model.unique_code ] = model
        else:
            model = registered

        # Ссылки на другие модели откладываем до полной загрузки данных,
        # т.к. порядок моделей в Json не гарантирован.
        # Поле ссылки в Dto заканчивается на "_code", а соответствующее
        # свойство модели (group, range, base, ...) должно существовать
        # и быть записываемым - по этому признаку ссылка отличается
        # от идентификатора (unique_code не является ссылкой)
        for field_name in common.get_fields( dto, is_common=True ):
            if not field_name.endswith("_code"):
                continue

            reference = field_name[ : -len("_code") ]
            if not domain_convertor.__can_attach( model, reference ):
                continue

            code = getattr( dto, field_name )
            if code:
                context["links"].append( ( model, reference, code ) )

        # Вложенные доменные модели и структуры загружаем рекурсивно
        # с тем же контекстом и привязываем к модели через сеттер свойства
        for key, value in source.items():
            if isinstance(value, dict):
                inner = self.deserialize(value, context) if domain_convertor.is_domain(value) else value
                domain_convertor.__attach( model, key, inner )
            elif isinstance(value, list):
                elements = [
                    self.deserialize(item, context)
                    if isinstance(item, dict) and domain_convertor.is_domain(item)
                    else item
                    for item in value
                ]
                domain_convertor.__attach( model, key, elements )

        if own_context:
            domain_convertor.resolve_links(context)

        return model


    """
    Создать пустой контекст десериализации:
    реестр загруженных моделей и список отложенных ссылок
    """
    @staticmethod
    def create_context() -> dict:
        return { "registry": {}, "links": [] }


    """
    Признак того, что словарь описывает доменную модель
    (содержит маркер типа и уникальный код)
    """
    @staticmethod
    def is_domain(source: any) -> bool:
        return isinstance(source, dict) and "type" in source and "unique_code" in source


    """
    Признак того, что модели можно присвоить значение по имени свойства
    """
    @staticmethod
    def __can_attach(model: abstact_model, field_name: str) -> bool:
        descriptor = getattr( type(model), field_name, None )
        return isinstance(descriptor, property) and descriptor.fset is not None


    """
    Присвоить значение свойству модели. Единственный способ передать
    конвертору вложенные данные - сеттер свойства, поэтому отсутствие
    сеттера является ошибкой модели, а не поводом терять данные
    """
    @staticmethod
    def __attach(model: abstact_model, field_name: str, value: any) -> None:
        if not domain_convertor.__can_attach(model, field_name):
            raise operation_exception(
                f"Модель {type(model).__name__} не содержит записываемого свойства {field_name}!"
            )

        setattr( model, field_name, value )


    """
    Разрешить накопленные ссылки между моделями по уникальному коду
    """
    @staticmethod
    def resolve_links(context: dict) -> None:
        registry = context["registry"]

        for model, field_name, code in context["links"]:
            target = registry.get( code )
            if target is None:
                # Модель, на которую ссылаемся, отсутствует в наборе - пропускаем
                continue

            domain_convertor.__attach( model, field_name, target )
