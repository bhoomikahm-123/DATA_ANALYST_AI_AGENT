import pandas as pd
import sqlite3
import requests

def import_data(source, source_type="csv"):
    try:
        if source_type == "csv":
            df = pd.read_csv(source)
        elif source_type == "excel":
            df = pd.read_excel(source)
        elif source_type == "sql":
            conn = sqlite3.connect(source)
            df = pd.read_sql_query("SELECT * FROM table_name", conn)
        elif source_type == "api":
            response = requests.get(source)
            df = pd.DataFrame(response.json())
        else:
            raise ValueError("Unsupported source type.")
        print("✅ Data imported successfully!")
        return df
    except Exception as e:
        print("❌ Error importing data:", e)
        return None
