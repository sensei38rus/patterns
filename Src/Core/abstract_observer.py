from abc import ABC, abstractmethod

"""
Абстрактный наблюдатель (шаблон проектирования "Наблюдатель").
Реализует интерфейс получения уведомлений от наблюдаемого объекта
"""
class abstract_observer(ABC):

    """
    Получить уведомление о событии наблюдаемого объекта
    Args:
        event (log_event_dto): Событие журнала операций
    """
    @abstractmethod
    def update(self, event) -> None:
        pass
