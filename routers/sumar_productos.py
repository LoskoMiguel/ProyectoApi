from fastapi import APIRouter, HTTPException
from models.sale_models import SalePlusProducts
from db.connection import get_db_connection

router = APIRouter()

@router.post("/sumar_productos")
async def plus_products(SalePlusProducts: SalePlusProducts):
    connection = get_db_connection()
    cursor = connection.cursor()

    total_price = 0

    try:
        for producto in SalePlusProducts.products:
            cursor.execute("SELECT price FROM products WHERE name_product = %s", (producto.product_name,))
            product_data = cursor.fetchone()

            if not product_data:
                raise HTTPException(status_code=404, detail=f"El Producto {producto.product_name} No Fue Encontrado")
            
            unit_price = int(product_data[0])
            subtotal = unit_price * producto.quantity
            total_price += subtotal

        return {"message": f"El Precio Total Hasta El Momento Es: {total_price}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()