"""Magic items API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.magic_item import MagicItem

router = APIRouter(tags=["magic_items"])


class MagicItemResponse(BaseModel):
    id: str
    slug: str
    name: str
    rarity: str
    type: str
    requires_attunement: bool
    description: str
    category: str
    floor_min: int
    gold_value: int


@router.get("/magic-items", response_model=list[MagicItemResponse])
async def list_magic_items(
    rarity: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all magic items with optional filters."""
    query = select(MagicItem)

    if rarity:
        query = query.where(MagicItem.rarity == rarity)
    if type:
        query = query.where(MagicItem.type == type)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return [
        MagicItemResponse(
            id=item.id,
            slug=item.slug,
            name=item.name,
            rarity=item.rarity,
            type=item.type,
            requires_attunement=item.requires_attunement,
            description=item.description,
            category=item.category,
            floor_min=item.floor_min,
            gold_value=item.gold_value,
        )
        for item in items
    ]


@router.get("/magic-items/{item_id}", response_model=MagicItemResponse)
async def get_magic_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single magic item by ID."""
    result = await db.execute(select(MagicItem).where(MagicItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Magic item not found")

    return MagicItemResponse(
        id=item.id,
        slug=item.slug,
        name=item.name,
        rarity=item.rarity,
        type=item.type,
        requires_attunement=item.requires_attunement,
        description=item.description,
        category=item.category,
        floor_min=item.floor_min,
        gold_value=item.gold_value,
    )
