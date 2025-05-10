from fastapi import APIRouter, HTTPException
from models.user import Login
from db.connection import get_db_connection
from core.security import create_access_token
import bcrypt

router = APIRouter()

@router.post("/login")
async def login_user(login: Login):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT username, password, rol FROM users WHERE username = %s", (login.username,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Credenciales Invalidas")
        
        username, password, rol = user

        if not bcrypt.checkpw(login.password.encode('utf-8'), password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Credenciales Invalidas")

        token = create_access_token(username=username, role=rol, expires_in=60)
        return {"Mensaje": "Bienvenido Al Sistema", "token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cursor.close()
        connection.close()