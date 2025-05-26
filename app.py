from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

# Ler variáveis de ambiente com default para evitar erros
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

    if user:
        return jsonify({"message": "Login OK", "user": user})
    else:
        return jsonify({"message": "Login falhou"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
