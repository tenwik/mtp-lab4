"""Среднее задание №5: генератор чисел Фибоначчи."""

from collections.abc import Iterator


def fibonacci(count: int) -> Iterator[int]:
    """Выдать count чисел Фибоначчи, начиная с 0 и 1.

    При отрицательном count ошибка возникает при начале итерации.
    """
    if count < 0:
        raise ValueError("Количество чисел не может быть отрицательным")
    first, second = 0, 1
    for _ in range(count):
        yield first
        first, second = second, first + second


def main() -> None:
    """Показать первые десять чисел последовательности."""
    print("Фибоначчи:", list(fibonacci(10)))


if __name__ == '__main__':
    main()
