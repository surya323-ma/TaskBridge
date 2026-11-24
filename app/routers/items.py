from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import Item
from ..pagination import paginate
from ..schemas import ItemCreate, ItemOut, ItemSummary, ItemUpdate, Page

router = APIRouter(prefix="/api/items", tags=["inventory"], dependencies=[Depends(get_current_user)])


def _get_item(db: Session, item_id: int) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return item


@router.get("", response_model=Page[ItemOut])
def list_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: str | None = Query(None, max_length=60),
    low_stock: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(Item).order_by(Item.name)
    if q:
        stmt = stmt.where(or_(Item.name.ilike(f"%{q}%"), Item.sku.ilike(f"%{q}%")))
    if low_stock:
        stmt = stmt.where(Item.quantity <= Item.reorder_level)
    return paginate(db, stmt, page, size)


@router.get("/summary", response_model=ItemSummary)
def summary(db: Session = Depends(get_db)):
    skus, units, value = db.execute(
        select(func.count(Item.id), func.coalesce(func.sum(Item.quantity), 0), func.coalesce(func.sum(Item.quantity * Item.price), 0.0))
    ).one()
    low = db.scalar(select(func.count(Item.id)).where(Item.quantity <= Item.reorder_level)) or 0
    return ItemSummary(skus=skus, units=int(units), stock_value=round(float(value), 2), low_stock=low)


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["sku"] = data["sku"].upper()
    item = Item(**data)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "That SKU already exists")
    return item


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return _get_item(db, item_id)


@router.put("/{item_id}", response_model=ItemOut, dependencies=[Depends(require_admin)])
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = _get_item(db, item_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db.delete(_get_item(db, item_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
