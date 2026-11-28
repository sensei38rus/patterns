from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception, argument_exception
import json
import os
import uuid
from enum import Enum
from Src.Models.settings_model import settings_model
from Src.Models.company_model import company_model
from Src.Core.abstract_model import abstact_model
from Src.Core.common import common
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.convertor import convertor
from Src.Logics.log_publisher import log_publisher

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
    Загрузка данных.
    Успешная загрузка и ошибка фиксируются в журнале операций
    """
    def load(self, file_name:str = ""):

        # Определим название фала
        inner_file_name = file_name if file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name, str)

        # Дополним имя с учетом текщего каталога
        full_file_name = os.path.abspath(inner_file_name)        
        if not os.path.exists(full_file_name):
            message = f'Не найден указанный файл {full_file_name}'
            self.__log("load", "error", message, {"file": full_file_name})
            raise operation_exception(message)

        try:
            with open(full_file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)
                self.is_loaded = self.build()
                if not self.is_loaded:
                    self.__settings = self.__create_default_data() 
        except Exception as ex:
            message = f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}"
            self.__log("load", "error", message, {"file": full_file_name})
            raise operation_exception(message)

        self.__log("load", "success", "Настройки загружены", {
            "file": full_file_name,
            "parameters": self.__parameters()
        })

    """
    Модель настроек
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Изменить параметры настроек.
    data - словарь изменяемых параметров: boss_name, account_name,
    first_start, default_report_type, company.
    Неизвестный параметр или некорректное значение приводят к
    argument_exception, при этом частично примененные параметры
    откатываются к прежним значениям.
    Изменение фиксируется в журнале операций (категория SETTINGS)
    """
    def update(self, data: dict) -> settings_model:
        if not isinstance(data, dict) or len(data) == 0:
            raise argument_exception("Ожидается непустой словарь параметров настроек!")

        unknown = [key for key in data.keys() if key not in self.__parameters()]
        if len(unknown) > 0:
            message = f"Неизвестные параметры настроек: {', '.join(sorted(unknown))}!"
            self.__log("update", "error", message, {"parameters": sorted(unknown)})
            raise argument_exception(message)

        # Прежние значения параметров: используются для отката и журнала
        previous = {key: getattr(self.__settings, key) for key in data.keys()}

        try:
            for key, value in data.items():
                setattr(self.__settings, key, self.__convert(key, value))
        except (argument_exception, operation_exception, ValueError, TypeError) as ex:
            # Откат уже примененных параметров
            for key, value in previous.items():
                try:
                    setattr(self.__settings, key, value)
                except Exception:
                    continue

            self.__log("update", "error", str(ex), {"parameters": sorted(data.keys())})
            raise

        changed = sorted([key for key in data.keys() if previous[key] != getattr(self.__settings, key)])
        self.__log("update", "success", "Изменение параметров настроек", {
            "parameters": sorted(data.keys()),
            "changed": changed,
            "before": {key: self.__dump(previous[key]) for key in changed},
            "after": {key: self.__dump(getattr(self.__settings, key)) for key in changed}
        })

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
            self.__settings = settings_manager.__to_domain_payload(self.__data)
            return True        
        except Exception as ex:
            self.__inner_error = str(ex)
            raise operation_exception(f"Ошибка десериализации настроек. Детали: {ex}")          


    """
    Привести загруженные данные к доменной модели настроек.
    Поддерживается формат с маркером типа ({"type": ...}) и плоский формат
    старого образца, где данные организации вынесены в ключи "company_*".
    Готовый payload десериализуется общим механизмом (convertor) по тому же
    принципу, что и доменные сущности хранилища
    """
    @staticmethod
    def __to_domain_payload(data: dict) -> settings_model:
        if not isinstance(data, dict):
            raise operation_exception("Настройки должны быть представлены словарем!")

        # Дамп общего механизма сериализации ({"result": {...}})
        if "type" not in data and isinstance(data.get("result"), dict):
            data = data["result"]

        # Данные уже описаны в формате доменной модели
        if "type" in data:
            payload = dict(data)
            # Маркер уникального кода обязателен для распознавания доменной модели
            payload.setdefault("unique_code", uuid.uuid4().hex)

            # Вложенной организации добавляем маркеры доменной модели
            company = payload.get("company")
            if isinstance(company, dict):
                company = dict(company)
                marker = company_model()
                company.setdefault("type", marker.type)
                company.setdefault("unique_code", marker.unique_code)
                payload["company"] = company
        else:
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

        # Десериализация построенного payload в доменную модель
        result = convertor().deserialize(payload)
        if not isinstance(result, settings_model):
            raise operation_exception("Некорректный формат настроек: не удалось выполнить десериализацию!")

        return result


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


    """
    Список изменяемых параметров настроек.
    Служебные поля доменной модели (уникальный код, маркер типа) не изменяются
    """
    @staticmethod
    def __parameters() -> list:
        return [
            name for name in common.get_fields(settings_model())
            if name not in ("unique_code", "type")
        ]


    """
    Привести значение изменяемого параметра к ожидаемому типу.
    Ошибка преобразования приводит к argument_exception
    """
    @staticmethod
    def __convert(key: str, value):
        # Данные организации десериализуются в доменную модель
        if key == "company":
            if isinstance(value, company_model):
                return value
            if not isinstance(value, dict):
                raise argument_exception("Параметр company должен содержать данные организации!")

            payload = dict(value)
            marker = company_model()
            payload.setdefault("type", marker.type)
            payload.setdefault("unique_code", marker.unique_code)

            result = convertor().deserialize(payload)
            if not isinstance(result, company_model):
                raise argument_exception("Некорректные данные организации!")
            return result

        # Формат отчетов по умолчанию задается кодом из перечисления
        if key == "default_report_type":
            try:
                number = int(value)
            except (TypeError, ValueError):
                raise argument_exception("Формат отчетов по умолчанию должен быть числом!")

            if number not in [item.value for item in report_type_enum]:
                raise argument_exception(f"Неизвестный формат отчетов по умолчанию: {number}!")
            return number

        # Флаг первого старта принимает строковое представление Json
        if key == "first_start" and isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in ("true", "false"):
                return lowered == "true"

        return value


    """
    Представить значение параметра в виде, пригодном для журнала
    """
    @staticmethod
    def __dump(value) -> object:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, abstact_model):
            return value.unique_code
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        return str(value)


    """
    Зафиксировать операцию с настройками в журнале операций
    """
    def __log(self, operation: str, status: str, message: str, details: dict = None) -> None:
        log_publisher().settings(
            operation,
            entity=settings_model.__name__,
            unique_code=self.__settings.unique_code if self.__settings is not None else "",
            message=message,
            status=status,
            details=details
        )
