from Src.Core.abstract_model import abstact_model
from Src.Core.common import common

"""
Сервис поиска ссылок между доменными сущностями.
Изолирует обход ссылочной структуры от хранения данных
"""
class reference_service:

    """
    Найти все сущности хранилища, которые ссылаются на указанную.
    Проверяются свойства-модели, списки и вложенные структуры
    """
    @staticmethod
    def find(data: dict, target: abstact_model) -> list:
        result = []
        if not isinstance(target, abstact_model):
            return result

        visited = set()
        for key, items in data.items():
            for item in items:
                if item is target:
                    continue
                if reference_service.__has_reference(item, target.unique_code, visited):
                    result.append({
                        "entity": key,
                        "unique_code": item.unique_code,
                        "name": str(getattr(item, "name", ""))
                    })

        return result


    """
    Проверить, содержит ли значение ссылку на сущность с указанным кодом
    """
    @staticmethod
    def __has_reference(value, target_code: str, visited: set) -> bool:
        if isinstance(value, abstact_model):
            if value.unique_code == target_code:
                return True

            if id(value) in visited:
                return False
            visited.add(id(value))

            for field in common.get_fields(value, is_common=False):
                if reference_service.__has_reference(getattr(value, field, None), target_code, visited):
                    return True
            return False

        if isinstance(value, (list, tuple, set)):
            return any(reference_service.__has_reference(item, target_code, visited) for item in value)

        if isinstance(value, dict):
            return any(reference_service.__has_reference(item, target_code, visited) for item in value.values())

        return False
