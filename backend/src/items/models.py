import uuid

from sqlmodel import Field, Relationship

from src.items.schemas import ItemBase
from src.users.models import User


class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(foreign_key='user.id', nullable=False)
    owner: User | None = Relationship(back_populates='items')
