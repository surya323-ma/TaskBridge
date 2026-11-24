from datetime import date, datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

Status = Literal["todo", "in_progress", "done"]
Priority = Literal["low", "medium", "high"]


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    status: Status = "todo"
    priority: Priority = "medium"
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    status: Status | None = None
    priority: Priority | None = None
    due_date: date | None = None


class TaskOut(TaskCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: datetime


class ItemCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=32, pattern=r"^[A-Za-z0-9-]+$")
    name: str = Field(min_length=1, max_length=120)
    quantity: int = Field(default=0, ge=0, le=1_000_000)
    price: float = Field(default=0, ge=0, le=10_000_000)
    reorder_level: int = Field(default=5, ge=0, le=1_000_000)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    quantity: int | None = Field(default=None, ge=0, le=1_000_000)
    price: float | None = Field(default=None, ge=0, le=10_000_000)
    reorder_level: int | None = Field(default=None, ge=0, le=1_000_000)


class ItemOut(ItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    updated_at: datetime


class ItemSummary(BaseModel):
    skus: int
    units: int
    stock_value: float
    low_stock: int


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
