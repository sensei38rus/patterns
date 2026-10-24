from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class basic_convertor(abstract_convertor):

   @staticmethod
   def convertable(obj):
      return isinstance(obj, (int, float, str))

   def Convert(self, source):
      if not self.convertable(source):
         raise argument_exception("basic convertor supports only int, float and string")

      return {type(source).__name__: source}

   


