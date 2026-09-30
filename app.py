from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from ai_model import train_model, predict_crop

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, 'kisanmitra.db')
MODEL = os.path.join(BASE_DIR, 'crop_model.joblib')

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS recommendations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nitrogen REAL, phosphorus REAL, potassium REAL,
        temperature REAL, humidity REAL, ph REAL, rainfall REAL,
        crop TEXT, irrigation TEXT, fertilizer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')
    conn.commit(); conn.close()

def irrigation_advice(temp, humidity, rainfall):
    if rainfall >= 150:
        return 'Low irrigation need. Monitor soil moisture and avoid overwatering.'
    if temp >= 32 and humidity < 50:
        return 'High irrigation need. Water according to soil moisture and local conditions.'
    return 'Moderate irrigation need. Check soil moisture before watering.'

def fertilizer_advice(n, p, k):
    low = []
    if n < 50: low.append('nitrogen')
    if p < 40: low.append('phosphorus')
    if k < 40: low.append('potassium')
    if low:
        return 'Potentially low: ' + ', '.join(low) + '. Confirm with a soil test before applying fertilizer.'
    return 'N-P-K values are within the prototype target range. Follow soil-test recommendations.'

@app.get('/')
def index():
    return render_template('index.html')

@app.post('/api/register')
def register():
    data = request.get_json() or {}
    for key in ('name','email','password'):
        if not str(data.get(key, '')).strip(): return jsonify(error=f'{key} is required'), 400
    try:
        conn = get_db()
        conn.execute('INSERT INTO users(name,email,password_hash,location) VALUES(?,?,?,?)',
            (data['name'].strip(), data['email'].strip().lower(),
            generate_password_hash(data['password']), data.get('location','').strip()))
        conn.commit(); conn.close()
        return jsonify(message='Registration successful'), 201
    except sqlite3.IntegrityError:
        return jsonify(error='Email already registered'), 409

@app.post('/api/login')
def login():
    data = request.get_json() or {}
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email=?', (data.get('email','').lower(),)).fetchone()
    conn.close()
    if not user or not check_password_hash(user['password_hash'], data.get('password','')):
        return jsonify(error='Invalid email or password'), 401
    session['user_id'] = user['id']; session['name'] = user['name']
    return jsonify(message='Login successful', name=user['name'])

@app.post('/api/recommend')
def recommend():
    if 'user_id' not in session: return jsonify(error='Please login first'), 401
    data = request.get_json() or {}
    fields = ['n','p','k','temperature','humidity','ph','rainfall']
    try:
        values = {f: float(data[f]) for f in fields}
    except (KeyError, TypeError, ValueError):
        return jsonify(error='All numeric fields are required'), 400
    if not (0 <= values['ph'] <= 14): return jsonify(error='pH must be between 0 and 14'), 400
    crop = predict_crop([values[f] for f in fields], MODEL)
    irrigation = irrigation_advice(values['temperature'], values['humidity'], values['rainfall'])
    fertilizer = fertilizer_advice(values['n'], values['p'], values['k'])
    conn = get_db()
    conn.execute('''INSERT INTO recommendations
        (user_id,nitrogen,phosphorus,potassium,temperature,humidity,ph,rainfall,crop,irrigation,fertilizer)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
        (session['user_id'], values['n'], values['p'], values['k'], values['temperature'],
        values['humidity'], values['ph'], values['rainfall'], crop, irrigation, fertilizer))
    conn.commit(); conn.close()
    return jsonify(crop=crop, irrigation=irrigation, fertilizer=fertilizer)

@app.get('/api/history')
def history():
    if 'user_id' not in session: return jsonify(error='Login required'), 401
    conn = get_db()
    rows = conn.execute('SELECT * FROM recommendations WHERE user_id=? ORDER BY id DESC', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.get('/api/me')
def me():
    if 'user_id' not in session: return jsonify(authenticated=False)
    return jsonify(authenticated=True, name=session['name'])

@app.get('/api/logout')
def logout():
    session.clear(); return jsonify(message='Logged out')

if __name__ == '__main__':
    init_db()
    if not os.path.exists(MODEL): train_model(MODEL)
    app.run(debug=True)
