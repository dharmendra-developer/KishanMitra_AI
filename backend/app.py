from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import sqlite3, uuid, os, json, datetime

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
DB = BASE / "kisanmitra.db"

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
      created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS expenses(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
      category TEXT, amount REAL, note TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS crop_history(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
      crop TEXT, sowing_date TEXT, notes TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS disease_history(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
      crop TEXT, disease TEXT, confidence REAL, image TEXT, created_at TEXT);
    """)
    con.commit(); con.close()

@app.get("/api/health")
def health():
    return jsonify({"status":"ok","service":"KisanMitra AI"})

@app.post("/api/register")
def register():
    d=request.get_json() or {}
    if not all(d.get(k) for k in ("name","phone","password")):
        return jsonify({"error":"name, phone and password are required"}),400
    con=db()
    try:
        cur=con.execute("INSERT INTO users(name,phone,password,created_at) VALUES(?,?,?,?)",
                        (d["name"],d["phone"],d["password"],datetime.datetime.now().isoformat()))
        con.commit()
        return jsonify({"id":cur.lastrowid,"name":d["name"]})
    except sqlite3.IntegrityError:
        return jsonify({"error":"Phone already registered"}),409
    finally: con.close()

@app.post("/api/login")
def login():
    d=request.get_json() or {}
    con=db()
    row=con.execute("SELECT id,name,phone FROM users WHERE phone=? AND password=?",
                    (d.get("phone"),d.get("password"))).fetchone()
    con.close()
    if not row: return jsonify({"error":"Invalid login"}),401
    return jsonify(dict(row))

@app.post("/api/crop-doctor")
def crop_doctor():
    f=request.files.get("image")
    if not f: return jsonify({"error":"Image is required"}),400
    name=f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
    path=UPLOADS/name; f.save(path)

    # Demo inference adapter. Replace with TensorFlow/PyTorch model in ml/predict.py.
    result={
      "crop":"Tomato",
      "disease":"Early Blight",
      "severity":"Moderate",
      "confidence":0.86,
      "expert_verification_recommended": False,
      "treatment":[
        "Remove severely infected leaves and keep the field clean.",
        "Avoid overhead irrigation and improve air circulation.",
        "Use only locally approved fungicides according to the product label."
      ],
      "image":name
    }
    return jsonify(result)

@app.get("/api/weather")
def weather():
    # Demo weather endpoint. Connect OpenWeather/IMD-compatible provider in production.
    city=request.args.get("city","Your Location")
    return jsonify({
      "city":city,"temperature":31,"humidity":68,"wind_kmph":12,
      "rain_probability":42,"condition":"Partly Cloudy",
      "advisory":"Check soil moisture before irrigation; rain is possible."
    })

@app.post("/api/soil")
def soil():
    d=request.get_json() or {}
    ph=float(d.get("ph",7)); n=float(d.get("nitrogen",0)); p=float(d.get("phosphorus",0)); k=float(d.get("potassium",0))
    fertility="High" if (n+p+k)>220 else ("Medium" if (n+p+k)>=120 else "Low")
    crops=["Rice","Wheat","Maize"] if 5.5<=ph<=7.5 else ["Millets","Pulses"]
    return jsonify({"fertility":fertility,"suitable_crops":crops,
                    "fertilizer_advice":"Use a soil-test-based balanced N-P-K plan; avoid over-fertilization."})

@app.post("/api/irrigation")
def irrigation():
    d=request.get_json() or {}
    moisture=float(d.get("moisture",40))
    crop=d.get("crop","Crop")
    if moisture < 30: rec="Irrigate soon; soil moisture is low."
    elif moisture < 50: rec="Light irrigation may be needed after checking weather."
    else: rec="No immediate irrigation required."
    return jsonify({"crop":crop,"soil_moisture":moisture,"recommendation":rec})

@app.post("/api/crop-recommendation")
def crop_recommendation():
    d=request.get_json() or {}
    ph=float(d.get("ph",7)); water=d.get("water","medium"); season=d.get("season","Kharif")
    base=[("Rice",92),("Maize",84),("Soybean",78)] if season=="Kharif" else [("Wheat",93),("Mustard",86),("Pea",79)]
    if water=="low": base=[(c, max(55,s-12)) for c,s in base if c!="Rice"]
    return jsonify({"recommendations":[{"crop":c,"suitability":s} for c,s in base],
                    "soil_ph":ph})

@app.get("/api/market")
def market():
    return jsonify({"markets":[
      {"crop":"Wheat","market":"Local Mandi","price":2450,"unit":"₹/quintal","trend":"up"},
      {"crop":"Rice","market":"Local Mandi","price":2280,"unit":"₹/quintal","trend":"stable"},
      {"crop":"Maize","market":"Local Mandi","price":2100,"unit":"₹/quintal","trend":"up"}
    ],"notice":"Demo prices. Replace with a verified live mandi data source before deployment."})

@app.get("/api/schemes")
def schemes():
    q=request.args.get("q","").lower()
    data=[
      {"name":"PM-KISAN","description":"Income support scheme for eligible farmer families.","documents":"Aadhaar, bank account and land-related details as applicable."},
      {"name":"Pradhan Mantri Fasal Bima Yojana","description":"Crop insurance scheme for eligible notified crops/areas.","documents":"Policy/application and crop/land details as applicable."}
    ]
    return jsonify([x for x in data if not q or q in x["name"].lower()])

@app.post("/api/expenses")
def add_expense():
    d=request.get_json() or {}
    con=db()
    con.execute("INSERT INTO expenses(user_id,category,amount,note,created_at) VALUES(?,?,?,?,?)",
                (d.get("user_id"),d.get("category"),float(d.get("amount",0)),d.get("note",""),datetime.datetime.now().isoformat()))
    con.commit(); con.close()
    return jsonify({"message":"Expense saved"})

@app.get("/api/expenses/<int:user_id>")
def expenses(user_id):
    con=db()
    rows=con.execute("SELECT * FROM expenses WHERE user_id=? ORDER BY id DESC",(user_id,)).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])

@app.post("/api/chat")
def chat():
    q=(request.get_json() or {}).get("message","").lower()
    if "water" in q or "irrigation" in q:
        a="Irrigation should depend on crop stage, soil moisture and upcoming rain. Check moisture before watering."
    elif "disease" in q:
        a="Upload a clear leaf photo in AI Crop Doctor. Low-confidence results should be verified by an agriculture expert."
    elif "fertilizer" in q:
        a="Use a soil-test-based fertilizer plan and follow locally approved product labels."
    else:
        a="I can help with crop disease, irrigation, soil, fertilizer, weather and farming decisions."
    return jsonify({"answer":a})

if __name__=="__main__":
    init_db()
    app.run(host="0.0.0.0",port=4000,debug=True)
