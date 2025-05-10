from fastapi import APIRouter, HTTPException, Depends, Request
from db.connection import get_db_connection

router = APIRouter()

@router.get("/mostrar_productos")
async def mostrar_productos():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT name_product, price, stock, description FROM products")
        resultados = cursor.fetchall()
        
        nombres = [fila[0] for fila in resultados]
        precios = [fila[1] for fila in resultados]
        descripciones = [fila[3] for fila in resultados]
        total = [fila[2] for fila in resultados]
        return {"nombres": nombres, "precios": precios, "descripciones": descripciones, "total": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {e}")
    finally:
        cursor.close()
        connection.close()