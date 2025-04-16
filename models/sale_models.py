from pydantic import BaseModel
from typing import List

class ProductInput(BaseModel):
    product_name: str
    quantity: int

class SaleInput(BaseModel):
    customer_name: str
    payment_method: str
    products: List[ProductInput]
