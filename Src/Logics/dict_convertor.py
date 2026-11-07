from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.validator import validator
from Src.Logics.domain_convertor import domain_convertor

"""
Конвертация словаря
"""
class dict_convertor(abstract_convertor):
    # Фабрика для подбора конвертора
    __convert_factory: abstract_convert_factory = None

    def __init__(self, convert_factory: abstract_convert_factory):
        super().__init__()
        validator.validate(convert_factory, abstract_convert_factory)
        self.__convert_factory = convert_factory

    """
    Выполнить сериализацию.
    Каждое значение словаря рекурсивно обрабатывается через фабрику конверторов
    """ 
    def serialize(self, field: str, object:any) -> dict:
       super().serialize( field, object)

       result = {}
       for key, value in object.items():
           if value is None:
               result[ key ] = None
               continue

           convertor = self.__convert_factory.create( value )
           inner_result = convertor.serialize( key, value )
           result[ key ] = inner_result[ key ]

       return { field: result }

    """
    Выполнить десериализацию.
    Словарь, описывающий доменную модель (содержит маркер типа),
    передается в конвертер доменных моделей, иначе значения обходятся рекурсивно
    """
    def deserialize(self, source: dict, context: dict = None ) -> object:
        super().deserialize(source, context)

        own_context = context is None
        if own_context:
            context = domain_convertor.create_context()

        if self.__is_domain(source):
            result = self.__convert_factory.create_domain().deserialize( source, context )
        else:
            result = {}
            for key, value in source.items():
                if value is None:
                    result[ key ] = None
                    continue

                convertor = self.__convert_factory.create( value )
                result[ key ] = convertor.deserialize( value, context )

        if own_context:
            domain_convertor.resolve_links(context)

        return result

    """
    Признак того, что словарь описывает доменную модель
    (содержит маркер типа и уникальный код)
    """
    @staticmethod
    def __is_domain(source: any) -> bool:
        return isinstance(source, dict) and "type" in source and "unique_code" in source
