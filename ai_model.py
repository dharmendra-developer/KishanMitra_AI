import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Educational demo data: [N, P, K, temperature, humidity, pH, rainfall]
X = np.array([
 [90,42,43,20.9,82,6.5,202],[85,58,41,21.8,80,6.3,190],
 [60,55,44,23,72,6.7,150],[30,40,30,27,55,6.5,80],
 [25,35,25,29,50,7.0,60],[70,45,50,24,70,6.2,130],
 [100,60,45,22,85,6.4,210],[40,50,40,26,60,6.8,100],
 [20,30,20,31,45,7.2,45],[75,50,55,25,75,6.5,160],
 [35,42,35,28,58,6.9,90],[95,48,48,21,83,6.4,205],
 [65,50,42,24,68,6.6,140],[28,38,28,30,48,7.1,55]
])
y = np.array(['Rice','Rice','Maize','Cotton','Millet','Maize','Rice','Cotton','Millet','Maize','Cotton','Rice','Maize','Millet'])

def train_model(path='crop_model.joblib'):
    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X, y)
    joblib.dump(model, path)
    return model

def predict_crop(values, path='crop_model.joblib'):
    model = joblib.load(path) if os.path.exists(path) else train_model(path)
    return str(model.predict([values])[0])
