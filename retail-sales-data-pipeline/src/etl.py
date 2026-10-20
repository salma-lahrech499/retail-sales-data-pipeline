"""ETL : nettoyage des données brutes puis chargement dans SQLite."""
import sqlite3
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
DB_PATH = Path("data/retail.db")
SCHEMA_PATH = Path("sql/schema.sql")


def clean_sales(sales: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les ventes et calcule le chiffre d'affaires.

    Règles de qualité :
      1. suppression des doublons exacts
      2. dates valides uniquement
      3. quantité strictement positive
      4. store_id et product_id doivent exister dans les dimensions
      5. revenue = quantité x prix unitaire x (1 - remise)
    """
    df = sales.drop_duplicates().copy()

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df = df.dropna(subset=["sale_date", "store_id", "product_id"])

    df = df[df["quantity"] > 0]
    df = df[df["store_id"].isin(stores["store_id"]) & df["product_id"].isin(products["product_id"])]

    df = df.merge(products[["product_id", "unit_price"]], on="product_id", how="left")
    df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)

    df["sale_date"] = df["sale_date"].dt.strftime("%Y-%m-%d")
    for col in ["sale_id", "store_id", "product_id", "quantity"]:
        df[col] = df[col].astype(int)

    cols = ["sale_id", "sale_date", "store_id", "product_id", "quantity", "discount", "revenue"]
    return df[cols].reset_index(drop=True)


def load_to_db(sales: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame, db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        products.to_sql("dim_product", conn, if_exists="append", index=False)
        stores.to_sql("dim_store", conn, if_exists="append", index=False)
        sales.to_sql("fact_sales", conn, if_exists="append", index=False)


def run() -> dict:
    sales_raw = pd.read_csv(RAW_DIR / "sales_raw.csv")
    products = pd.read_csv(RAW_DIR / "products.csv")
    stores = pd.read_csv(RAW_DIR / "stores.csv")

    sales = clean_sales(sales_raw, products, stores)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    sales.to_csv(PROCESSED_DIR / "sales_clean.csv", index=False)
    load_to_db(sales, products, stores)

    stats = {"raw_rows": len(sales_raw), "clean_rows": len(sales), "rejected_rows": len(sales_raw) - len(sales)}
    print(f"ETL terminé : {stats}")
    return stats


if __name__ == "__main__":
    run()
