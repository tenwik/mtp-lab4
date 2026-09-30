"""Среднее задание №1: квадраты чисел от 1 до 10 через map."""


def squares() -> list[int]:
    """Вычислить квадраты чисел 1–10 с помощью map и lambda."""
    return list(map(lambda number: number ** 2, range(1, 11)))


def main() -> None:
    """Вывести вычисленные квадраты."""
    print("Квадраты 1–10:", squares())


if __name__ == '__main__':
    main()
