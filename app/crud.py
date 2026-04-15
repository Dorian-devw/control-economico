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
    create_audit_log(
        db,
        action="create",
        entity="movement",
        entity_id=model.id,
        detail=json.dumps(movement.model_dump(), ensure_ascii=True, default=str),
    )
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
    create_audit_log(
        db,
        action="create",
        entity="budget",
        entity_id=model.id,
        detail=f"Presupuesto {budget.year}-{budget.month:02} categoria={budget.category_id}",
    )
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
    create_audit_log(
        db,
        action="create",
        entity="savings_goal",
        entity_id=model.id,
        detail=f"Meta creada: {model.name}",
    )
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


def find_duplicate_movement(db: Session, movement: schemas.MovementCreate):
    normalized_note = (movement.note or "").strip()
    return (
        db.query(models.Movement)
        .filter(
            models.Movement.movement_date == movement.movement_date,
            models.Movement.amount == movement.amount,
            models.Movement.movement_type == movement.movement_type,
            models.Movement.payment_method == movement.payment_method,
            models.Movement.category_id == movement.category_id,
            func.coalesce(models.Movement.note, "") == normalized_note,
        )
        .first()
    )


def get_budget_alerts(db: Session, year: int, month: int):
    rows = (
        db.query(
            models.Budget.category_id,
            models.Category.name.label("category_name"),
            models.Budget.limit_amount,
            func.coalesce(func.sum(models.Movement.amount), 0.0).label("spent_amount"),
        )
        .join(models.Category, models.Category.id == models.Budget.category_id)
        .outerjoin(
            models.Movement,
            (models.Movement.category_id == models.Budget.category_id)
            & (models.Movement.movement_type == "expense")
            & (extract("year", models.Movement.movement_date) == year)
            & (extract("month", models.Movement.movement_date) == month),
        )
        .filter(models.Budget.year == year, models.Budget.month == month)
        .group_by(models.Budget.category_id, models.Category.name, models.Budget.limit_amount)
        .all()
    )

    alerts = []
    for row in rows:
        usage = (float(row.spent_amount) / float(row.limit_amount)) * 100 if row.limit_amount else 0
        level = "ok"
        if usage >= 100:
            level = "critical"
        elif usage >= 80:
            level = "warning"

        alerts.append(
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "limit_amount": float(row.limit_amount),
                "spent_amount": float(row.spent_amount),
                "usage_pct": round(usage, 2),
                "level": level,
            }
        )
    return alerts


def create_audit_log(
    db: Session,
    action: str,
    entity: str,
    entity_id: int | None = None,
    detail: str | None = None,
):
    model = models.AuditLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        detail=detail,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def list_audit_logs(db: Session, limit: int = 50):
    return (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
