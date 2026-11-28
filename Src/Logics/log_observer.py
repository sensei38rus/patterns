import json
import os
from collections import deque
from Src.Core.abstract_observer import abstract_observer
from Src.Dtos.log_event_dto import log_event_dto

"""
Наблюдатель журнала операций (шаблон проектирования "Наблюдатель").

События, рассылаемые log_publisher, сохраняются в Json-файл
(формат Json Lines - одна строка на событие) и накапливаются в
кольцевом буфере в памяти. Буфер используется для выборки записей
и тестов, файл - долговременное хранение журнала
"""
class log_observer(abstract_observer):
    # Каталог журнала по умолчанию (корень проекта)
    __default_directory: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    """
    Путь к файлу журнала по умолчанию
    """
    @staticmethod
    def default_file() -> str:
        return os.path.join(log_observer.__default_directory, "logs", "app_log.jsonl")

    """
    Конструктор
    Args:
        file_path (str): Путь к файлу журнала (по умолчанию logs/app_log.jsonl)
        buffer_size (int): Размер кольцевого буфера событий в памяти
    """
    def __init__(self, file_path: str = "", buffer_size: int = 1000):
        inner_file_name = "" if file_path is None else str(file_path).strip()
        self.__file_path = inner_file_name if inner_file_name != "" else log_observer.default_file()
        self.__buffer = deque(maxlen=int(buffer_size) if int(buffer_size) > 0 else 1000)
        self.__failures = 0
        self.__last_error = ""

    """
    Путь к файлу журнала
    """
    @property
    def file_path(self) -> str:
        return self.__file_path

    """
    Количество событий в памяти
    """
    @property
    def count(self) -> int:
        return len(self.__buffer)

    """
    Количество ошибок записи журнала
    """
    @property
    def failures(self) -> int:
        return self.__failures

    """
    Текст последней ошибки записи журнала
    """
    @property
    def last_error(self) -> str:
        return self.__last_error

    """
    Получить уведомление наблюдаемого объекта:
    событие сохраняется в буфер и дописывается в файл журнала
    """
    def update(self, event) -> None:
        if not isinstance(event, log_event_dto):
            return

        self.__buffer.append(event)
        self.__write(event)

    """
    Выбрать события из буфера.
    category - отбор по категории (сравнение выполняется по группам события),
    operation - отбор по наименованию операции,
    status - отбор по статусу выполнения (success | error)
    """
    def records(self, category=None, operation=None, status=None) -> list:
        result = []

        for event in self.__buffer:
            if category is not None and not event.belongs_to(category):
                continue
            if operation is not None and event.operation != operation:
                continue
            if status is not None and event.status != status:
                continue

            result.append(event)

        return result

    """
    Очистить буфер событий в памяти (файл журнала не изменяется)
    """
    def clear(self) -> None:
        self.__buffer.clear()

    """
    Прочитать записи файла журнала в виде словарей
    """
    def read(self) -> list:
        if not os.path.exists(self.__file_path):
            return []

        with open(self.__file_path, "r", encoding="utf-8") as file:
            return [json.loads(line) for line in file if line.strip()]

    """
    Дописать событие в файл журнала.
    Ошибка записи не прерывает бизнес операцию: она фиксируется
    счетчиком failures и текстом last_error
    """
    def __write(self, event: log_event_dto) -> None:
        try:
            directory = os.path.dirname(self.__file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

            line = json.dumps(event.to_dict(), ensure_ascii=False, default=str)
            with open(self.__file_path, "a", encoding="utf-8") as file:
                file.write(f"{line}\n")
        except Exception as ex:
            self.__failures += 1
            self.__last_error = str(ex)
