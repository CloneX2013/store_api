from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from store.core.exceptions import InsertionError, NotFoundError
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import (
    ProductIn,
    ProductOut,
    ProductUpdate,
)

class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        """Cria um novo produto na base de dados."""
        product_model = ProductModel(**body.model_dump())

        
        try:
            await self.collection.insert_one(product_model.model_dump())
        except PyMongoError as exc:
            
            raise InsertionError(message=exc._message) from exc

        return ProductOut(**product_model.model_dump())

    async def get(self, id: UUID) -> ProductOut:
        """Busca um produto pelo seu ID."""
        result = await self.collection.find_one({"id": id})

        if not result:
            
            raise NotFoundError(message=f"Product not found with filter: {id}")

        return ProductOut(**result)

    
    async def query(
        self, price_min: Optional[float] = None, price_max: Optional[float] = None
    ) -> List[ProductOut]:
        """Busca produtos com filtros de preço opcionais."""
        filter_query = {}
        price_filter = {}

        
        if price_min is not None:
            price_filter["$gt"] = price_min  

        if price_max is not None:
            price_filter["$lt"] = price_max  

        if price_filter:
            filter_query["price"] = price_filter

        return [ProductOut(**item) async for item in self.collection.find(filter_query)]

    
    async def update(self, id: UUID, body: ProductUpdate) -> ProductOut:
        """Atualiza um produto e a sua data de atualização."""
        
        update_data = body.model_dump(exclude_none=True)

        
        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": update_data},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        
        if not result:
            raise NotFoundError(message=f"Product not found with filter: {id}")

        return ProductOut(**result)

    async def delete(self, id: UUID) -> bool:
        """Deleta um produto da base de dados."""
        product = await self.collection.find_one({"id": id})
        if not product:
            
            raise NotFoundError(message=f"Product not found with filter: {id}")

        result = await self.collection.delete_one({"id": id})

        return True if result.deleted_count > 0 else False


product_usecase = ProductUsecase()
