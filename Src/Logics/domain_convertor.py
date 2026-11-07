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

            # Доменные коллекции (состав рецепта) сериализируем полностью,
            # а не кодами, чтобы модели можно было восстановить при загрузке
            model_value = getattr( object, item, None )
            if isinstance(model_value, list):
                value = model_value

            convertor = self.__convert_factory.create( value )
            value_dto = self.__mapping_factory.to_dto( value )
            if value_dto is None:
                 raise operation_exception(f"Невозможно сопоставить тип {type(value).__name__}!")

            inner_result = convertor.serialize( item, value_dto )
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

        # Заполняем Dto простыми полями из словаря
        for key, value in source.items():
            if key in ("type", "items") or value is None:
                continue
            if hasattr(dto, key):
                setattr( dto, key, value )

        # Создаем доменную модель из Dto
        model = self.__mapping_factory.to_model( dto )
        if model is None:
            raise operation_exception(f"Невозможно сопоставить тип {source.get('type')}!")

        context["registry"][ model.unique_code ] = model

        # Ссылки на другие модели откладываем до полной загрузки данных,
        # т.к. порядок моделей в Json не гарантирован
        for field_name in common.get_fields( dto, is_common=True ):
            if field_name.endswith("_code"):
                code = getattr( dto, field_name )
                if code:
                    context["links"].append( ( model, field_name[ : -len("_code") ], code ) )

        # Вложенные доменные модели (состав рецепта) загружаем рекурсивно
        items = source.get("items")
        if isinstance(items, list):
            for element in items:
                if not isinstance(element, dict):
                    continue
                child = self.deserialize( element, context )
                add = getattr( model, "add", None )
                if callable(add):
                    add( child )

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

            setattr( model, field_name, target )
