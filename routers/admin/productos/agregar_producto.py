from fastapi import APIRouter, HTTPException, Depends, Request
from models.productos import agregar_producto
from db.connection import get_db_connection
from core.security import verify_token_and_role

router = APIRouter()

@router.post("/agregar_producto")
async def agregar_producto(
    agregar_producto: agregar_producto,
    request: Request,
    token_data=Depends(verify_token_and_role)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        
        if agregar_producto.name_product == "" or agregar_producto.price == "" or agregar_producto.stock == "" or agregar_producto.description == "":
            raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")
        
        cursor.execute("SELECT * FROM products WHERE name_product = %s", (agregar_producto.name_product,))
        product = cursor.fetchone()

        if product:
            raise HTTPException(status_code=401, detail="El producto ya existe")

        cursor.execute("INSERT INTO products (name_product, price, stock, description) VALUES (%s, %s, %s, %s)", 
                       (agregar_producto.name_product, agregar_producto.price, agregar_producto.stock, agregar_producto.description))
        connection.commit()

        return {"Mensaje": "Producto Creado Correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
