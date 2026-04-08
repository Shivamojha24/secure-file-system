from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
import os
import bcrypt
import hashlib
import sqlite3
from cryptography.fernet import Fernet

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------- Encryption Key ----------
if not os.path.exists("key.key"):
    with open("key.key", "wb") as f:
        f.write(Fernet.generate_key())

with open("key.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)

# ---------- Database ----------
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    filename TEXT,
    owner TEXT,
    hash TEXT
)
""")

conn.commit()

# ---------- Auth Check ----------
def check_auth():
    return session.get('user')

# ---------- Register ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"message": "User registered"})
    except:
        return jsonify({"message": "User already exists"}), 400

# ---------- Login ----------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password'].encode()

    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    if result and bcrypt.checkpw(password, result[0]):
        session['user'] = username
        return jsonify({"message": "Login success"})
    
    return jsonify({"message": "Invalid credentials"}), 401

# ---------- Upload ----------
@app.route('/api/upload', methods=['POST'])
def upload():
    user = check_auth()
    if not user:
        return jsonify({"message": "Login required"}), 401

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    data = file.read()
    file_hash = hashlib.sha256(data).hexdigest()
    encrypted = cipher.encrypt(data)

    with open(filepath, 'wb') as f:
        f.write(encrypted)

    cursor.execute("INSERT INTO files VALUES (?, ?, ?)",
                   (file.filename, user, file_hash))
    conn.commit()

    return jsonify({"message": "File uploaded securely"})

# ---------- List Files ----------
@app.route('/api/files', methods=['GET'])
def files():
    user = check_auth()
    if not user:
        return jsonify({"message": "Login required"}), 401

    cursor.execute("SELECT filename FROM files WHERE owner=?", (user,))
    files = [row[0] for row in cursor.fetchall()]
    return jsonify(files)

# ---------- Download ----------
@app.route('/api/download/<filename>', methods=['GET'])
def download(filename):
    user = check_auth()
    if not user:
        return "Login required", 401

    cursor.execute("SELECT owner, hash FROM files WHERE filename=?", (filename,))
    result = cursor.fetchone()

    if not result:
        return "File not found", 404

    owner, saved_hash = result

    if owner != user:
        return "Unauthorized", 403

    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, 'rb') as f:
        encrypted = f.read()

    decrypted = cipher.decrypt(encrypted)

    current_hash = hashlib.sha256(decrypted).hexdigest()
    if current_hash != saved_hash:
        return "File corrupted!", 500

    temp = "temp_" + filename
    with open(temp, 'wb') as f:
        f.write(decrypted)

    return send_file(temp, as_attachment=True)

# ---------- Logout ----------
@app.route('/api/logout')
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logged out"})

if __name__ == '__main__':
    app.run(debug=True)