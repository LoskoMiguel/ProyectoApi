from fastapi import APIRouter, HTTPException, Depends, Request
from models.productos import editar_producto
from db.connection import get_db_connection
from core.security import verify_token_and_role

router = APIRouter()

@router.put("/editar_producto")
async def editar_producto(
    editar_producto: editar_producto,
    request: Request,
    token_data=Depends(verify_token_and_role)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if not editar_producto.name_product_edit:
            raise HTTPException(status_code=400, detail="El nombre del producto a editar no puede estar vacío")

        cursor.execute("SELECT * FROM products WHERE name_product = %s", (editar_producto.name_product_edit,))
        product = cursor.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="El producto no existe")

        fields = []
        values = []

        if editar_producto.new_name_product is not None:
            fields.append("name_product = %s")
            values.append(editar_producto.new_name_product)

        if editar_producto.new_price_product is not None:
            fields.append("price = %s")
            values.append(editar_producto.new_price_product)

        if editar_producto.new_stock_product is not None:
            fields.append("stock = %s")
            values.append(editar_producto.new_stock_product)

        if editar_producto.new_description_product is not None:
            fields.append("description = %s")
            values.append(editar_producto.new_description_product)

        if not fields:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")

        query = f"UPDATE products SET {', '.join(fields)} WHERE name_product = %s"
        values.append(editar_producto.name_product_edit)

        cursor.execute(query, tuple(values))
        connection.commit()

        return {"mensaje": "Producto editado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cursor.close()
        connection.close()