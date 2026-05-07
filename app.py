@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Pata data na ulazimishe (force) JSON hata kama header ina tatizo
        data = request.get_json(force=True)
        
        # Hii itakuonyesha kwenye Render Logs kile kinachotumwa kutoka kwa JS
        print(f"DEBUG: Data iliyopokelewa: {data}")

        if not data:
            return jsonify({"error": "No data received"}), 400

        # 2. Toa data kwa usalama. Ikiwa key haipo, itatumia 0 badala ya kuleta Error 400
        try:
            features = [
                float(data.get('v_x', 0)), 
                float(data.get('v_y', 0)), 
                float(data.get('v_z', 0)),
                float(data.get('temp', 0)), 
                float(data.get('curr', 0)), 
                float(data.get('rpm', 0)),
                float(data.get('pres', 0)), 
                0, 0, 0, 0, 0  # Wavelet features ambazo modeli inatarajia
            ]
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Invalid number format: {str(e)}"}), 400

        input_df = pd.DataFrame([features], columns=COLUMNS)
        
        # 3. Health Status Confidence
        is_faulty = int(binary_model.predict(input_df))
        binary_probs = binary_model.predict_proba(input_df)
        health_confidence = binary_probs[0][is_faulty] * 100

        diagnosis = ""
        diag_confidence = 0
        
        if is_faulty == 1:
            # 4. Specific Problem Confidence
            fault_name = diagnostic_model.predict(input_df)[0]
            diag_probs = diagnostic_model.predict_proba(input_df)
            
            # Tafuta index ya class iliyotabiriwa
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
        # Hii itatusaidia kuona kosa halisi kwenye logs kama kodi itafeli
        print(f"SERVER ERROR: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
