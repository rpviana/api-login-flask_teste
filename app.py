# app.py
from flask import Flask, request, jsonify
import mysql.connector
import os
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'muda_isto_para_uma_chave_secreta_bem_forte'

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "localhost"),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", ""),
        database=os.getenv("MYSQLDATABASE", "testdb"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password_input = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password_input))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        user.pop('password', None)  # tira a password do JSON
        return jsonify({"message": "Login OK", "token": token, "user": user})
    return jsonify({"message": "Login falhou"}), 401

@app.route('/dados', methods=['GET'])
def dados():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Token em falta"}), 401

    try:
        token = auth_header.split()[1]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        # Se quiseres, podes usar payload['user_id'] para buscar dados específicos

        return jsonify({"data": f"Olá {payload['username']}, esta info está protegida."})
    except Exception:
        return jsonify({"message": "Token inválido"}), 401

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
