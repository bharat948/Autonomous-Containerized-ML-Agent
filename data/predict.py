import sys
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from joblib import load

# Load the model
model = load('final_model.pkl')

# Function to preprocess input
def preprocess(input_data):
    # Convert input JSON to DataFrame
    df = pd.DataFrame([input_data])
    scaler = StandardScaler()
    df[df.columns] = scaler.fit_transform(df[df.columns])
    return df

if __name__ == '__main__':
    input_json = json.loads(sys.argv[1])
    processed_data = preprocess(input_json)
    prediction = model.predict(processed_data)
    probability = model.predict_proba(processed_data)
    result = {
        'prediction': int(prediction[0]),
        'probability': probability.max()
    }
    print(json.dumps(result))