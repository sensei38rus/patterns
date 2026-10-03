from Src.Core.exception import argument_exception, operation_exception


class validator:

    @staticmethod
    def validate(value, type_, len_=None):
       
        if value is None:
            raise argument_exception("value", "Пустой аргумент")

        # Проверка типа
        if not isinstance(value, type_):
            raise argument_exception(
                "value",
                f"Некорректный тип! Ожидается {type_}. Текущий тип {type(value)}"
            )

        # Проверка аргумента
        if len(str(value).strip()) == 0:
            raise argument_exception("value", "Пустой аргумент")

        if len_ is not None and len(str(value).strip()) > len_:
            raise argument_exception("value", "Некорректная длина аргумента")

        return True