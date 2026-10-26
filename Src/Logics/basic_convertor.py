from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception

"""
Конвертер примитивных типов (int, float, str).
Возвращает значение как есть — без обёртки {имя_типа: значение},
чтобы результат был плоским и корректно сериализовался в JSON.
"""
class basic_convertor(abstract_convertor):

   @staticmethod
   def convertable(obj):
      """
      Проверить, поддерживает ли конвертер указанный тип.
      Область поддержки: int, float, str.
      """
      return isinstance(obj, (int, float, str))

   def Convert(self, source):
      """
      Конвертировать примитивное значение.
      Значение возвращается в исходном виде (плоское, без обёртки),
      None и посторонние типы не поддерживаются и приводят к исключению.
      """
      if not self.convertable(source):
         raise argument_exception("basic convertor supports only int, float and string")

      return source
