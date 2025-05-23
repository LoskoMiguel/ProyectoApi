# Sistema de Gestión Comercial - API

## Descripción
Sistema completo de gestión comercial desarrollado con FastAPI. Esta API proporciona servicios para la gestión de productos, ventas, usuarios y comunicación mediante chat con inteligencia artificial.

## Características
- 🔐 **Autenticación**: Sistema de inicio de sesión seguro
- 👥 **Gestión de usuarios**: Registro y administración de usuarios
- 📦 **Control de inventario**: Administración completa de productos
  - Agregar nuevos productos
  - Editar productos existentes
  - Eliminar productos
  - Consultar inventario
- 💰 **Gestión de ventas**: Registro y seguimiento de ventas
- 💬 **Sistema de chat de inteligencia artificial**: Asistente especializado con modelo GPT-4o que consulta directamente la base de datos para proporcionar información detallada sobre productos y ventas. Presenta resultados formateados con HTML y ofrece consultas avanzadas como totales de venta por cliente y fecha.

## Tecnologías utilizadas
- **FastAPI**: Framework web de alto rendimiento para APIs
- **PostgreSQL**: Base de datos relacional
- **Python 3**: Lenguaje de programación principal
- **Pydantic**: Validación de datos y settings
- **SQLAlchemy**: ORM para manejo de base de datos
- **OpenAI**: Integración de modelo GPT-4o para asistencia mediante chat inteligente
- **LangChain**: Framework para desarrollo de aplicaciones con IA, utilizado para la creación del agente SQL

## Estructura del proyecto
```
proyecto_cedenorte/
├── main.py                 # Punto de entrada de la aplicación
├── config.py               # Configuraciones generales
├── requirements.txt        # Dependencias del proyecto
├── models/                 # Modelos de datos
│   ├── productos.py
│   ├── user.py
│   ├── sale_models.py
│   └── chat_models.py
├── routers/                # Rutas de la API
│   ├── admin/              # Endpoints para administradores
│   │   ├── productos/      # Gestión de productos
│   │   └── registrar_usuario.py
│   ├── login.py
│   ├── mostrar_productos.py
│   ├── registrar_venta.py
│   ├── sumar_productos.py
│   └── chat.py
└── db/                     # Configuración de base de datos
    └── connection.py
```

## Instalación y configuración

### Requisitos previos
- Python 3.8 o superior
- PostgreSQL

### Pasos de instalación
1. Clonar el repositorio:
```bash
git clone https://github.com/LoskoMiguel/ProyectoApi.git
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Unix/MacOS:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con:
La Base De Datos Es SupaBase
```
HOST=<host-de-base-de-datos>
DBPORT=<puerto-de-base-de-datos>
DBNAME=<nombre-de-base-de-datos>
USER=<usuario-de-base-de-datos>
PASSWORD=<contraseña-de-base-de-datos>
PORT=<puerto-para-la-api>
OPENAI_API_KEY=<tu-clave-api-de-openai>
```

5. Iniciar el servidor:
```bash
python main.py
```

## Uso de la API

### Endpoints principales
- `/login` - Autenticación de usuarios
- `/admin/registrar_usuario` - Registro de usuarios
- `/admin/productos/agregar_producto` - Agregar productos
- `/admin/productos/editar_producto` - Editar productos
- `/admin/productos/eliminar_producto` - Eliminar productos
- `/productos/mostrar_productos` - Visualizar productos
- `/ventas/registrar_venta` - Registrar ventas
- `/ventas/sumar_productos` - Calcular suma de productos
- `/chat` - Sistema de comunicación con asistente IA especializado en consultas sobre productos y ventas

## Contribución
Para contribuir al proyecto:
1. Hacer fork del repositorio
2. Crear una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Hacer commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Hacer push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abrir un Pull Request