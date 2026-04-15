from datetime import date, datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    movement_type: str = Field(pattern="^(income|expense)$")


class CategoryOut(CategoryCreate):
    id: int

    class Config:
        from_attributes = True


class MovementCreate(BaseModel):
    movement_date: date
    amount: float = Field(gt=0)
    movement_type: str = Field(pattern="^(income|expense)$")
    payment_method: str = Field(min_length=2, max_length=30)
    note: str | None = Field(default=None, max_length=255)
    category_id: int


class MovementOut(MovementCreate):
    id: int

    class Config:
        from_attributes = True


class BudgetCreate(BaseModel):
    year: int
    month: int = Field(ge=1, le=12)
    category_id: int
    limit_amount: float = Field(gt=0)


class BudgetOut(BudgetCreate):
    id: int

    class Config:
        from_attributes = True


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    due_date: date | None = None


class SavingsGoalOut(SavingsGoalCreate):
    id: int

    class Config:
        from_attributes = True


class BudgetAlert(BaseModel):
    category_id: int
    category_name: str
    limit_amount: float
    spent_amount: float
    usage_pct: float
    level: str


class AuditLogOut(BaseModel):
    id: int
    action: str
    entity: str
    entity_id: int | None = None
    detail: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
