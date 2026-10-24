from Src.Core.abstract_convertor import abstract_convertor
import datetime
from Src.Core.exception import argument_exception

"""
Конвертер типа DateTime
"""
class datetime_convertor(abstract_convertor):

    @staticmethod
    def convertable(obj):
        return isinstance(obj, datetime.datetime)


    def Convert(self, source):
        if not self.convertable(source):
            raise argument_exception("datetime convertor supports only datetime type")

        return {type(source).__name__: source}

