from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import os

os.sys.path.append(
    r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# 应用于->普通用户与管理员的兼容接口
@router.get("/", response_model=List[schemas.Item])
def read_items(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 10000,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve items.
    """
    if crud.user.is_superuser(current_user):
        items = crud.item.get_multi_items(db, skip=skip, limit=limit)
    else:
        items = crud.item.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return items


# 根据用于id来创建一个item
@router.post("/", response_model=schemas.Item)
def create_item(
        *,
        db: Session = Depends(deps.get_db),
        item_in: schemas.ItemCreate,
        current_user: models.User = Depends(deps.get_current_active_user),
        item_id: int = Body(None)
) -> Any:
    """
    Create new item.
    """

    if crud.user.is_superuser(current_user):

        owner_id = item_id
    else:
        owner_id = current_user.id

    item = crud.item.create_with_owner(db=db, obj_in=item_in, owner_id=owner_id)
    return item


# 根据item的id更新用户信息
@router.put("/{id}", response_model=schemas.Item)
def update_item(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        item_in: schemas.ItemUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get("/{id}", response_model=schemas.Item)
def read_item(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.delete("/{id}", response_model=schemas.Item)
def delete_item(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = crud.item.remove(db=db, id=id)
    return item
