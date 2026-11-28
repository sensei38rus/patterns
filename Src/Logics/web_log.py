import functools
import time
from flask import has_request_context, request
from Src.Logics.log_publisher import log_publisher

"""
Декоратор регистрации вызовов web методов в журнале операций
(категория WEB, шаблон проектирования "Наблюдатель").

Обработчик REST API оборачивается декоратором: после выполнения
фиксируется наименование метода, параметры запроса, код ответа,
время обработки и ошибка (если метод завершился исключением).
Исключение после регистрации пробрасывается дальше без изменений
"""
def web_log(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        started = time.perf_counter()
        status = 200
        error = ""

        try:
            result = func(*args, **kwargs)
            status = __status_code(result)
            return result
        except Exception as ex:
            error = str(ex)
            status = 500
            raise
        finally:
            details = __details(kwargs, status, started)
            if error:
                details["error"] = error

            # Метод завершился ошибкой: исключение либо код ответа 4xx/5xx
            failed = error != "" or status >= 400
            if failed and not error:
                error = f"Web метод завершился с кодом {status}"

            log_publisher().web(
                func.__name__,
                entity=str(kwargs.get("entity", "") or ""),
                unique_code=str(kwargs.get("unique_code", "") or ""),
                message=error if failed else "Вызов web метода",
                status="error" if failed else "success",
                details=details
            )

    return wrapper


"""
Определить код ответа web метода.
Обработчики возвращают кортеж (данные, код[, заголовки]) либо данные
"""
def __status_code(result) -> int:
    if isinstance(result, tuple) and len(result) >= 2 and isinstance(result[1], int):
        return result[1]

    return 200


"""
Собрать детали вызова: параметры запроса, код ответа, время обработки
и сведения о запросе (метод и путь), если есть контекст запроса
"""
def __details(kwargs: dict, status: int, started: float) -> dict:
    parameters = {}
    for key, value in kwargs.items():
        # Тело запроса заменяется списком ключей: журнал не должен хранить данные целиком
        parameters[key] = sorted(value.keys()) if isinstance(value, dict) else value

    result = {
        "status_code": status,
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
        "parameters": parameters
    }

    if has_request_context():
        result["http_method"] = request.method
        result["http_path"] = request.path

    return result
