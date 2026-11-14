import json
from Src.Logics.convert_factory import convert_factory
from Src.Logics.domain_convertor import domain_convertor
from Src.Core.abstract_model import abstact_model
from typing import Any, Dict, Type

from Src.Core.validator import validator, operation_exception
from Src.Core.common import common


class convertor:
    # Фабрика для подбора конвертора
    __factory: convert_factory = None

    def __init__(self):
        self.__factory = convert_factory()

    
    # Singletone
    def __new__(cls):
          if not hasattr(cls, 'instance'):
                  cls.instance = super(convertor, cls).__new__(cls)
          return cls.instance 

    """
    Сериализовать объект в словарь
    """
    def serialize(self, source: any ) -> dict:

          convertor = self.__factory.create( source )
          result = convertor.serialize( "result", source )
          return result


    """
    Десериализовать Json (строку) или словарь в объект.
    Обход структуры выполняется рекурсивно через фабрику конверторов,
    после загрузки разрешаются ссылки между моделями по уникальному коду.
    Параметр registry позволяет передать заранее известный набор моделей
    (например, содержимое хранилища), чтобы ссылки разрешались и на них
    """
    def deserialize(self, source: any, registry: dict = None ) -> object:
          # Источник может быть представлен строкой в формате Json
          if isinstance(source, str):
                try:
                      source = json.loads(source)
                except json.JSONDecodeError as ex:
                      raise operation_exception(f"Некорректный формат Json! {ex}")

          if not isinstance(source, dict):
                raise operation_exception("Десериализация ожидает словарь или строку в формате Json!")

          # Контекст: реестр загруженных моделей и отложенные ссылки между ними
          context = domain_convertor.create_context()
          if registry:
                context["registry"].update(registry)

          convertor = self.__factory.create( source )
          result = convertor.deserialize( source, context )

          domain_convertor.resolve_links( context )
          return result


    """
    Десериализовать словарь в объект (устаревшее имя метода)
    """
    def deserizlize(self, source: dict) -> object:
          return self.deserialize(source)
