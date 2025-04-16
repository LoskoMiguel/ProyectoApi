from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.agents import AgentType, AgentExecutor
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.memory import ConversationBufferMemory
from langchain.schema.output_parser import OutputParserException
import os
import re
from fastapi import APIRouter, HTTPException, Depends, Request
from models.chat_models import chat
from db.connection import get_db_connection
from core.security import verify_token_and_role

router = APIRouter()

llm = ChatOpenAI(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o-mini", 
    temperature=0, 
    streaming=True
)

# Crear memoria de conversación
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def clean_response(response):
    match = re.search(r"Here are the details:(.*)", response, re.DOTALL)
    if match:
        response = match.group(1)
    
    match = re.search(r"I have successfully retrieved(.*)", response, re.DOTALL)
    if match:
        response = match.group(1)

    response = re.sub(r"In summary:.*", "", response, flags=re.DOTALL)
    response = re.sub(r"\*\*", "", response) 
    response = response.strip()

    return response

def get_db():
    conn = get_db_connection()
    connection_string = f"postgresql://{conn.info.user}:{conn.info.password}@{conn.info.host}:{conn.info.port}/{conn.info.dbname}"
    return connection_string

def generate_response(user_message):
    db = SQLDatabase.from_uri(get_db())

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    enhanced_message = f"""
    {user_message}

    Eres un asistente de ventas que ayuda a los usuarios a realizar consultas sobre productos y ventas.
    Tu tarea es responder a las preguntas de los usuarios sobre productos y ventas en una tienda.
    Puedes realizar consultas a la base de datos para obtener información sobre productos, precios y detalles de ventas.
    Asegúrate de proporcionar respuestas claras y concisas.
    Porfavor Todas las respuestas deben ser en español.
    No olvides incluir detalles relevantes y ser amigable en tu tono.
    las respuestas porfavor proporcionalas ordenadas usando etiquetas de html como h1 h2 h3 p ul li br pero nunca uses etiquetas que alteren la pagina como script o style.
    No olvides que eres un asistente de ventas y no un asistente de programación.
    Además, asegúrate de que todas las respuestas sean informativas y útiles para el usuario.
    Todas las respuestas deben ser basasdas en la base de datos y no en suposiciones.
    Debes de tener en cuenta que siempre los nombres de los productos y los clientes y de todo esta en minusuculas.

    TIP DE RESPUESTA:
    Antes de dar la respuesta te recomiendo que hagas un select de cada una de las 3 tablas menos la de users por que esa es privada
    entonces hacer un select de cada una de las tablas y luego hacer un join entre ellas para obtener la respuesta
    por que digamos si el usuario te pide el nombre de un cliente digamos JUAN y en la base de datos esta Juan o jUan entonces lo que debes de hacer en ese caso es por logica sabes que es ese juan a el que serefiere
    por eso es bueno primero imprimir toda la informacion de las tablas para comparar

    Cuando necesites hacer saltos usa <br> por que recuerda que las respuestas debes de generarlas con etiquetas html
    """

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        memory=memory 
    )

    try:
        result = agent_executor.run(enhanced_message)
        result = clean_response(result)
        return result
    except OutputParserException as e:
        return "Lo siento, hubo un problema al entender la respuesta del agente. Intenta reformular la pregunta."
    except Exception as e:
        return f"Ocurrió un error: {e}"
    
@router.post("/chat")
async def chat(
    chat: chat,
    request: Request,
    token_data=Depends(verify_token_and_role)
):
    user_message = chat.user_message

    if not user_message:
        raise HTTPException(status_code=400, detail="El mensaje del usuario no puede estar vacío.")

    response = generate_response(user_message)
    return {"response": response}