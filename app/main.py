from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, engine, get_db
from app.services.excel_export import export_monthly_report

app = FastAPI(title="Control Economico Personal", version="0.1.0")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/categories", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.Category)
        .filter(models.Category.name == category.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="La categoria ya existe")
    return crud.create_category(db, category)


@app.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.list_categories(db)


@app.post("/movements", response_model=schemas.MovementOut)
def create_movement(movement: schemas.MovementCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == movement.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    if category.movement_type != movement.movement_type:
        raise HTTPException(
            status_code=400,
            detail="El tipo del movimiento no coincide con la categoria",
        )
    return crud.create_movement(db, movement)


@app.get("/movements", response_model=list[schemas.MovementOut])
def list_movements(year: int | None = None, month: int | None = None, db: Session = Depends(get_db)):
    return crud.list_movements(db, year, month)


@app.post("/budgets", response_model=schemas.BudgetOut)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == budget.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    if category.movement_type != "expense":
        raise HTTPException(status_code=400, detail="El presupuesto solo aplica a categorias de gasto")
    return crud.create_budget(db, budget)


@app.get("/budgets", response_model=list[schemas.BudgetOut])
def list_budgets(year: int, month: int, db: Session = Depends(get_db)):
    return crud.list_budgets(db, year, month)


@app.post("/savings-goals", response_model=schemas.SavingsGoalOut)
def create_savings_goal(goal: schemas.SavingsGoalCreate, db: Session = Depends(get_db)):
    return crud.create_savings_goal(db, goal)


@app.get("/savings-goals", response_model=list[schemas.SavingsGoalOut])
def list_savings_goals(db: Session = Depends(get_db)):
    return crud.list_savings_goals(db)


@app.get("/summary")
def get_summary(year: int, month: int, db: Session = Depends(get_db)):
    return crud.monthly_summary(db, year, month)


@app.post("/reports/monthly")
def generate_monthly_report(year: int, month: int, db: Session = Depends(get_db)):
    report_file = export_monthly_report(db, year, month)
    return {"message": "Reporte generado", "file": report_file}
