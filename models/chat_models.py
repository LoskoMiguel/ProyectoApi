from pydantic import BaseModel

class chat(BaseModel):
    user_message: str