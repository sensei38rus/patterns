from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abs_mod
from Src.Core.exception import argument_exception

class reference_convertor(abstract_convertor):
  
    @staticmethod
    def convertable(obj):
        return isinstance(obj, abs_mod)

    
    def Convert(self, obj) -> dict:
        if not self.convertable(obj):
           raise argument_exception("reference convertor only supports abstract model derived classes")

        result = {}

        for name in dir(type(obj)):
            if name.startswith("_"):
                continue

            if not isinstance(getattr(type(obj), name, None), property):
                continue

            try:
                value = getattr(obj, name)
            except Exception as error:
                raise argument_exception("source", f"property '{name}' cannot be read: {error}")


            result[name] = value.id if isinstance(value, abs_mod) else value

        return result


ReferenceConvertor = reference_convertor
