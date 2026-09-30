# KisanMitra AI — Smart Agriculture Platform

A CSE final-year project MVP combining AI Crop Doctor, weather advisory, soil health, irrigation, crop recommendation, mandi prices, schemes, farm calculator and AI chatbot.

## Tech Stack
- Frontend: React + Vite + Axios
- Backend: Python Flask + SQLite + Flask-CORS
- ML adapter: Python; plug TensorFlow/PyTorch model into `ml/predict.py`

## Run

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the Vite URL shown in terminal.

## Important
This starter uses demo weather/market data and a demo disease inference response. For a real deployment, connect verified live APIs and a properly trained/validated crop-disease model. Never treat an AI prediction as a guaranteed diagnosis.
