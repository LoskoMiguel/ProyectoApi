from pydantic import BaseModel
from typing import Optional

class agregar_producto(BaseModel):
    name_product : str
    price : float
    stock : int
    description : str

class editar_producto(BaseModel):
    name_product_edit: str
    new_name_product: Optional[str] = None
    new_price_product: Optional[float] = None
    new_stock_product: Optional[int] = None
    new_description_product: Optional[str] = None

class eliminar_producto(BaseModel):
    name_product: str