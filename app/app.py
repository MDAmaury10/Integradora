
from flask_wtf.csrf import CSRFProtect
from psycopg2.extras import RealDictCursor
import os
import psycopg2
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, render_template, url_for, redirect, request, flash
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, logout_user
from Models.ModelUser import ModelUser
from Models.entitites.user import User



app = Flask(__name__)
csrf=CSRFProtect()

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}


def get_db_connection():
    try:
        conn = psycopg2.connect(host='localhost', 
                                dbname='integradora', 
                                user=os.environ['DB_USERNAME'], 
                                password=os.environ['DB_PASSWORD'])
        return conn
    except psycopg2.Error as error:
        print(f"Error al conectar a la base de datos:{error}")
        return None

app.secret_key='mysecretkey'

login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(idusuarios):
    return ModelUser.get_by_id(get_db_connection(),idusuarios)
   


def my_random_string(string_length=10):
    random=str(uuid.uuid4())
    random = random.upper()
    random=random.replace("-", "")
    return random[0:string_length]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

#<----------------LOGIN------------------>
@app.route("/")
def login():
    return render_template('login.html')

@app.route('/loguear', methods=('GET', 'POST'))
def loguear():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        user=User(0, username, password, None, None)
        loged_user= ModelUser.login(get_db_connection(), user)
        print(user.username)
        print(loged_user)

        if loged_user != None :
            if loged_user.password:
                login_user(loged_user)
                return redirect(url_for('index'))
            else:
                flash('Nombre de usuario y/o contraseña incorecta.')
                return redirect (url_for('login'))
        else:
            flash('Nombre de usuario y/o contraseña incorrecta.')
            return redirect (url_for('login'))
    else:

        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/prueba')
def prueba():
    return render_template('prueba.html')

def pagina_no_encontrada(error):
    return render_template('404.html')

#@app.errorhandler(404)
#def pagina_no_encontrada(e):
 #   if not current_user.is_authenticated:
  #      return redirect(url_for('login'))
   # return render_template('404.html'), 404

#<----------------PAGINACION----------------->
def paginador(sql_count, sql_lim, in_page, per_pages):
    page = request.args.get('page', in_page, type=int)
    per_page = request.args.get('per_page', per_pages, type=int)

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(sql_count)
    total_items = cursor.fetchone()['count']

    cursor.execute(sql_lim + " LIMIT %s OFFSET %s", (per_page, offset))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_items + per_page - 1) // per_page

    return items, page, per_page, total_items, total_pages



@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/productos')
@login_required
def productos():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql_count='SELECT COUNT(*) FROM productos_sql'
        sql_lim='SELECT * FROM productos_sql'
        #cursor.execute(sql)
        productos, page, per_page, total_items, total_pages = paginador(sql_count, sql_lim, in_page=1, per_pages=10)
        #productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('productos.html', productos=productos, page=page, per_page=per_page, total_items=total_items, total_pages=total_pages)
    else:
        flash('Error al conectar a la base de datos.')
        return redirect(url_for('index'))
        

@app.route('/productos/crear')
@login_required
def productos_crear():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_categoria, nombre FROM categorias')
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('productos_crear.html', categorias=categorias)
    else:
        flash('Error al conectar a la base de datos.')
        return redirect(url_for('index'))


@app.route('/productos/nuevo', methods =['GET', 'POST'])    
@login_required
def productos_nuevo():
    if request.method=='POST':
        nombre=request.form['nombre']
        marca=request.form['marca']
        stock=int(request.form['stock'])
        precio=float(request.form['precio'])
        categoria=int(request.form['categoria'])
        
        conn=get_db_connection()
        cur=conn.cursor()
        cur.execute ('INSERT INTO productos (nombre, marca, stock, precio, id_categoria)'
                    'VALUES (%s, %s, %s, %s, %s)',
                    (nombre, marca, stock, precio, categoria))
        conn.commit()
        cur.close()
        conn.close() 
        
        flash('¡Producto creado de manera correcta!')
        return redirect(url_for('productos'))

    else:

        flash('Error al crear el nuevo producto')
        return redirect(url_for('productos'))
    
@app.route('/productos/detalles/<string:id>', methods=['GET', 'POST'])
@login_required
def productos_detalles(id):
    titulo = 'Detalles del producto'
    conn = get_db_connection()
    cur = conn.cursor()

    # Obtener el producto
    cur.execute('SELECT * FROM productos WHERE id_producto=%s',(id,))
    producto = cur.fetchall()

    # Obtener todas las categorías
    cur.execute('SELECT id_categoria, nombre FROM categorias')
    categorias = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('productos_detalles.html', titulo=titulo, producto=producto[0], categorias=categorias)


@app.route('/productos/editar/<string:id>')
@login_required
def productos_editar(id):
    titulo= 'Detalles del producto'
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM productos WHERE id_producto=%s',(id,))
    producto=cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('productos_detalles.html', titulo=titulo, producto=producto[0])

@app.route('/productos/actualizar/<string:id>', methods=['POST'])
@login_required
def productos_actualizar(id):
    if request. method == 'POST':
        nombre=request.form['nombre']
        marca=request.form['marca']
        stock=int(request.form['stock'])
        precio=float(request.form['precio'])
        categoria=int(request.form['id_categoria'])
        conn=get_db_connection()
        cur=conn.cursor()
        sql='UPDATE productos SET nombre=%s, marca=%s, stock=%s, precio=%s, id_categoria=%s WHERE id_producto=%s'
        values=(nombre, marca, stock, precio, categoria, id)
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        flash('Producto editado de manera correcta')
        return redirect (url_for('productos'))
    
    else: 
        flash('Error al hacer la edición del producto')
        return render_template('productos.html')
    
@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def productos_eliminar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM productos WHERE id_producto = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Producto eliminado de manera correcta!')
    return redirect(url_for('productos'))

@app.route('/proveedores')
@login_required
def proveedores():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        sql_count='SELECT COUNT (*) FROM proveedores_sql'
        sql_lim='SELECT * FROM proveedores_sql'
        #cur.execute(sql)
        proveedores, page, per_page, total_items, total_pages = paginador(sql_count, sql_lim, in_page=1, per_pages=10)
        #proveedores = cur.fetchall()
        cur.close()
        conn.close()
        return render_template ('proveedores.html', proveedores=proveedores, page=page, per_page=per_page, total_items=total_items, total_pages=total_pages)
    else:
        flash('Error al conectar a la base de datos.')
        return redirect(url_for('index'))
    
@app.route('/proveedores/crear')
@login_required
def proveedores_crear():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        sql='SELECT id_producto, nombre FROM productos'
        cur.execute(sql)
        productos = cur.fetchall()
        cur.close()
        conn.close()
        return render_template ('proveedores_crear.html', productos=productos)
    else:
        flash('Error al conectar a la base de datos.')
        return redirect(url_for('index'))

@app.route('/proveedores/nuevo', methods =['GET', 'POST'])    
@login_required
def proveedores_nuevo():
    if request.method=='POST':
        contacto=request.form['contacto']
        diaPedido=request.form['diaPedido']
        diaEntrega=request.form['diaEntrega']
        totalPago=float(request.form['totalPago'])
        producto=int(request.form['producto'])
        
        conn=get_db_connection()
        cur=conn.cursor()
        cur.execute ('INSERT INTO proveedores (contacto, dia_pedido, dia_entrega, total_pagado, id_producto) VALUES (%s, %s, %s, %s, %s)',
                    (contacto, diaPedido, diaEntrega, totalPago, producto))
        conn.commit()
        cur.close()
        conn.close() 
        
        flash('¡Proveedor agregado de manera correcta!')
        return redirect(url_for('proveedores'))

    else:

        flash('Error al crear el nuevo proveedor')
        return redirect(url_for('proveedores'))

@app.route('/proveedores/detalles/<string:id>', methods=['GET', 'POST'])
@login_required
def proveedores_detalles(id):
    titulo= 'Detalles de proveedor'
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM proveedores WHERE id_proveedor=%s',(id,))
    proveedores=cur.fetchall()
    cur.execute('SELECT id_producto, nombre FROM productos')
    productos=cur.fetchall()
    cur.close()
    conn.close()
    return render_template('proveedores_detalles.html', titulo=titulo, proveedores=proveedores[0], productos=productos)

@app.route('/proveedores/editar/<string:id>')
@login_required
def proveedores_editar(id):
    titulo= 'Detalles del proveedor'
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM proveedores WHERE id_proveedor=%s',(id,))
    proveedores=cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('proveedores_detalles.html', titulo=titulo, proveedores=proveedores)

@app.route('/proveedores/actualizar/<string:id>', methods =['GET', 'POST'])
@login_required
def proveedores_actualizar(id):
    if request.method == 'POST':
        contacto=request.form['contacto']
        diaPedido=request.form['diaPedido']
        diaEntrega=request.form['diaEntrega']
        totalPago=request.form['totalPago']
        producto=request.form['producto']
        conn=get_db_connection()
        cur=conn.cursor()
        sql='UPDATE proveedores SET contacto=%s, dia_pedido=%s, dia_entrega=%s, total_pagado=%s, id_producto=%s WHERE id_proveedor=%s'
        values=(contacto, diaPedido, diaEntrega, totalPago, producto, id)
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        flash ('¡Proveedor editado de manera correcta!')
        return redirect (url_for('proveedores'))
    else:
        flash('Error al hacer la edición de proveedor')
        return redirect(url_for('proveedores'))

@app.route('/proveedores/eliminar/<string:id>', methods=['POST'])
@login_required
def proveedores_eliminar(id):
    conn=get_db_connection()
    cur=conn.cursor()
    sql='DELETE FROM proveedores WHERE id_proveedor=%s'
    values=(id,)
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Proveedor eliminado de manera correcta!')
    return redirect(url_for('proveedores'))

@app.route('/categorias')
@login_required
def categorias():
    conn = get_db_connection()
    if conn:
        cur= conn.cursor()
        sql_count='SELECT COUNT (*) FROM categorias'
        sql_lim='SELECT * FROM categorias'
        #cur.execute(sql)
        categorias, page, per_page, total_items, total_pages = paginador(sql_count, sql_lim, in_page=1, per_pages=10)
        #categorias=cur.fetchall()
        cur.close()
        conn.close()
        return render_template('categorias.html', categorias=categorias, page=page, per_page=per_page, total_items=total_items, total_pages=total_pages)
    else:
        flash('Error al conectar a la base de datos')
        return redirect(url_for('index'))
    
@app.route('/categorias/crear')
@login_required
def categorias_crear():
    return render_template('categorias_crear.html')

@app.route('/categorias/nuevo', methods=['POST'])
@login_required
def categorias_nuevo():
    if request.method =='POST':
        nombre=request.form['nombre_categoria']
        conn=get_db_connection()
        cur=conn.cursor()
        sql='INSERT INTO categorias (nombre) VALUES (%s)'
        values=(nombre,)
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Categoria creada de manera correcta!')
        return redirect(url_for('categorias'))
    
    else:

        flash('Error al crear la nueva categoria')
        return redirect(url_for('categorias'))
    
@app.route('/categorias/detalles/<string:id>')
@login_required
def categorias_detalles(id):
    titulo= 'Detalles de la categoria'
    conn=get_db_connection()
    cur=conn.cursor()
    sql='SELECT * FROM categorias WHERE id_categoria=%s'
    values=(id,)
    cur.execute(sql, values)
    categorias=cur.fetchall()
    cur.close()
    conn.close()
    return render_template('categorias_detalles.html', tituolo=titulo, categoria=categorias[0])

@app.route('/categorias/editar/<string:id>')
@login_required
def categorias_editar(id):
    titulo='Editar categoria'
    conn=get_db_connection()
    cur=conn.cursor()
    sql='SELECT * FROM categorias WHERE id_categoria=%s'
    values=(id,)
    cur.execute(sql, values)
    categorias=cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return render_template ('categorias_detalles.html', titulo=titulo, categoria=categorias)

@app.route('/categorias/actualizar/<string:id>', methods=['GET, POST'])
@login_required
def categorias_actualizar(id):
    if request.method=='POST':
        nombre=request.form['nombre_categoria']
        conn=get_db_connection()
        cur=conn.cursor()
        sql='UPDATE categorias SET nombre=%s WHERE id_categoria=%s'
        values=(nombre, id)
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        flash('¡Categoria editada de manera correcta!')
        return redirect(url_for('categorias'))
    else:
        flash('¡Error al hacer la edicion de la categoria!')
        return redirect(url_for('categorias'))
    
@app.route('/categorias/eliminar/<string:id>', methods=['POST'])
@login_required
def categorias_eliminar(id):
    conn=get_db_connection()
    cur=conn.cursor()
    sql='DELETE FROM categorias WHERE id_categoria=%s'
    values=(id,)
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
    flash('Categoria eliminada de manera correcta') 
    return redirect(url_for('categorias'))       


@app.route('/usuarios')
@login_required
def usuarios():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql_count='SELECT COUNT (*) FROM usuarios'
        sql_lim='SELECT * FROM usuarios'
        #cursor.execute(sql)
        usuarios, page, per_page, total_items, total_pages = paginador(sql_count, sql_lim, in_page=1, per_pages=10)
        #usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('usuarios.html', usuarios=usuarios, page=page, per_page=per_page, total_items=total_items, total_pages=total_pages )
    else:
        flash('Error al conectar a la base de datos.')
        return redirect(url_for('index'))
            
@app.route('/usuarios/crear')
@login_required
def usuarios_crear():
        return render_template('usuarios_crear.html')

@app.route('/usuarios/nuevo', methods=['POST'])
@login_required
def usuarios_nuevo():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        rol = request.form.get('rol')
        active = request.form.get('active') == 'on'
        
        imagen = request.files.get('imagen')
        imagen_filename = None

        if imagen and imagen.filename != '' and allowed_file(imagen.filename):
            imagen_filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
            
            # Guarda el archivo en la carpeta de subida
            imagen.save(imagen_path)

        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cur = conn.cursor()

        sql = 'INSERT INTO usuarios (name, password, rol, activo, imagen) VALUES (%s, %s, %s, %s, %s)'
        values = (name, hashed_password, rol, active, imagen_filename)
        
        try:
            cur.execute(sql, values)
            conn.commit()
            flash('¡Usuario agregado de manera correcta!')
        except Exception as e:
            conn.rollback()
            flash(f'Error al crear al nuevo usuario: {str(e)}')
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('usuarios'))
    else:
        flash('Error al crear al nuevo usuario')
        return redirect(url_for('usuarios'))

    
@app.route('/usuarios/detalles/<string:id>', methods=['GET'])
@login_required
def usuarios_detalles(id):
    titulo = 'Detalles del usuario'
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    sql = 'SELECT * FROM usuarios WHERE id_usuario=%s'
    cur.execute(sql, (id,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('usuarios_detalles.html', titulo=titulo, usuario=usuario)


@app.route('/usuarios/editar/<string:id>')
@login_required
def usuarios_editar(id):
    titulo = 'Detalles del usuario'
    conn=get_db_connection()
    cur=conn.cursor()
    sql = 'SELECT * FROM USUARIOS WHERE id_usuario=%s'
    cur.execute(sql, (id,))
    usuarios=cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return render_template ('usuarios_detalles.html', titulo=titulo, usuarios=usuarios)

@app.route('/usuarios/actualizar/<string:id>', methods=['GET', 'POST'])
@login_required
def usuarios_actualizar(id):
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        rol=request.form['rol']
        active=request.form['active'] == 'on'
        hashed_password = generate_password_hash(password)
        conn=get_db_connection()
        cur=conn.cursor()
        sql = 'UPDATE usuarios SET name=%s, password=%s, rol=%s, activo=%s WHERE id_usuario=%s'
        values = (name, hashed_password, rol, active, id)
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        flash('¡Usuario editadi de manera correcta!')
        return redirect(url_for('usuarios'))
    else:
        flash('Error al hacer la edicion de usuario')
        return redirect (url_for('usuarios'))
    
@app.route('/usuarios/eliminar/<string:id>', methods=['POST'])
@login_required
def usuarios_eliminar(id):
    conn=get_db_connection()
    cur=conn.cursor()
    sql='DELETE FROM usuarios WHERE id_usuario=%s'
    values=(id,)
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Usuario eliminado de manera correcta!')
    return redirect(url_for('usuarios'))    


@app.route ('/ventas')
@login_required
def ventas():
    conn=get_db_connection()
    if conn:
        cur = conn.cursor()
        sql_count='SELECT COUNT (*) FROM ventas'
        sql_lim='SELECT * FROM ventas'
        ventas, page, per_page, total_items, total_pages = paginador(sql_count, sql_lim, in_page=1, per_pages=10)
        cur.close()
        conn.close()
        return render_template('ventas.html', ventas=ventas, page=page, per_page=per_page, total_items=total_items, total_pages=total_pages)
    else:
        flash('Error al conectar a la base de datos')
        return redirect(url_for('index'))


@app.route('/ventas/crear')
@login_required
def ventas_crear():
    conn=get_db_connection()
    if conn:
        cur=conn.cursor()
        sql='SELECT id_producto, nombre from productos'
        cur.execute(sql)
        productos=cur.fetchall()
        cur.close()
        conn.close()
        return render_template ('ventas_crear.html', productos=productos)
    else:
        flash('Error al conectar a la base de datos.')
        return redirect(url_for('index'))

@app.route('/ventas/nuevo', methods= ['POST'])
@login_required
def ventas_nuevo():
    productos
    if request.method == 'POST':
        #repetir las veces necesarias
        x=request.form[x]
        conn=get_db_connection()
        cur=conn.cursor()
        sql=''
        values=()
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()

        flash('Venta realizada de manera correcta')
        return redirect(url_for('ventas_crear', productos=productos))
    else:
        flash('Error al conectar a la base de datos')
        return redirect(url_for('ventas_crear'))
    


##    if conn:
  #      conn=get_db_connection()
#        cur=conn.cursor()
   #     sql_count='SELECT COUNT (*) FROM ventas'
    #    sql_lim='SELECT * FROM ventas'
     #   ventas, page, per_page, total_items, total_pages = paginador(sql_count, sql_lim, in_page=1, per_pages=10)
      #  cur.close
       # conn.close
        #return render_template('ventas.html', ventas=ventas, page=page, per_page=per_page, total_items=total_items, total_pages=total_pages)
   # else:
    #    flash('Error al conectar a la base de datos')
     #   return redirect (url_for('index'))








if __name__ == '__main__':
    csrf.init_app(app)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, pagina_no_encontrada)
    app.run(debug=True, port=5000)
