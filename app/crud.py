from datetime import date
import json

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app import models, schemas


def create_category(db: Session, category: schemas.CategoryCreate):
    model = models.Category(**category.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    create_audit_log(
        db,
        action="create",
        entity="category",
        entity_id=model.id,
        detail=f"Categoria creada: {model.name}",
    )
    return model


def list_categories(db: Session):
    return db.query(models.Category).order_by(models.Category.name.asc()).all()


def create_movement(db: Session, movement: schemas.MovementCreate):
    model = models.Movement(**movement.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def list_movements(db: Session, year: int | None = None, month: int | None = None):
    query = db.query(models.Movement).order_by(models.Movement.movement_date.desc())
    if year:
        query = query.filter(extract("year", models.Movement.movement_date) == year)
    if month:
        query = query.filter(extract("month", models.Movement.movement_date) == month)
    return query.all()


def create_budget(db: Session, budget: schemas.BudgetCreate):
    model = models.Budget(**budget.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def list_budgets(db: Session, year: int, month: int):
    return (
        db.query(models.Budget)
        .filter(models.Budget.year == year, models.Budget.month == month)
        .all()
    )


def create_savings_goal(db: Session, goal: schemas.SavingsGoalCreate):
    model = models.SavingsGoal(**goal.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def list_savings_goals(db: Session):
    return db.query(models.SavingsGoal).order_by(models.SavingsGoal.name.asc()).all()


def monthly_summary(db: Session, year: int, month: int):
    income = (
        db.query(func.coalesce(func.sum(models.Movement.amount), 0.0))
        .filter(
            extract("year", models.Movement.movement_date) == year,
            extract("month", models.Movement.movement_date) == month,
            models.Movement.movement_type == "income",
        )
        .scalar()
    )

    expense = (
        db.query(func.coalesce(func.sum(models.Movement.amount), 0.0))
        .filter(
            extract("year", models.Movement.movement_date) == year,
            extract("month", models.Movement.movement_date) == month,
            models.Movement.movement_type == "expense",
        )
        .scalar()
    )

    return {
        "year": year,
        "month": month,
        "income": float(income),
        "expense": float(expense),
        "balance": float(income - expense),
        "generated_at": date.today().isoformat(),
    }
