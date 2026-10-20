"""Génère un jeu de données FICTIF de ventes retail (reproductible).

Les données sont synthétiques : elles servent uniquement à démontrer le pipeline.
Des défauts volontaires (doublons, valeurs manquantes, quantités négatives, dates
invalides) sont injectés pour que l'étape de nettoyage ait un vrai travail à faire.
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path("data/raw")

CITIES = ["Casablanca", "Rabat", "Salé", "Marrakech", "Tanger", "Fès"]
PRODUCTS = [
    ("Thé à la menthe 500g", "Alimentaire", 38.0),
    ("Huile d'olive 1L", "Alimentaire", 85.0),
    ("Dattes Medjool 1kg", "Alimentaire", 120.0),
    ("Couscous 1kg", "Alimentaire", 22.0),
    ("Savon noir beldi", "Hygiène", 30.0),
    ("Huile d'argan 100ml", "Hygiène", 150.0),
    ("Shampoing 400ml", "Hygiène", 45.0),
    ("Tajine en terre cuite", "Maison", 180.0),
    ("Théière inox", "Maison", 140.0),
    ("Tapis berbère", "Maison", 650.0),
    ("Écouteurs Bluetooth", "Électronique", 250.0),
    ("Chargeur rapide USB-C", "Électronique", 120.0),
]


def generate(seed: int = 42, n_sales: int = 20_000) -> None:
    rng = np.random.default_rng(seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    products = pd.DataFrame(PRODUCTS, columns=["product_name", "category", "unit_price"])
    products.insert(0, "product_id", range(1, len(products) + 1))
    stores = pd.DataFrame({"store_id": range(1, len(CITIES) + 1), "city": CITIES})

    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    # saisonnalité simple : pics au printemps et en été
    month_weight = np.array([0.8, 0.8, 0.9, 1.3, 1.1, 1.0, 1.3, 1.4, 1.0, 0.9, 0.9, 1.1])
    w = month_weight[dates.month - 1]
    w = w / w.sum()

    sales = pd.DataFrame({
        "sale_id": range(1, n_sales + 1),
        "sale_date": rng.choice(dates, size=n_sales, p=w),
        "store_id": rng.choice(stores["store_id"], size=n_sales, p=[0.28, 0.2, 0.1, 0.17, 0.13, 0.12]),
        "product_id": rng.choice(products["product_id"], size=n_sales),
        "quantity": rng.integers(1, 6, size=n_sales),
        "discount": rng.choice([0, 0, 0, 0.05, 0.1, 0.2], size=n_sales),
    })
    sales["sale_date"] = pd.to_datetime(sales["sale_date"]).dt.strftime("%Y-%m-%d")

    # --- défauts volontaires pour tester le nettoyage ---
    dirty = pd.concat([sales, sales.sample(150, random_state=1)], ignore_index=True)       # doublons
    dirty.loc[dirty.sample(100, random_state=2).index, "quantity"] = -1                    # quantités invalides
    dirty.loc[dirty.sample(80, random_state=3).index, "store_id"] = np.nan                 # magasin manquant
    dirty.loc[dirty.sample(60, random_state=4).index, "sale_date"] = "date_invalide"       # dates invalides

    products.to_csv(RAW_DIR / "products.csv", index=False)
    stores.to_csv(RAW_DIR / "stores.csv", index=False)
    dirty.to_csv(RAW_DIR / "sales_raw.csv", index=False)
    print(f"Données générées dans {RAW_DIR}/ ({len(dirty)} lignes de ventes brutes)")


if __name__ == "__main__":
    generate()
