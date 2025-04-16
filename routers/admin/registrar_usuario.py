from fastapi import APIRouter, HTTPException, Depends, Request
from models.user import Registrar
from db.connection import get_db_connection
from core.security import verify_token_and_role

router = APIRouter()

@router.post("/registrar")
async def registrar_usuario(
    registrar: Registrar,
    request: Request,
    token_data=Depends(verify_token_and_role)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if registrar.rol not in ["admin", "user"]:
            raise HTTPException(status_code=400, detail="Rol no permitido")
        
        if len(registrar.password) < 8:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
        
        if registrar.name == "" or registrar.username == "" or registrar.password == "" or registrar.rol == "":
            raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")
        
        cursor.execute("SELECT username FROM users WHERE username = %s", (registrar.username,))
        user = cursor.fetchone()

        if user:
            raise HTTPException(status_code=401, detail="El usuario ya existe")

        cursor.execute("INSERT INTO users (name, username, password, rol) VALUES (%s, %s, %s, %s)", 
                       (registrar.name, registrar.username, registrar.password, registrar.rol))
        connection.commit()

        return {"Mensaje": "Usuario Creado Correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
