from Src.Core.abstract_model import abstact_model

"""
Сервис построения реестра доменных сущностей (код -> модель).
Используется при десериализации запросов для разрешения ссылок
на существующие сущности
"""
class registry_service:

    """
    Построить реестр всех сущностей из данных хранилища
    """
    @staticmethod
    def build(data: dict) -> dict:
        result = {}
        for items in data.values():
            for item in items:
                if isinstance(item, abstact_model):
                    result[ item.unique_code ] = item
        return result
