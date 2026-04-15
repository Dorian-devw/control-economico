import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.services.excel_export import export_monthly_report


def run(year: int, month: int):
    db = SessionLocal()
    try:
        report_file = export_monthly_report(db, year, month)
        print(f"Reporte generado: {report_file}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera reporte mensual Excel.")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    args = parser.parse_args()
    run(args.year, args.month)
