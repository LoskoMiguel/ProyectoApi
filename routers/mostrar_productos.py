from fastapi import APIRouter, HTTPException, Depends, Request
from db.connection import get_db_connection

router = APIRouter()

@router.get("/mostrar_productos")
async def mostrar_productos():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT name_product FROM products")
        resultados = cursor.fetchall()
        
        nombres = [fila[0] for fila in resultados]
        return {"nombres": nombres}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nombres: {e}")
    finally:
        cursor.close()
        connection.close()