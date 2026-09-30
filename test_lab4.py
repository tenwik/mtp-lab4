"""Проверки результатов и граничных случаев пяти заданий ЛР4."""

import csv
import unittest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from csv_processing import DATA_DIR, process_csv
from fibonacci import fibonacci
from logging_decorator import log_call
from parameterized_decorator import repeat
from squares import squares


class FibonacciTests(unittest.TestCase):
    """Проверки последовательности и ленивой выдачи чисел."""

    def test_sequence(self) -> None:
        """Первые десять чисел совпадают с известной последовательностью."""
        self.assertEqual(
            list(fibonacci(10)), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34],
        )

    def test_boundaries(self) -> None:
        """Ноль, одно число и отрицательное количество обработаны явно."""
        self.assertEqual(list(fibonacci(0)), [])
        self.assertEqual(list(fibonacci(1)), [0])
        with self.assertRaises(ValueError):
            list(fibonacci(-1))

    def test_lazy(self) -> None:
        """Большой count не требует заранее вычислять все числа."""
        generator = fibonacci(10 ** 12)
        self.assertIs(iter(generator), generator)
        self.assertEqual([next(generator), next(generator)], [0, 1])


class LoggingTests(unittest.TestCase):
    """Проверки лога и сохранения поведения исходной функции."""

    def test_arguments_result_and_metadata(self) -> None:
        """Аргументы логируются, результат и метаданные сохраняются."""
        @log_call
        def subtract(first: int, second: int = 1) -> int:
            """Вычесть второе число из первого."""
            return first - second

        with self.assertLogs("logging_decorator", level="INFO") as captured:
            self.assertEqual(subtract(8, second=3), 5)
        self.assertIn("subtract", captured.output[0])
        self.assertIn("args=(8,)", captured.output[0])
        self.assertIn("'second': 3", captured.output[0])
        self.assertEqual(subtract.__name__, "subtract")
        self.assertEqual(subtract.__doc__, "Вычесть второе число из первого.")

    def test_exception(self) -> None:
        """Декоратор не подавляет исключение исходной функции."""
        @log_call
        def fail() -> None:
            """Сгенерировать тестовую ошибку."""
            raise RuntimeError("Ошибка")

        with self.assertLogs("logging_decorator", level="INFO"):
            with self.assertRaises(RuntimeError):
                fail()


class SquaresTests(unittest.TestCase):
    """Проверка квадратов диапазона 1–10."""

    def test_squares(self) -> None:
        """Список содержит десять ожидаемых квадратов."""
        self.assertEqual(squares(), [1, 4, 9, 16, 25, 36, 49, 64, 81, 100])


class RepeatTests(unittest.TestCase):
    """Проверки параметризованного декоратора."""

    def test_call_count_and_arguments(self) -> None:
        """Функция реально вызывается три раза с переданными аргументами."""
        calls: list[int] = []

        @repeat(times=3)
        def record(value: int) -> int:
            """Запомнить аргумент и вернуть текущий номер вызова."""
            calls.append(value)
            return len(calls)

        self.assertEqual(record(value=7), [1, 2, 3])
        self.assertEqual(calls, [7, 7, 7])
        self.assertEqual(record.__name__, "record")

    def test_invalid_times(self) -> None:
        """Неположительный параметр отклоняется при создании декоратора."""
        for times in (0, -1):
            with self.subTest(times=times), self.assertRaises(ValueError):
                repeat(times)

    def test_once_and_exception(self) -> None:
        """Один повтор допустим, ошибка останавливает следующие вызовы."""
        self.assertEqual(repeat(1)(lambda: 4)(), [4])
        calls: list[int] = []

        @repeat(3)
        def fail() -> None:
            """Записать попытку и завершиться ошибкой."""
            calls.append(1)
            raise RuntimeError("Ошибка")

        with self.assertRaises(RuntimeError):
            fail()
        self.assertEqual(calls, [1])


class CsvTests(unittest.TestCase):
    """Проверки реальных CSV-файлов во временном каталоге."""

    def test_sample(self) -> None:
        """Порог включается, кириллица и запятая внутри имени сохраняются."""
        with TemporaryDirectory() as directory:
            output = Path(directory) / "result.csv"
            self.assertEqual(process_csv(DATA_DIR / "products.csv", output), 3)
            with output.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows, [
                {"name": "МЫШЬ", "price": "1000.00"},
                {"name": "КЛАВИАТУРА", "price": "3500.00"},
                {"name": "МОНИТОР, 24 ДЮЙМА", "price": "15000.00"},
            ])

    def test_empty_selection_and_header_only(self) -> None:
        """Пустой результат остаётся корректным CSV с заголовком."""
        with TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            output = Path(directory) / "result.csv"
            for content in ("name,price\n", "name,price\nТовар,1\n"):
                source.write_text(content, encoding="utf-8-sig")
                self.assertEqual(process_csv(source, output), 0)
                self.assertEqual(output.read_text(encoding="utf-8"),
                                 "name,price\n")

    def test_invalid_csv(self) -> None:
        """Неверные данные не повреждают существующий выходной файл."""
        with TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            output = Path(directory) / "result.csv"
            output.write_text("original", encoding="utf-8")
            for content in (
                "", "title,cost\n", "name,price\nТовар,text\n",
                "name,price\nТовар,-1\n", "name,price\nТовар,NaN\n",
                "name,price\nТовар,Infinity\n", "name,price\n,10\n",
                "name,price\nТовар\n",
            ):
                with self.subTest(content=content):
                    source.write_text(content, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        process_csv(source, output)
                    self.assertEqual(output.read_text(encoding="utf-8"),
                                     "original")

    def test_same_file_and_invalid_threshold(self) -> None:
        """Перезапись источника и некорректный порог запрещены."""
        with TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            output = Path(directory) / "result.csv"
            source.write_text("name,price\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                process_csv(source, source)
            for threshold in (Decimal("-1"), Decimal("NaN")):
                with self.assertRaises(ValueError):
                    process_csv(source, output, threshold)


if __name__ == '__main__':
    unittest.main()
