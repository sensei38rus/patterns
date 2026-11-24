from Src.Core.validator import argument_exception

"""
Схема фильтрации доменной сущности (value object).
Описывает, по каким полям можно фильтровать модель:
листовые поля (name, unique_code) и ссылочные свойства
(group, parent, base, range), ведущие к другим моделям.
Знание принадлежит доменной модели (Information Expert):
модель сама объявляет свою схему через filter_schema()
"""
class filter_schema:
    # Листовые поля, допустимые для сравнения
    __leaf: frozenset

    # Ссылочные свойства: имя поля -> класс связанной модели
    __links: dict

    def __init__(self, leaf: set = None, links: dict = None) -> None:
        self.__leaf = frozenset(leaf if leaf is not None else set())
        self.__links = dict(links if links is not None else {})

    """
    Базовая схема сущности: наименование и уникальный код
    """
    @staticmethod
    def base() -> "filter_schema":
        return filter_schema(leaf={"name", "unique_code"})

    """
    Независимая копия схемы с дополнительными ссылочными свойствами
    """
    def with_links(self, links: dict) -> "filter_schema":
        if not isinstance(links, dict):
            raise argument_exception("Ожидается словарь ссылочных свойств!")

        merged = dict(self.__links)
        merged.update(links)
        return filter_schema(leaf=set(self.__leaf), links=merged)

    """
    Листовые поля схемы
    """
    @property
    def leaf(self) -> frozenset:
        return self.__leaf

    """
    Ссылочные свойства схемы
    """
    @property
    def links(self) -> dict:
        return dict(self.__links)

    """
    Проверить путь поля: лист или цепочка вложенных ссылок.
    Каждая промежуточная часть — ссылка на связанную модель,
    последняя — листовое поле целевой схемы
    """
    def validate_path(self, path: str) -> None:
        if not isinstance(path, str):
            raise argument_exception(f"Некорректное поле для фильтрации: {path}!")

        parts = path.split(".")
        if len(parts) < 1 or any(part.strip() == "" for part in parts):
            raise argument_exception(f"Некорректное поле для фильтрации: {path}!")

        current = self
        last_index = len(parts) - 1

        for index, part in enumerate(parts):
            if index == last_index:
                if part not in current.__leaf:
                    raise argument_exception(
                        f"Недопустимое поле для фильтрации: {part}!"
                    )
                return

            if part not in current.__links:
                raise argument_exception(
                    f"Недопустимое вложенное поле для фильтрации: {part}!"
                )

            linked_type = current.__links[part]
            current = linked_type.filter_schema()
            if current is None:
                raise argument_exception(
                    f"Недопустимое вложенное поле для фильтрации: {part}!"
                )

    """
    Путь допустим для этой схемы (без исключения)
    """
    def is_valid_path(self, path: str) -> bool:
        try:
            self.validate_path(path)
            return True
        except argument_exception:
            return False
