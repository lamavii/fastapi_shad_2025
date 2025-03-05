from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_204_NO_CONTENT

from src.configurations.database import get_async_session
from src.routers.v1.token import get_current_user
from src.schemas.sellers import ReturnedSeller, IncomingSeller, ReturnedAllSellers, ReturnedSellersDetails, SellerUpdate
from src.services.sellers import SellerService

seller_router = APIRouter(tags=["seller"], prefix="/seller")

DBSession = Depends(get_async_session)


@seller_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(
        seller: IncomingSeller, session: AsyncSession = DBSession
):
    seller_service = SellerService(session)
    new_seller = await seller_service.create_seller(seller)
    if new_seller is None:
        raise HTTPException(status_code=400, detail="Seller with this email already exists")
    return new_seller


@seller_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: AsyncSession = DBSession):
    seller_service = SellerService(session)
    sellers = await seller_service.get_all_sellers()
    return {"sellers": sellers}


@seller_router.get("/{seller_id}", response_model=ReturnedSellersDetails, dependencies=[Depends(get_current_user)])
async def get_seller(seller_id: int, session: AsyncSession = DBSession):
    seller_service = SellerService(session)
    seller = await seller_service.get_seller_by_id(seller_id)
    if seller is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller


@seller_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_update: SellerUpdate, session: AsyncSession = DBSession):
    seller_service = SellerService(session)
    updated_seller = await seller_service.update_seller(seller_id, seller_update.model_dump(exclude_unset=True))
    if updated_seller is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return updated_seller


@seller_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: AsyncSession = Depends(get_async_session)):
    seller_service = SellerService(session)
    await seller_service.delete_seller(seller_id)
    return Response(status_code=HTTP_204_NO_CONTENT)
