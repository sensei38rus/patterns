from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import validator
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Logics.domain_convertor import domain_convertor

"""
Конвертация списка
"""
class list_convertor(abstract_convertor):
     # Фабрика для подбора конвертора
    __convert_factory:abstract_convert_factory = None
     # Фабрика для маппинга 
    __mapping_factory:abstract_mapping_factory = None

    def __init__(self, convert_factory: abstract_convert_factory, mapping_factory: abstract_mapping_factory):
        super().__init__()
        validator.validate(convert_factory, abstract_convert_factory)
        self.__convert_factory = convert_factory
        validator.validate(mapping_factory, abstract_mapping_factory)
        self.__mapping_factory = mapping_factory

    
    """
    Выполнить сериализацию
    """ 
    def serialize(self, field: str, items:any) -> dict:
        result = []
        for item in items:
            convertor = self.__convert_factory.create( item )
            convert_result = convertor.serialize( field, item )
            result.append( convert_result[ field ] )

        return { field: result }  
            

    """
    Выполнить десериализацию.
    Каждый элемент списка рекурсивно обрабатывается через фабрику конверторов
    """
    def deserialize(self, source: list, context: dict = None ) -> object:
        super().deserialize(source, context)

        own_context = context is None
        if own_context:
            context = domain_convertor.create_context()

        result = []
        for item in source:
            if item is None:
                result.append(None)
                continue

            convertor = self.__convert_factory.create( item )
            result.append( convertor.deserialize( item, context ) )

        if own_context:
            domain_convertor.resolve_links(context)

        return result
