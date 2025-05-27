from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Chave secreta para JWT (altera para algo seguro em produção)
SECRET_KEY = os.getenv('JWT_SECRET', 'RPViana2005RPViana2005RPViana2005')

# Parse da string de conexão MySQL (public URL do Railway)
db_url = os.getenv(
    'MYSQL_URL',
    'mysql://root:UwKvnlVfgniKIZBTMGdSUxqTCzCVexzp@ballast.proxy.rlwy.net:11454/railway'
)
parsed = urlparse(db_url)
DB_HOST = parsed.hostname
DB_USER = parsed.username
DB_PASS = parsed.password
DB_NAME = parsed.path.lstrip('/')
DB_PORT = parsed.port

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT
    )

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return jsonify({'message': 'Token em falta'}), 401
        parts = auth.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'message': 'Formato de token inválido'}), 401
        token = parts[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = payload.get('username')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except Exception:
            return jsonify({'message': 'Token inválido'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return "API a correr"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username')
    password_input = data.get('password')
    if not username or not password_input:
        return jsonify({'message': 'Username e password obrigatórios'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username FROM users WHERE username = %s AND password = %s",
        (username, password_input)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"message": "Login falhou"}), 401

    token = jwt.encode({
        'username': user['username'],
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, SECRET_KEY, algorithm='HS256')

    # Se PyJWT devolver bytes (v3.x), converte para str
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return jsonify({"token": token})

@app.route('/perfil', methods=['GET'])
@token_required
def perfil(current_user):
    return jsonify({"message": f"Bem-vindo {current_user} à área protegida!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
