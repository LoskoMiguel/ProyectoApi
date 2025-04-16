from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str

class Registrar(BaseModel):
    name : str
    username : str
    password : str
    rol : str