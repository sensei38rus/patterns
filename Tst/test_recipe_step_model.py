import pytest
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.recipe_step_model import recipe_step_model


"""
Набор модульных тестов для класса recipe_step_model
"""


def test_success_recipe_step_model_full_creation():
    """
    Ожидание: Успешное создание шага технологического процесса с полным набором параметров.
    Метод: recipe_step_model.__init__
    Описание: Шаг содержит наименование, порядковый номер и описание действий
              (шаблон из Docs/Recipe.md).
    """
    # Arrange (Подготовка)

    # Act (Действие)
    step = recipe_step_model("Подготовка сырья", 1, "Проверить сроки годности, муку просеять.")

    # Assert (Проверка)
    assert step.name == "Подготовка сырья"
    assert step.order == 1
    assert step.description == "Проверить сроки годности, муку просеять."


def test_argument_exception_recipe_step_model_empty_name():
    """
    Ожидание: Выброс argument_exception при пустом наименовании шага.
    Метод: abs_mod.name (setter)
    Описание: Наименование шага наследуется от abs_mod и не может быть пустым.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_step_model("", 1, "Проверить сроки годности.")


def test_max_length_exception_recipe_step_model_name_too_long():
    """
    Ожидание: Выброс max_length_exception при наименовании длиннее 50 символов.
    Метод: abs_mod.name (setter)
    Описание: Наименование шага ограничено 50 символами базового класса abs_mod.
    """
    # Arrange (Подготовка)
    too_long_name = "А" * 51

    # Act & Assert (Действие и Проверка)
    with pytest.raises(max_length_exception):
        recipe_step_model(too_long_name, 1, "Проверить сроки годности.")


def test_argument_exception_recipe_step_model_zero_order():
    """
    Ожидание: Выброс argument_exception при нулевом порядке шага.
    Метод: recipe_step_model.order (setter)
    Описание: Нумерация шагов начинается с 1.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_step_model("Подготовка сырья", 0, "Проверить сроки годности.")


def test_argument_exception_recipe_step_model_negative_order():
    """
    Ожидание: Выброс argument_exception при отрицательном порядке шага.
    Метод: recipe_step_model.order (setter)
    Описание: Отрицательные порядковые номера недопустимы.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_step_model("Подготовка сырья", -1, "Проверить сроки годности.")


def test_argument_exception_recipe_step_model_non_integer_order():
    """
    Ожидание: Выброс argument_exception при дробном порядке шага.
    Метод: recipe_step_model.order (setter)
    Описание: Порядковый номер должен быть целым числом.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_step_model("Подготовка сырья", 1.5, "Проверить сроки годности.")


def test_argument_exception_recipe_step_model_empty_description():
    """
    Ожидание: Выброс argument_exception при пустом описании шага.
    Метод: recipe_step_model.description (setter)
    Описание: Описание действий - обязательный реквизит шага.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_step_model("Подготовка сырья", 1, "")


def test_argument_exception_recipe_step_model_invalid_description_type():
    """
    Ожидание: Выброс argument_exception при нестроковом описании.
    Метод: recipe_step_model.description (setter)
    Описание: Поле description должно быть строкой.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        recipe_step_model("Подготовка сырья", 1, 12345)


def test_success_recipe_step_model_boundary_1000_description():
    """
    Ожидание: Успешное создание шага с описанием ровно в 1000 символов.
    Метод: recipe_step_model.description (setter)
    Описание: Граничное значение - описание в 1000 символов допустимо.
    """
    # Arrange (Подготовка)
    long_description = "А" * 1000

    # Act (Действие)
    step = recipe_step_model("Замес творожной массы", 2, long_description)

    # Assert (Проверка)
    assert len(step.description) == 1000


def test_max_length_exception_recipe_step_model_description_too_long():
    """
    Ожидание: Выброс max_length_exception при описании длиннее 1000 символов.
    Метод: recipe_step_model.description (setter)
    Описание: Описание шага ограничено 1000 символами.
    """
    # Arrange (Подготовка)
    too_long_description = "А" * 1001

    # Act & Assert (Действие и Проверка)
    with pytest.raises(max_length_exception):
        recipe_step_model("Замес творожной массы", 2, too_long_description)
