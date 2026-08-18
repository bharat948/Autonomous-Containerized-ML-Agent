import joblib
import pandas as pd
import sys
import json

# Load the model
model = joblib.load('final_model.pkl')

# Input validation function
def validate_input(data):
    required_fields = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    for field in required_fields:
        if field not in data:
            raise ValueError(f'Missing field: {field}')

# Main prediction function
if __name__ == '__main__':
    # Input data from command line argument
    input_data = json.loads(sys.argv[1])
    validate_input(input_data)

    # Prepare input for prediction
    input_df = pd.DataFrame([input_data])
    # Make prediction
    prediction = model.predict(input_df)
    prediction_proba = model.predict_proba(input_df)

    # Output prediction
    result = {
        'prediction': int(prediction[0]),
        'probability': prediction_proba[0].tolist()
    }
    print(json.dumps(result))