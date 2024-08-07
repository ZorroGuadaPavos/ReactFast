import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from src.auth.services import CurrentUser, SessionDep
from src.core.schemas import Message
from src.items.models import Item
from src.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate

from . import services

router = APIRouter()


@router.put('/{id}', response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail='Not enough permissions')
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete('/{id}')
def delete_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Message:
    """
    Delete an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail='Not enough permissions')
    session.delete(item)
    session.commit()
    return Message(message='Item deleted successfully')


@router.post('/', response_model=ItemPublic)
def create_item(*, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate) -> Any:
    """
    Create new item.
    """
    return services.create_item(session=session, item_in=item_in, owner_id=current_user.id)


@router.get('/{id}', response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail='Not enough permissions')
    return item


@router.get('/', response_model=ItemsPublic)
def read_items(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
        count = session.exec(count_statement).one()
        statement = select(Item).where(Item.owner_id == current_user.id).offset(skip).limit(limit)
        items = session.exec(statement).all()

    return ItemsPublic(data=items, count=count)