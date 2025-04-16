from fastapi import APIRouter, HTTPException
from models.sale_models import SaleInput
from db.connection import get_db_connection

router = APIRouter()

@router.post("/registrar_venta")
async def register_sale(sale: SaleInput):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        total_items = 0
        total_price = 0
        products_data = []

        for product in sale.products:
            cursor.execute("SELECT price, stock FROM products WHERE name_product = %s", (product.product_name,))
            product_data = cursor.fetchone()

            if not product_data:
                raise HTTPException(status_code=404, detail=f"El Producto {product.product_name} No Fue Encontrado")

            unit_price = float(product_data[0])
            stock = product_data[1]

            if product.quantity > stock:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.product_name}. Disponible: {stock}")

            subtotal = unit_price * product.quantity
            total_items += product.quantity
            total_price += subtotal

            products_data.append({
                "product_name": product.product_name,
                "quantity": product.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal
            })

        cursor.execute("INSERT INTO sales_details (customer_name, total_items, total_price, payment_method) VALUES (%s, %s, %s, %s) RETURNING id", (sale.customer_name, total_items, total_price, sale.payment_method))

        sale_id = cursor.fetchone()[0]

        for product in products_data:
            cursor.execute("""
                INSERT INTO sales_products (sale_id, product_name, quantity, unit_price, subtotal) VALUES (%s, %s, %s, %s, %s) """, (sale_id, product["product_name"], product["quantity"], product["unit_price"], product["subtotal"]))

            cursor.execute('UPDATE products SET stock = stock - %s WHERE name_product = %s', (product["quantity"], product["product_name"]))
        connection.commit()
        return {"message": "Venta Registrada Exitosamente", "Precio Total": total_price}

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    finally:
        cursor.close()
        connection.close()