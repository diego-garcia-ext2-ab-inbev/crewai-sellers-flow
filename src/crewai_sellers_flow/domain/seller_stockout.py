from pydantic import BaseModel


class SellerStockOut(BaseModel):
    id: int
    name: str
    stockout: int
    top_product: str


