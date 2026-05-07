from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load your models
# Ensure these files are in your main folder on GitHub
binary_model = joblib.load('model.pkl')
diagnostic_model = joblib.load('fault_type_model.pkl')

COLUMNS = [
    'vibration_x', 'vibration_y', 'vibration_z', 'temperature_c', 
    'current_a', 'rpm', 'pressure_bar', 'wavelet_feature_1', 
    'wavelet_feature_2', 'wavelet_feature_3', 'wavelet_feature_4', 'wavelet_feature_5'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Force JSON parsing and use .get() for safety
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data received"}), 400

        features = [
            float(data.get('v_x', 0)), 
            float(data.get('v_y', 0)), 
            float(data.get('v_z', 0)),
            float(data.get('temp', 0)), 
            float(data.get('curr', 0)), 
            float(data.get('rpm', 0)),
            float(data.get('pres', 0)), 
            0, 0, 0, 0, 0
        ]
        
        input_df = pd.DataFrame([features], columns=COLUMNS)
        
        # 1. Health Status Confidence
        is_faulty = int(binary_model.predict(input_df)[0])
        binary_probs = binary_model.predict_proba(input_df)
        health_confidence = binary_probs[0][is_faulty] * 100

        diagnosis = ""
        diag_confidence = 0
        
        if is_faulty == 1:
            # 2. Specific Problem Confidence
            fault_name = diagnostic_model.predict(input_df)[0]
            diag_probs = diagnostic_model.predict_proba(input_df)
            class_idx = np.where(diagnostic_model.classes_ == fault_name)[0][0]
            diag_confidence = diag_probs[0][class_idx] * 100
            
            diagnosis = str(fault_name).replace('_', ' ').upper()
            status = "🚨 MAINTENANCE REQUIRED"
            color = "#ff4b2b"
        else:
            status = "✅ MACHINE HEALTHY"
            color = "#00ff87"

        return jsonify({
            "status": status,
            "health_conf": f"{health_confidence:.2f}%",
            "diagnosis": diagnosis,
            "diag_conf": f"{diag_confidence:.2f}%" if diagnosis else None,
            "result_color": color
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # Use the port Render provides or default to 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
