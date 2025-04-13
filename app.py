from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, request
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
import re
from datetime import datetime

from models.ModelUser import ModelUser

from models.entities.User import User

app = Flask(__name__)
db = MySQL(app)
login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    user = ModelUser.get_by_id(db, id)
    return user

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['Usuario'], request.form['Contraseña'])

        logged_user = ModelUser.login(db, user)
        if logged_user is not None:
            if logged_user.password:
                login_user(logged_user)
                return jsonify({"status": "success", "message": "Inicio exitoso"})
            else:
                return jsonify({"status": "error", "message": "Contraseña Incorrecta"})
        else:
            return jsonify({"status": "error", "message": "Usuario no encontrado"})
    else:
        return render_template('index.html')

    
@app.route("/logout")
def logout():
    logout_user()
    return render_template('index.html')

@app.route("/regist")
def regist():
    return render_template('registro.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    if request.form['Contraseña'] == request.form['Contraseña2']:
        user = User(0, request.form['Usuario'], request.form['Contraseña'], request.form['Nombre'], request.form['Apellido'])
        ver = Verificar(user)
        if ver == True:
            logged_user = ModelUser.registrar(db, user)
            login_user(logged_user)
            return jsonify({"status": "success", "redirect": url_for('home')})

        else: 
            return jsonify({"status": "error", "message": ver})
    else:
        return jsonify({"status": "error", "message": "La contraseña no coincide"})

def Verificar(user):

    patron = r'^[a-zA-Z0-9\s]+$'

    if user.nombre.strip() == "":
        return "El nombre no puede estar vacío o compuesto solo por espacios."
    if not re.match(patron, user.nombre):
        return "El nombre contiene caracteres no válidos."
    if len(user.nombre) > 25:
        return "El nombre no puede tener más de 25 caracteres."

    if user.apellido.strip() == "":
        return "El apellido no puede estar vacío o compuesto solo por espacios."
    if not re.match(patron, user.apellido):
        return "El apellido contiene caracteres no válidos."
    if len(user.apellido) > 25:
        return "El apellido no puede tener más de 25 caracteres."
    
    if user.username.strip() == "":
        return "El nombre de usuario no puede estar vacío o compuesto solo por espacios."
    if len(user.username) > 24:
        return "El Usuario no puede tener más de 25 caracteres."
    
    return True

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404

@app.route('/home')
@login_required
def home():
    cursor = db.connection.cursor()
    cursor.execute("SELECT ID, Usuario, Fecha, Nota FROM notas WHERE Usuario = %s ORDER BY Fecha DESC", (current_user.username,))
    notas = cursor.fetchall()
    cursor.close()
    return render_template('home.html', notas=notas)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    cursor = db.connection.cursor()

    if request.method == 'GET': 
        cursor.execute("SELECT ID, Nota FROM notas WHERE ID = %s", (id,))
        nota = cursor.fetchone()
        cursor.close()

        return render_template('edit.html', nota=nota)

    elif request.method == 'POST':
        nueva_nota = request.form['nota'].strip() 
        nueva_fecha = datetime.now().strftime('%Y-%m-%d')

        if len(nueva_nota) <= 800:
            cursor.execute("UPDATE notas SET Nota = %s, Fecha = %s WHERE ID = %s AND Usuario = %s",
                        (nueva_nota, nueva_fecha, id, current_user.username))
            db.connection.commit()
            cursor.close()

            return redirect(url_for('home'))
        
        else:
            if not nueva_nota:
                return jsonify({"status": "error", "message": "La nota no puede estar en blanco."})
            
            if len(nueva_nota) > 800:
                return jsonify({"status": "error", "message": "La nota no puede contener más de 800 caracteres."})

            else:
                cursor.execute("UPDATE notas SET Nota = %s, Fecha = %s WHERE ID = %s AND Usuario = %s",
                            (nueva_nota, nueva_fecha, id, current_user.username))
                db.connection.commit()
                cursor.close()

                return jsonify({"status": "success", "message": "Nota actualizada correctamente."})


@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    
    if request.method == 'GET':
        return render_template('crear.html')
    
    elif request.method == 'POST':
        cursor = db.connection.cursor()
        nota = request.form['nota'].strip() 
        fecha = datetime.now().strftime('%Y-%m-%d')

        if not nota:
            return jsonify({"status": "error", "message": "La nota no puede estar en blanco."})
                
        if len(nota) > 800:
            return jsonify({"status": "error", "message": "La nota no puede contener más de 800 caracteres."})

        else:
            cursor.execute("INSERT INTO notas (usuario, fecha, nota) VALUES (%s, %s, %s)",
                                (current_user.username, fecha, nota))
            db.connection.commit()
            cursor.close()

            return redirect(url_for('home'))

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, status_401)
    app.run(host='0.0.0.0')  # Ejecuta el servidor en http://127.0.0.1:5000
