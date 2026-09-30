"""Повышенное задание №6: декоратор с параметром числа повторений."""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def repeat(times: int) -> Callable[[Callable[P, R]], Callable[P, list[R]]]:
    """Создать декоратор, вызывающий функцию times раз и собирающий ответы.

    times должен быть положительным целым числом. Исключение исходной
    функции передаётся вызывающему коду и прекращает повторы.
    """
    if isinstance(times, bool) or not isinstance(times, int):
        raise TypeError("Число повторений должно быть целым числом")
    if times < 1:
        raise ValueError("Число повторений должно быть положительным")

    def decorator(function: Callable[P, R]) -> Callable[P, list[R]]:
        """Обернуть функцию повторяющимися вызовами."""
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> list[R]:
            """Выполнить заданное количество вызовов с теми же аргументами."""
            return [function(*args, **kwargs) for _ in range(times)]

        return wrapper

    return decorator


@repeat(times=3)
def greet(name: str) -> str:
    """Сформировать приветствие."""
    return f"Здравствуйте, {name}!"


def main() -> None:
    """Показать три результата декорированной функции."""
    print("Повторение:", greet("Георгий"))


if __name__ == '__main__':
    main()
