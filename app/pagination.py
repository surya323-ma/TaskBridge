import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def paginate(db: Session, stmt, page: int, size: int) -> dict:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    items = db.scalars(stmt.limit(size).offset((page - 1) * size)).all()
    return {"items": items, "total": total, "page": page, "size": size, "pages": max(1, math.ceil(total / size))}
