import pandas as pd

from src.etl import clean_sales

PRODUCTS = pd.DataFrame({"product_id": [1, 2], "product_name": ["A", "B"], "category": ["x", "y"], "unit_price": [100.0, 50.0]})
STORES = pd.DataFrame({"store_id": [1, 2], "city": ["Rabat", "Salé"]})


def make(rows):
    return pd.DataFrame(rows, columns=["sale_id", "sale_date", "store_id", "product_id", "quantity", "discount"])


def test_revenue_is_computed_with_discount():
    df = clean_sales(make([[1, "2024-01-05", 1, 1, 2, 0.1]]), PRODUCTS, STORES)
    assert df.loc[0, "revenue"] == 180.0  # 2 x 100 x 0.9


def test_duplicates_are_removed():
    row = [1, "2024-01-05", 1, 1, 2, 0.0]
    df = clean_sales(make([row, row]), PRODUCTS, STORES)
    assert len(df) == 1


def test_invalid_rows_are_rejected():
    rows = [
        [1, "2024-01-05", 1, 1, 2, 0.0],         # valide
        [2, "date_invalide", 1, 1, 2, 0.0],      # date invalide
        [3, "2024-01-06", 1, 1, -1, 0.0],        # quantité négative
        [4, "2024-01-07", None, 1, 1, 0.0],      # magasin manquant
        [5, "2024-01-08", 99, 1, 1, 0.0],        # magasin inexistant
    ]
    df = clean_sales(make(rows), PRODUCTS, STORES)
    assert list(df["sale_id"]) == [1]
