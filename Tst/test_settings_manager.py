from Src.Logics.settings_manager import settings_manager
from Src.Logics.convertor import convertor
from Src.Core.validator import operation_exception
from Src.Models.settings_model import settings_model
import pytest
import time
from Src.Dtos.report_type_enum import report_type_enum

"""
Проверить загрузку настроек. Нет исключения.
"""
def test_not_raise_settings_manager_load():
    # Подготовка
    manager = settings_manager()

    # Действие и проверки
    try:
        manager.load("./Tst/settings.json")
        assert True
    except operation_exception :
         assert False
    except:
        assert False  

"""
Проверить загрузку настроек. Настройки не пустые.
"""
def test_not_empty_settings_manager_load():
    # Подготовка
    manager = settings_manager()
    
    # Действие 
    try:
        manager.load("./Tst/settings.json")
    except:
          assert False  

    # Проверки
    assert manager.settings is not None

"""
Проверить работу шаблона Singletone
"""
def test_equals_settings_manager_create():
    # Подготовка
    instance1 = settings_manager()
    time.sleep(1)
    instance2 = settings_manager()

    # Действие

    # Проверка
    assert instance1 == instance2


"""
Проверить работу шаблона Singletone
"""
def test_equals_properties_settings_manager_create():
    # Подготовка
    instance1 = settings_manager()
    time.sleep(1)
    instance2 = settings_manager()

    # Действие

    # Проверка
    assert instance1.settings == instance2.settings

    

"""
Проверить загрузку и конвертацию данных
"""
def test_is_loaded_settings_manager_true():
    # Подготовка
    manager = settings_manager()
    
    # Действие
    manager.load("./Tst/settings.json")

    # Проверки
    assert manager.is_loaded == True


"""
Проверить загрузку default_report_type
"""
def test_default_report_type_settings_manager_true(): 
    # Подготовка
    manager = settings_manager()
        
    # Действие
    manager.load("./Tst/settings.json")
    
    # Проверки
    assert manager.settings.default_report_type == report_type_enum.CSV


"""
Проверить загрузку данных организации общим механизмом десериализации
"""
def test_company_settings_manager_load():
    # Подготовка
    manager = settings_manager()
        
    # Действие
    manager.load("./Tst/settings.json")
    
    # Проверки
    assert manager.settings.company is not None
    assert manager.settings.company.name == "ООО Ромашка"
    assert manager.settings.company.inn == 4354545


"""
Проверить round-trip настроек через общий механизм
сериализации / десериализации (convertor)
"""
def test_round_trip_settings_manager_convertor():
    # Подготовка
    manager = settings_manager()
    manager.load("./Tst/settings.json")
    settings = manager.settings

    # Действие
    restored = convertor().deserialize(convertor().serialize(settings))["result"]

    # Проверки
    assert isinstance(restored, settings_model)
    assert restored.boss_name == settings.boss_name
    assert restored.default_report_type == settings.default_report_type
    assert restored.first_start == settings.first_start
    assert restored.company is not None
    assert restored.company.name == settings.company.name
    assert restored.company.inn == settings.company.inn


"""
Проверить загрузку настроек из поврежденного файла. Ожидается исключение.
"""
def test_raise_operation_exception_settings_manager_load_broken_file(tmp_path):
    # Подготовка
    file = tmp_path / "settings.json"
    file.write_text('{"default_report_type": "не число"}', encoding="utf-8")
    manager = settings_manager()

    # Действие и проверки
    with pytest.raises(operation_exception):
        manager.load(str(file))