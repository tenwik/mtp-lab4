"""Общая демонстрация пяти заданий ЛР4, вариант 5."""

import csv_processing
import fibonacci
import logging_decorator
import parameterized_decorator
import squares


def main() -> None:
    """Последовательно запустить все задания лабораторной работы."""
    fibonacci.main()
    logging_decorator.main()
    squares.main()
    parameterized_decorator.main()
    csv_processing.main()


if __name__ == '__main__':
    main()
