import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


class settings_manager(abstract_manager):
    __default_file_name: str = "settings.json"

    _settings: settings_model = None
    __is_loaded: bool = False
    __data: dict = None

    def __new__(cls):
        # Реализация паттерна Singleton через атрибут класса
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def load(self, file_name: str = "") -> None:
        """Загружает данные настроек из JSON файла."""
        target_file = file_name.strip() if file_name and file_name.strip() else self.__default_file_name
        validator.validate(target_file, str)

        try:
            with open(target_file, mode="r", encoding="utf-8") as file:
                self.__data = json.load(file)

            self.__is_loaded = self.convert()
        except Exception as error:
            raise operation_exception(
                f"Ошибка при загрузке данных из файла {target_file}: {error}"
            ) from error

    def convert(self) -> bool:
        """Преобразует сырые данные JSON в объект settings_model."""
        if not isinstance(self.__data, dict):
            return False

        try:
            if self._settings is None:
                self._settings = settings_model()

            # 1. Заполнение данных организации
            org_data = self.__data.get("organization")
            if isinstance(org_data, dict):
                org_name = str(org_data.get("name", "")).strip()
                org_inn = str(org_data.get("inn", "")).strip()

                if org_name and org_inn:
                    try:
                        self._settings.organization = organization_model(**org_data)
                    except Exception:
                        pass

            # 2. Заполнение ответственных лиц
            for field in ("boss_name", "account_name"):
                val = self.__data.get(field)
                if val is not None and str(val).strip():
                    setattr(self._settings, field, str(val).strip())

            # 3. Флаг первого запуска
            if "is_first_start" in self.__data:
                self._settings.is_first_start = bool(self.__data["is_first_start"])

            return True
        except Exception:
            return False

    @property
    def is_loaded(self) -> bool:
        """Флаг успешности загрузки настроек."""
        return self.__is_loaded

    @property
    def settings(self) -> settings_model:
        """Объект настроек settings_model."""
        return self._settings