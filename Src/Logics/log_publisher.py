from Src.Core.abstract_subject import abstract_subject
from Src.Core.validator import argument_exception
from Src.Dtos.log_category_enum import log_category_enum
from Src.Dtos.log_event_dto import log_event_dto

"""
Наблюдаемый объект журнала операций (шаблон проектирования "Наблюдатель").

Единый издатель событий системы: продуценты операций (хранилище, настройки,
web методы, сервис складского учета) публикуют события, а подписанные
наблюдатели (например log_observer) сохраняют их в журнал.
Издатель реализован в виде синглтона, чтобы наблюдатели подписывались
на один и тот же поток событий независимо от места вызова
"""
class log_publisher(abstract_subject):
    # Типы статусов события
    STATUS_SUCCESS: str = "success"
    STATUS_ERROR: str = "error"

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(log_publisher, cls).__new__(cls)
        return cls.instance

    """
    Отправить событие всем подписанным наблюдателям
    """
    def publish(self, event: log_event_dto) -> log_event_dto:
        if not isinstance(event, log_event_dto):
            raise argument_exception("Ожидается событие журнала (log_event_dto)!")

        self.notify(event)
        return event

    """
    Зарегистрировать CRUD операцию над доменной сущностью
    """
    def crud(self, operation: str, entity: str = "", unique_code: str = "",
             message: str = "", status: str = STATUS_SUCCESS, details: dict = None) -> log_event_dto:
        return self.__emit(log_category_enum.CRUD, [log_category_enum.CRUD],
                           operation, entity, unique_code, message, status, details)

    """
    Зарегистрировать складскую операцию.
    Параметр groups позволяет указать дополнительные категории
    (складская операция с сущностью склада является и CRUD операцией)
    """
    def warehouse(self, operation: str, entity: str = "", unique_code: str = "",
                  message: str = "", status: str = STATUS_SUCCESS, details: dict = None,
                  groups: list = None) -> log_event_dto:
        result = [log_category_enum.WAREHOUSE]
        for item in groups or []:
            if isinstance(item, log_category_enum) and item not in result:
                result.append(item)

        return self.__emit(log_category_enum.WAREHOUSE, result,
                           operation, entity, unique_code, message, status, details)

    """
    Зарегистрировать вызов web метода
    """
    def web(self, operation: str, entity: str = "", unique_code: str = "",
            message: str = "", status: str = STATUS_SUCCESS, details: dict = None) -> log_event_dto:
        return self.__emit(log_category_enum.WEB, [log_category_enum.WEB],
                           operation, entity, unique_code, message, status, details)

    """
    Зарегистрировать изменение параметров настроек
    """
    def settings(self, operation: str, entity: str = "", unique_code: str = "",
                 message: str = "", status: str = STATUS_SUCCESS, details: dict = None) -> log_event_dto:
        return self.__emit(log_category_enum.SETTINGS, [log_category_enum.SETTINGS],
                           operation, entity, unique_code, message, status, details)

    """
    Собрать событие и отправить его наблюдателям
    """
    def __emit(self, category: log_category_enum, groups: list, operation: str,
               entity: str, unique_code: str, message: str, status: str, details: dict) -> log_event_dto:
        event = log_event_dto(category, operation)
        event.entity = entity
        event.unique_code = unique_code
        event.message = message
        event.status = status

        for item in groups:
            event.add_group(item)

        for key, value in (details or {}).items():
            event.add_detail(key, value)

        return self.publish(event)
