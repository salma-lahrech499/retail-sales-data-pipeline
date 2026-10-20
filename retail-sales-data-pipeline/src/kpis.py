"""Exécute les requêtes SQL de kpis.sql et produit des CSV + graphiques."""
import re
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = Path("data/retail.db")
SQL_PATH = Path("sql/kpis.sql")
REPORTS = Path("reports")
BLUE, ORANGE = "#1F3A5F", "#D2643C"


def load_queries(path: Path = SQL_PATH) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"--\s*name:\s*(\w+)\s*\n", text)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def run_queries(db_path: Path = DB_PATH) -> dict:
    queries = load_queries()
    with sqlite3.connect(db_path) as conn:
        return {name: pd.read_sql_query(sql, conn) for name, sql in queries.items()}


def make_charts(res: dict) -> None:
    REPORTS.mkdir(exist_ok=True)

    m = res["revenue_by_month"]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(m["month"], m["revenue"] / 1000, marker="o", color=BLUE, linewidth=2)
    ax.set_title("Chiffre d'affaires mensuel (en milliers de MAD)")
    ax.set_ylabel("kMAD")
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    fig.tight_layout()
    fig.savefig(REPORTS / "revenue_by_month.png", dpi=130)
    plt.close(fig)

    c = res["revenue_by_city"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(c["city"][::-1], c["revenue"][::-1] / 1000, color=ORANGE)
    ax.set_title("Chiffre d'affaires par ville (kMAD)")
    fig.tight_layout()
    fig.savefig(REPORTS / "revenue_by_city.png", dpi=130)
    plt.close(fig)

    p = res["top_products"].head(8)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(p["product_name"][::-1], p["revenue"][::-1] / 1000, color=BLUE)
    ax.set_title("Top produits par chiffre d'affaires (kMAD)")
    fig.tight_layout()
    fig.savefig(REPORTS / "top_products.png", dpi=130)
    plt.close(fig)


def run() -> None:
    res = run_queries()
    REPORTS.mkdir(exist_ok=True)
    for name, df in res.items():
        df.to_csv(REPORTS / f"{name}.csv", index=False)
    make_charts(res)
    total = res["revenue_by_month"]["revenue"].sum()
    print(f"KPIs générés dans {REPORTS}/ — CA total : {total:,.0f} MAD")


if __name__ == "__main__":
    run()
