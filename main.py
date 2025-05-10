from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

from routers.login import router as login_router
from routers.admin.registrar_usuario import router as registrar_router
from routers.admin.productos.agregar_producto import router as agregar_producto_router
from routers.admin.productos.editar_producto import router as editar_producto_router
from routers.mostrar_productos import router as mostrar_productos_router
from routers.admin.productos.eliminar_producto import router as eliminar_producto_router
from routers.registrar_venta import router as registrar_venta_router
from routers.sumar_productos import router as sumar_productos_router
from routers.chat import router as chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(registrar_router, prefix="/admin")
app.include_router(agregar_producto_router, prefix="/admin/productos")
app.include_router(editar_producto_router, prefix="/admin/productos")
app.include_router(mostrar_productos_router, prefix="/productos")
app.include_router(eliminar_producto_router, prefix="/admin/productos")
app.include_router(registrar_venta_router, prefix="/ventas")
app.include_router(sumar_productos_router, prefix="/ventas")
app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT")))