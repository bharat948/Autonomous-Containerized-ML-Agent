import sys
import json
import joblib
import pandas as pd
import numpy as np

FEATURE_NAMES = [
    'Pregnancies', 'Glucose', 'BloodPressure', 
    'SkinThickness', 'Insulin', 'BMI', 
    'DiabetesPedigreeFunction', 'Age'
]

DEFAULT_VALUES = {
    'Pregnancies': 1.0,
    'Glucose': 120.0,
    'BloodPressure': 70.0,
    'SkinThickness': 20.0,
    'Insulin': 80.0,
    'BMI': 28.0,
    'DiabetesPedigreeFunction': 0.35,
    'Age': 33.0
}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python predict.py '<sample_json_string>'",
            "status": "error"
        }))
        sys.exit(1)

    raw_input = sys.argv[1]
    
    try:
        data_dict = json.loads(raw_input)
    except Exception as e:
        print(json.dumps({
            "error": f"Invalid JSON string: {e}",
            "status": "error"
        }))
        sys.exit(1)

    # Build input feature vector
    input_row = {}
    for feature in FEATURE_NAMES:
        val = data_dict.get(feature, DEFAULT_VALUES[feature])
        # Handle physiologically invalid zeros for Glucose or BMI
        if feature in ['Glucose', 'BMI'] and val == 0:
            val = DEFAULT_VALUES[feature]
        input_row[feature] = float(val)

    X_input = pd.DataFrame([input_row], columns=FEATURE_NAMES)

    try:
        model = joblib.load('/workspace/final_model.pkl')
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load model from /workspace/final_model.pkl: {e}",
            "status": "error"
        }))
        sys.exit(1)

    try:
        prediction = int(model.predict(X_input)[0])
        probabilities = model.predict_proba(X_input)[0]
        confidence = float(probabilities[prediction])
        
        result = {
            "prediction": prediction,
            "prediction_label": "Positive (Diabetes)" if prediction == 1 else "Negative (No Diabetes)",
            "probability": round(confidence, 4),
            "status": "success"
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({
            "error": f"Inference execution failed: {e}",
            "status": "error"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
