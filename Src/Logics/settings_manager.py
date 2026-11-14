from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
import json
import os
import uuid
from Src.Models.settings_model import settings_model
from Src.Models.company_model import company_model
from Src.Logics.convertor import convertor

"""
Менеджер для работы с настройками
"""
class settings_manager(abstract_manager):
    # Наименование файла по умолчанию
    __default_file_name:str = "settings.json"
    # Настройки
    __settings:settings_model = None
    # Загруженные сырые данные
    __data:dict = {} 
    # Информация об ошибке при загрузке
    __inner_error:str = ""

    def __init__(self):
        self.__settings = settings_model()

    # Singletone
    def __new__(cls):
          if not hasattr(cls, 'instance'):
                  cls.instance = super(settings_manager, cls).__new__(cls)
          return cls.instance 
  
    """
    Загрузка данных
    """
    def load(self, file_name:str = ""):

        # Определим название фала
        inner_file_name = file_name if file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name, str)

        # Дополним имя с учетом текщего каталога
        full_file_name = os.path.abspath(inner_file_name)        
        if not os.path.exists(full_file_name):
            raise operation_exception(f'Не найден указанный файл {full_file_name}')

        try:
            with open(full_file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)
                self.is_loaded = self.build()
                if not self.is_loaded:
                    self.__settings = self.__create_default_data() 
        except Exception as ex:
            raise  operation_exception(f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}")      

    """
    Модель настроек
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Обработать загруженные данные.
    Данные десериализуются общим механизмом (convertor) по тому же
    принципу, что и доменные сущности хранилища
    """
    def build(self) -> bool:
        if len(self.__data) == 0:
              return False

        try: 
            payload = settings_manager.__to_domain_payload(self.__data)
            self.__settings = convertor().deserialize(payload)
            return True        
        except Exception as ex:
            self.__inner_error = str(ex)
            raise operation_exception(f"Ошибка десериализации настроек. Детали: {ex}")          


    """
    Привести загруженные данные к формату доменной модели.
    Поддерживается формат с маркером типа ({"type": ...}) и плоский формат
    старого образца, где данные организации вынесены в ключи "company_*"
    """
    @staticmethod
    def __to_domain_payload(data: dict) -> dict:
        if not isinstance(data, dict):
            raise operation_exception("Настройки должны быть представлены словарем!")

        # Данные уже описаны в формате доменной модели
        if "type" in data:
            return data

        payload = {
            "type": settings_model().type,
            "unique_code": uuid.uuid4().hex
        }

        company_payload = {}
        for key, value in data.items():
            if key.startswith("company_"):
                company_payload[ key[ len("company_") : ] ] = value
            else:
                payload[ key ] = value

        # Данные организации преобразуются во вложенную доменную модель
        if len(company_payload) > 0:
            company = company_model()
            company_payload.setdefault("type", company.type)
            company_payload.setdefault("unique_code", company.unique_code)
            payload["company"] = company_payload

        return payload


    """
    Сформировать настройки по умолчанию
    """
    def __create_default_data(self) -> settings_model:
        result = settings_model()

        company = company_model()
        company.bik = "044525225"
        company.inn = 123456789999
        company.corr_account = 30101810400000000225
        company.name = " Сбербанка (Москва)"
        company.account = 40812810400000000225

        result.company = company
        result.boss_name = "Воловиков Александр Сергеевич"
        result.account_name = "Балахчи Анна Георгиевна"

        return result
