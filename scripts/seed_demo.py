from datetime import date
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine
from app.models import Budget, Category, Movement, SavingsGoal


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Category).count() > 0:
            print("Ya existen datos, seed omitido.")
            return

        categories = [
            Category(name="Sueldo", movement_type="income"),
            Category(name="Freelance", movement_type="income"),
            Category(name="Comida", movement_type="expense"),
            Category(name="Transporte", movement_type="expense"),
            Category(name="Servicios", movement_type="expense"),
        ]
        db.add_all(categories)
        db.flush()

        cat_map = {c.name: c.id for c in categories}

        movements = [
            Movement(
                movement_date=date(2026, 4, 1),
                amount=3500,
                movement_type="income",
                payment_method="transferencia",
                note="Sueldo abril",
                category_id=cat_map["Sueldo"],
            ),
            Movement(
                movement_date=date(2026, 4, 3),
                amount=45.5,
                movement_type="expense",
                payment_method="yape",
                note="Almuerzo",
                category_id=cat_map["Comida"],
            ),
            Movement(
                movement_date=date(2026, 4, 4),
                amount=20,
                movement_type="expense",
                payment_method="efectivo",
                note="Bus",
                category_id=cat_map["Transporte"],
            ),
            Movement(
                movement_date=date(2026, 4, 5),
                amount=120,
                movement_type="expense",
                payment_method="tarjeta",
                note="Internet",
                category_id=cat_map["Servicios"],
            ),
        ]
        db.add_all(movements)

        budgets = [
            Budget(year=2026, month=4, category_id=cat_map["Comida"], limit_amount=600),
            Budget(year=2026, month=4, category_id=cat_map["Transporte"], limit_amount=250),
            Budget(year=2026, month=4, category_id=cat_map["Servicios"], limit_amount=300),
        ]
        db.add_all(budgets)

        db.add(
            SavingsGoal(
                name="Fondo de emergencia",
                target_amount=5000,
                current_amount=1200,
            )
        )

        db.commit()
        print("Datos demo cargados.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
