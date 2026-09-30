"""Среднее задание №7: логирование вызовов функции."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
LOGGER = logging.getLogger(__name__)


def log_call(function: Callable[P, R]) -> Callable[P, R]:
    """Записать имя и аргументы перед вызовом, сохранив результат функции."""
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """Зарегистрировать вызов и передать управление исходной функции."""
        LOGGER.info(
            "Вызов %s: args=%r, kwargs=%r",
            function.__name__, args, kwargs,
        )
        return function(*args, **kwargs)

    return wrapper


@log_call
def add(first: int, second: int) -> int:
    """Вернуть сумму двух целых чисел."""
    return first + second


def main() -> None:
    """Продемонстрировать логирование вызова с именованным аргументом."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("Сумма:", add(3, second=5))


if __name__ == '__main__':
    main()
