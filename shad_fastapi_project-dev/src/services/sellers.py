from typing import Type, Optional

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_seller(self, seller_data: IncomingSeller) -> Optional[Seller]:
        existing_seller = await self.db_session.execute(
            select(Seller).where(Seller.email == seller_data.email)
        )
        if existing_seller.scalars().first() is not None:
            return None

        hashed_password = self.hash_password(seller_data.password)
        new_seller = Seller(
            first_name=seller_data.first_name,
            last_name=seller_data.last_name,
            email=seller_data.email,
            password=hashed_password
        )
        self.db_session.add(new_seller)
        await self.db_session.flush()
        await self.db_session.refresh(new_seller)
        return new_seller

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def authenticate_user(self, email: str, password: str) -> Optional[Seller]:
        result = await self.db_session.execute(select(Seller).where(Seller.email == email))
        seller = result.scalar_one_or_none()
        if seller is not None:
            if pwd_context.verify(password, seller.password):
                return seller
        return None

    async def get_seller_by_email(self, email: str) -> Optional[Seller]:
        result = await self.db_session.execute(select(Seller).where(Seller.email == email))
        seller = result.scalar_one_or_none()
        if seller:
            return seller
        return None

    async def get_all_sellers(self):
        result = await self.db_session.execute(select(Seller))
        sellers = result.scalars().all()
        return sellers

    async def get_seller_by_id(self, seller_id: int) -> Seller:
        result = await self.db_session.execute(
            select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
        )
        return result.scalar_one_or_none()

    async def update_seller(self, seller_id: int, seller_update: dict) -> Optional[Type[Seller]]:
        result = await self.db_session.get(Seller, seller_id)
        if result is None:
            return None
        for key, value in seller_update.items():
            setattr(result, key, value)
        await self.db_session.flush()
        await self.db_session.refresh(result)
        return result

    async def delete_seller(self, seller_id: int):
        result = await self.db_session.get(Seller, seller_id)
        if result:
            await self.db_session.delete(result)
            await self.db_session.flush()
