import os
import sys
import json
import joblib
import pandas as pd

# Load the model relative to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'final_model.pkl')
model = joblib.load(model_path)

def predict(input_json):
    # Required features expected by the pipeline preprocessor
    required_fields = [
        'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure', 
        'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity', 
        'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 
        'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod', 
        'MonthlyCharges', 'TotalCharges'
    ]
    
    # Check fields
    for field in required_fields:
        if field not in input_json:
            raise ValueError(f'Missing required field: {field}')
            
    # Coerce TotalCharges to float if it is a string containing numbers or spaces
    total_charges = input_json.get('TotalCharges')
    if isinstance(total_charges, str):
        cleaned_str = total_charges.strip()
        if not cleaned_str:
            input_json['TotalCharges'] = float('nan')
        else:
            try:
                input_json['TotalCharges'] = float(cleaned_str)
            except ValueError:
                input_json['TotalCharges'] = float('nan')

    # Convert to DataFrame with training column order
    input_df = pd.DataFrame([input_json])[required_fields]
    
    # Run prediction
    pred = model.predict(input_df)
    proba = model.predict_proba(input_df)[:, 1]
    
    # Map back target predictions
    pred_label = 'Yes' if pred[0] == 1 else 'No'
    
    return json.dumps({
        'prediction': pred_label,
        'probability': proba.tolist()[0]
    })

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Missing JSON input argument'}))
        sys.exit(1)
    try:
        input_json = json.loads(sys.argv[1])
        # If input is a list, extract the first element
        if isinstance(input_json, list):
            input_json = input_json[0]
        print(predict(input_json))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)