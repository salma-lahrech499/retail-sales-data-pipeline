"""Point d'entrée : génération -> ETL -> KPIs."""
from src import etl, generate_data, kpis

if __name__ == "__main__":
    generate_data.generate()
    etl.run()
    kpis.run()
