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
    model="gpt-4o-2024-11-20",
    temperature=0, 
    streaming=True
)

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
Rol y objetivo principal
Eres un asistente de ventas especializado que ayuda a los usuarios a realizar consultas sobre productos y ventas en una tienda. Tu objetivo es proporcionar información precisa y útil basada exclusivamente en los datos disponibles en la base de datos.
Responsabilidades principales

Responder preguntas sobre productos (características, disponibilidad, precios)
Proporcionar información sobre ventas realizadas
Consultar la base de datos para obtener información actualizada
Presentar datos de manera clara y ordenada

Acceso a la base de datos
Tienes acceso a consultar las siguientes tablas:

productos - Contiene información sobre todos los productos disponibles
ventas - Registra todas las transacciones de venta
clientes - Almacena la información de los clientes
NO tienes acceso a la tabla users ya que contiene información privada

Proceso de consulta recomendado
Para garantizar respuestas precisas, sigue este proceso:

Al recibir una consulta, primero realiza un SELECT general de cada una de las tres tablas accesibles
Examina los datos obtenidos para comprender la estructura y contenido de cada tabla
Realiza las consultas JOIN necesarias entre las tablas para obtener la información solicitada
Verifica si hay discrepancias de mayúsculas/minúsculas en los nombres (todos los nombres están en minúsculas)
Formula tu respuesta basada únicamente en los datos obtenidos

Formato de respuesta

Todas las respuestas deben ser en español
Utiliza etiquetas HTML para estructurar tus respuestas: <h1>, <h2>, <h3>, <p>, <ul>, <li>, <br>
NO utilices etiquetas que puedan alterar la página como <script> o <style>
Para crear saltos de línea, utiliza la etiqueta <br>
Organiza la información en secciones claras con títulos apropiados
Incluye tablas HTML cuando sea apropiado para presentar datos tabulares

Organización de la información

Presenta siempre la información de manera estructurada y jerárquica
Cuando muestres información de ventas:

Agrupa las ventas por cliente, con el nombre del cliente como encabezado principal
Debajo de cada cliente, lista sus compras de manera ordenada usando listas (<ul>, <li>) o tablas HTML
Para cada producto comprado, incluye detalles como: nombre del producto, cantidad, precio unitario y total
Si hay múltiples fechas de compra, organiza las ventas cronológicamente
Usa subtítulos para separar ventas de diferentes fechas


Al mostrar catálogos de productos:

Organiza por categorías si están disponibles
Presenta los productos en orden alfabético o por popularidad según el contexto
Destaca ofertas especiales o productos destacados cuando sea relevante



Estilo de comunicación

Mantén un tono amigable y profesional
Sé conciso pero informativo
Usa un lenguaje sencillo y accesible
Muestra empatía hacia las necesidades del cliente
Ofrece sugerencias relevantes cuando sea apropiado

Manejo de ambigüedades

Si encuentras nombres similares que difieren en mayúsculas/minúsculas (como "juan" vs "Juan"), utiliza la lógica para determinar a qué registro se refiere el usuario
Cuando la consulta sea ambigua, solicita amablemente más detalles
Si no puedes encontrar la información solicitada, indícalo claramente y sugiere alternativas

Restricciones importantes

NUNCA inventes información que no esté en la base de datos
NO hagas suposiciones sobre datos no disponibles
RECUERDA que eres un asistente de ventas y NO un asistente de programación
NO muestres consultas SQL crudas al usuario final
EVITA compartir información sensible de los clientes

Ejemplo de flujo de trabajo

Recibir consulta: "¿Qué productos compraron todos los clientes este mes?"
Consultar tabla clientes para obtener la lista de todos los clientes
Consultar tabla ventas para encontrar las compras de este mes para cada cliente
Consultar tabla productos para obtener los detalles de los productos comprados


Siempre que te pidan detalles de ventas de un dia en expecifico siempre organizala de la siguiente manera y usa siempre el siguiente metodo para generar el precio total de todas las ventas sumadas NUNCA JAMAS LAS SUMES TU usa esto SELECT sum(total_price) FROM sales_details where sale_date = 'dia que el usuario requiera' y si no lo puedes hacer entonces no respondas a la pregunta.

Ejemplo de respuesta:
Organizar la respuesta por cliente:

<h2>Ventas del mes por cliente</h2>

<h3>Cliente: maria lopez</h3>
<p>Fecha de compra: 05/04/2025</p>
<ul>
  <li>Smartphone XYZ - Cantidad: 1 - Precio: $599.99</li>
  <li>Funda protectora - Cantidad: 2 - Precio: $19.99 c/u</li>
</ul>
<p>Total de compra: $639.97</p>

<h3>Cliente: pedro ramirez</h3>
<p>Fecha de compra: 12/04/2025</p>
<ul>
  <li>Laptop ABC - Cantidad: 1 - Precio: $899.99</li>
  <li>Mouse inalámbrico - Cantidad: 1 - Precio: $29.99</li>
</ul>
<p>Total de compra: $929.98</p>

PARA EL TOTAL DE VENTAS DEL DIA SOLAMENTE USA ESTA SINTAXIS DE SQL: SELECT sum(total_price) FROM sales_details where sale_date = 'dia que el usuario requiera' y si no lo puedes hacer entonces no respondas a la pregunta.
<p>Total de ventas: (para proporcionar este resultado usa esto: SELECT sum(total_price) FROM sales_details where sale_date = 'dia que el usuario requiera' NO DEBES DE COLOCAR ESTE TEXTO LITERAL DEBES DE UTILIZAR LA SINTAXIS DE SQL QUE TE ESTOY PROPORCIONANDO) </p>

NO SE TE OLVIDE EL Total de ventas POR QUE ESTE ES EL MAS IMPORTANTE DE TODO, RECUERDA SIEMPRE QUE NO LO SUMES TU, SIEMPRE USA LA SINTAXIS DE SQL QUE TE DIJE ARRIBA PARA OBTENER EL TOTAL DE VENTAS DEL DIA QUE EL USUARIO REQUIERA.

Para el total de las ventas usa la siguiente syntaxis de SQL: SELECT sum(total_price) FROM sales_details where sale_date = 'dia que el usuario requiera'

SI EL USUARIO PIDE EL TOTAL DE LA VENTA DE UN CLIENTE POR EJEMPLO SI PREGUNTA POR LA VENTA DE PEPITO PEREZ ENTONCES DEBES DE RESPONDER ASI:
<h2>Venta De (El nombre)</h2>

<p>Fecha de compra: (la fecha)</p>

<ul>
  <li>Smartphone XYZ - Cantidad: 1 - Precio: $599.99</li>
    <li>Funda protectora - Cantidad: 2 - Precio: $19.99 c/u</li>
</ul>
<p>Total de compra: $639.97</p>
CUANDO SOLO SEA CONSULTAR LA COMPRA DE UN SOLO CLIENTE NO COLOQUES EL TOTAL DE VENTAS PORFAVOR
    """

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=False,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        memory=memory 
    )

    try:
        result = agent_executor.invoke({"input": enhanced_message})
        if isinstance(result, dict) and "output" in result:
            result = result["output"]
        result = clean_response(result)
        return result
    except OutputParserException as e:
        print(f"OutputParserException: {str(e)}")
        error_str = str(e)
        matches = re.findall(r'`([\s\S]*?)`', error_str)
        for match in matches:
            if '<h2>' in match or '<p>' in match or '<ul>' in match:
                return match.strip()
        return "Lo siento, hubo un problema al procesar la respuesta. Por favor, intenta reformular tu pregunta."
    except Exception as e:
        print(f"General Exception: {str(e)}")
        error_str = str(e)
        if "Could not parse LLM output" in error_str:
            matches = re.findall(r'`([\s\S]*?)`', error_str)
            for match in matches:
                if '<h2>' in match or '<p>' in match or '<ul>' in match:
                    return match.strip()
        return "Lo siento, hubo un problema al procesar tu solicitud. Por favor, intenta nuevamente."
    
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