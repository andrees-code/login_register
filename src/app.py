from flask import Flask, flash, redirect, render_template, request, url_for, session
import hashlib
import mysql.connector
import os
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()
app.secret_key='clave_secreta_necesaria_para_usar_flash'

conexion = mysql.connector.connect(
    host='localhost',
    user= os.getenv('DATABASE_USER'),
    password= os.getenv('DATABASE_PASSWD'),
    database='login_register'
)

@app.route('/')
def home():
    if session.get('logged_in') == True:
        return render_template('home.html', title='home')
    return redirect('login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwd = request.form.get('passwd')

        if email and passwd:
            cursor = None
            hash_passwd = hashlib.sha256(passwd.encode('UTF-8')).hexdigest()

            try:
                cursor = conexion.cursor(dictionary=True, buffered=True)
                cursor.execute('SELECT * FROM usuarios WHERE email =%s',(email,))
                usuario = cursor.fetchone()
                if usuario:
                    if hash_passwd == usuario["passwd"]:
                        session["id"] = usuario["id"]
                        session["name"] = usuario["name"]
                        session["email"] = usuario["email"]
                        session["logged_in"] = True
                        flash('Sesion iniciada','success')
                        return redirect(url_for('home'))
                    flash('email o contraseña incorrectos.','danger')
                    return redirect(url_for('login'))
                flash('No se encuentra ningun usuario con ese correo.','danger')
                return redirect(url_for('login'))
            
            except Exception as e:
                print(e)

        flash('Completa todos los campos.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html', title='LOGIN')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        passwd = request.form.get('passwd')
        if name and email and passwd:
            if len(passwd) >= 6:
                cursor = None
                hash_passwd = hashlib.sha256(passwd.encode('UTF-8')).hexdigest()
                try:
                    cursor = conexion.cursor(dictionary=True, buffered=True)
                    cursor.execute('SELECT email FROM usuarios WHERE email = %s',(email,))
                    usuario = cursor.fetchone()
                    if usuario:
                        flash('usuario ya registrado.', 'danger')
                        return redirect(url_for('register'))
                    cursor.execute('INSERT INTO usuarios (name, email, passwd) VALUES(%s,%s,%s)', (name, email, hash_passwd))
                    conexion.commit()
                    cursor.execute('SELECT * FROM usuarios WHERE email =%s',(email,))
                    usuario = cursor.fetchone()
                    session["id"] = usuario["id"]
                    session["name"] = usuario["name"]
                    session["email"] = usuario["email"]
                    session["logged_in"] = True

                    flash('Usuario registrado correctamente.','success')
                    return redirect(url_for('home'))
                except Exception as e:
                    print(e)
                finally:
                    if cursor:
                        cursor.close()
            if len(passwd) <6:
                flash('La contraseña debe tener al menos 6 carácteres.', 'danger')
                return redirect(url_for('register'))
        if not (name and email and passwd):
            flash('Completa todos los campos.','danger')
            return redirect(url_for('register'))
    return render_template('register.html', title='REGISTER')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)