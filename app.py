from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import jwt
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Chave secreta para JWT
SECRET_KEY = 'RPViana2005RPViana2005RPViana2005'

def get_db_connection():
    return mysql.connector.connect(
        host="ballast.proxy.rlwy.net",
        user="root",
        password="UwKvnlVfgniKIZBTMGdSUxqTCzCVexzp",
        database="railway",
        port=11454
    )

# Middleware para verificar token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

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
        except Exception:
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

    token = jwt.encode({
        'username': username,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

@app.route('/perfil', methods=['GET'])
@token_required
def perfil(current_user):
    return jsonify({"message": f"Bem-vindo {current_user} à área protegida!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
