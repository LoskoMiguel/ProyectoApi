from fastapi import APIRouter, HTTPException, Depends, Request
from models.productos import eliminar_producto
from db.connection import get_db_connection
from core.security import verify_token_and_role

router = APIRouter()

@router.delete("/eliminar_producto")
async def eliminar_producto(
    eliminar_producto: eliminar_producto,
    request: Request,
    token_data=Depends(verify_token_and_role)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        
        if eliminar_producto.name_product == "":
            raise HTTPException(status_code=400, detail="El nombre del producto no puede estar vacío")
        
        cursor.execute("SELECT * FROM products WHERE name_product = %s", (eliminar_producto.name_product,))
        product = cursor.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="El producto no existe")

        cursor.execute("DELETE FROM products WHERE name_product = %s", (eliminar_producto.name_product,))
        connection.commit()

        return {"Mensaje": "Producto Eliminado Correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cursor.close()
        connection.close()