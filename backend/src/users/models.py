import typing
import uuid

from sqlmodel import Field, Relationship

from src.users.schemas import UserBase

if typing.TYPE_CHECKING:
    from src.items.models import Item


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    items: list['Item'] = Relationship(back_populates='owner')
