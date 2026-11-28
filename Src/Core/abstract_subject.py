from abc import ABC
from Src.Core.abstract_observer import abstract_observer
from Src.Core.validator import argument_exception

"""
Абстрактный наблюдаемый объект (шаблон проектирования "Наблюдатель").
Хранит список подписанных наблюдателей и рассылает им события
через метод notify. Список наблюдателей создается лениво, поэтому
повторная инициализация объекта (например, конструктор синглтона)
не отменяет подписки
"""
class abstract_subject(ABC):

    """
    Подписать наблюдателя.
    Повторная подпись одного и того же наблюдателя игнорируется
    """
    def subscribe(self, observer) -> None:
        if observer is None:
            raise argument_exception("Не передан наблюдатель!")
        if not isinstance(observer, abstract_observer):
            raise argument_exception("Ожидается наблюдатель (abstract_observer)!")

        if observer in self.observers:
            return

        self.observers.append(observer)

    """
    Отписать наблюдателя. Отсутствие наблюдателя не является ошибкой
    """
    def unsubscribe(self, observer) -> None:
        if observer is None:
            return

        if observer in self.observers:
            self.observers.remove(observer)

    """
    Наблюдатели, подписанные на события
    """
    @property
    def observers(self) -> list:
        if getattr(self, "_subject_observers", None) is None:
            self._subject_observers = []
        return self._subject_observers

    """
    Уведомить всех подписанных наблюдателей.
    Ошибка одного наблюдателя не прерывает рассылку и не влияет
    на ход бизнес операции
    """
    def notify(self, event) -> None:
        for observer in list(self.observers):
            try:
                observer.update(event)
            except Exception:
                continue
