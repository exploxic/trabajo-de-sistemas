from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuración de conexión a MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # Cambia por tu usuario de MySQL
        password="",        # Cambia por tu contraseña de MySQL
        database="restaurante_db"
    )

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    return render_template('index.html')

# 1. MODULO PEDIDOS (PUNTO DE VENTA)
@app.route('/pedidos')
def pedidos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM platillos")
    platillos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos.html', platillos=platillos)

@app.route('/crear_pedido', methods=['POST'])
def crear_pedido():
    platillo_id = request.form.get('platillo_id')
    notas = request.form.get('notas')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Registrar la comanda
    cursor.execute("INSERT INTO pedidos (notas) VALUES (%s)", (notas,))
    pedido_id = cursor.lastrowid
    
    # 2. Registrar el detalle de la comanda
    cursor.execute("INSERT INTO detalle_pedidos (pedido_id, platillo_id) VALUES (%s, %s)", (pedido_id, platillo_id))
    
    # 3. AUTOMATIZACIÓN DE INVENTARIO: Descontar ingredientes según la receta
    cursor.execute("SELECT ingrediente_id, cantidad_requerida FROM recetas WHERE platillo_id = %s", (platillo_id,))
    receta = cursor.fetchall()
    
    for item in receta:
        cursor.execute(
            "UPDATE ingredientes SET cantidad_disponible = cantidad_disponible - %s WHERE id = %s",
            (item['cantidad_requerida'], item['ingrediente_id'])
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('pedidos'))

# 2. MÓDULO PANTALLA DE COCINA
@app.route('/cocina')
def cocina():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener órdenes activas ordenadas de manera cronológica[cite: 2]
    query = """
        SELECT p.id, p.estado, p.notas, p.fecha_hora, pl.nombre AS platillo
        FROM pedidos p
        JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        JOIN platillos pl ON dp.platillo_id = pl.id
        WHERE p.estado IN ('Pendiente', 'En preparación')
        ORDER BY p.fecha_hora ASC
    """
    cursor.execute(query)
    ordenes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('cocina.html', ordenes=ordenes)

@app.route('/cambiar_estado/<int:pedido_id>', methods=['POST'])
def cambiar_estado(pedido_id):
    nuevo_estado = request.form.get('estado')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (nuevo_estado, pedido_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('cocina'))

# 3. MÓDULO INVENTARIO Y PROVEEDORES
@app.route('/inventario')
def inventario():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ingredientes")
    ingredientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventario.html', ingredientes=ingredientes)

@app.route('/reabastecer', methods=['POST'])
def reabastecer():
    ingrediente_id = request.form.get('ingrediente_id')
    cantidad = request.form.get('cantidad')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ingredientes SET cantidad_disponible = cantidad_disponible + %s WHERE id = %s",
        (cantidad, ingrediente_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('inventario'))

if __name__ == '__main__':
    app.run(debug=True)