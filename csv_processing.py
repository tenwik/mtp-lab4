"""Повышенное задание №8: фильтрация и преобразование CSV map/filter."""

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TypedDict

DATA_DIR = Path(__file__).resolve().parent / "data"


class Product(TypedDict):
    """Товар с названием и точной десятичной ценой."""

    name: str
    price: Decimal


def parse_product(row: dict[str, str]) -> Product:
    """Проверить CSV-строку и преобразовать текстовую цену в Decimal."""
    name = (row.get("name") or "").strip()
    try:
        price = Decimal(row.get("price") or "")
    except InvalidOperation as error:
        raise ValueError("Цена должна быть числом") from error
    if not name or not price.is_finite() or price < 0:
        raise ValueError("Нужны название и конечная неотрицательная цена")
    return {"name": name, "price": price}


def uppercase_name(product: Product) -> Product:
    """Вернуть новый товар с названием в верхнем регистре."""
    return {"name": product["name"].upper(), "price": product["price"]}


def process_csv(
    source: Path,
    destination: Path,
    min_price: Decimal = Decimal("1000"),
) -> int:
    """Сохранить товары с ценой >= min_price, преобразовав их названия.

    CSV должен иметь столбцы name,price и кодировку UTF-8 (BOM допустим).
    Вернуть число сохранённых товаров. Ошибочные данные вызывают ValueError
    до открытия выходного файла; исходный файл нельзя перезаписать.
    """
    if source.resolve() == destination.resolve():
        raise ValueError("Исходный и выходной файлы должны различаться")
    if not min_price.is_finite() or min_price < 0:
        raise ValueError("Минимальная цена должна быть конечной и >= 0")
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["name", "price"]:
            raise ValueError("Ожидается заголовок CSV: name,price")
        products = map(parse_product, reader)
        selected = filter(lambda item: item["price"] >= min_price, products)
        result = list(map(uppercase_name, selected))

    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["name", "price"])
        writer.writeheader()
        writer.writerows(result)
    return len(result)


def main() -> None:
    """Обработать учебный CSV независимо от текущего рабочего каталога."""
    destination = DATA_DIR / "processed_products.csv"
    count = process_csv(DATA_DIR / "products.csv", destination)
    print(f"CSV: сохранено товаров — {count}; файл: {destination.name}")


if __name__ == '__main__':
    main()
