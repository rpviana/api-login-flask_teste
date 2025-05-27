from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Configurações secretas e DB
SECRET_KEY = os.getenv('JWT_SECRET', 'RPViana2005RPViana2005RPViana2005')

host = os.getenv("MYSQLHOST", "localhost")
user = os.getenv("MYSQLUSER", "root")
password = os.getenv("MYSQLPASSWORD", "")
database = os.getenv("MYSQLDATABASE", "testdb")
port = int(os.getenv("MYSQLPORT", 3306))

def get_db_connection():
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )

# Middleware para proteger rotas com JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Pega token do header Authorization: Bearer token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token em falta'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['username']
        except Exception as e:
            return jsonify({'message': 'Token inválido ou expirado'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return "API a correr"

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password_input = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password_input))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"message": "Login falhou"}), 401

    # Criar token JWT válido por 30 min
    token = jwt.encode({
        'username': username,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

# Rota protegida - só funciona com token válido
@app.route('/perfil', methods=['GET'])
@token_required
def perfil(current_user):
    return jsonify({"message": f"Bem-vindo {current_user} à área protegida!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
