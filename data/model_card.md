# Model Card for Customer Churn Prediction Model

## Model Details
- **Model Type:** Random Forest Classifier
- **Version:** 1.0

## Input Schema
- **Features:**
  - Categorical: Includes gender, Partner, Dependents, PhoneService, etc.
  - Numerical: Includes SeniorCitizen, tenure, MonthlyCharges, TotalCharges.

## Training Data
- **Size:** 7043 records
- **Target Distribution:** 73.4% No, 26.6% Yes

## Evaluation Metrics
- **F1 Score (Holdout Set):** 0.59 (for Yes)
- **Overall Accuracy:** 80%
- **ROC AUC (Cross-Validation):** 0.8216

## Limitations
- The model has shown bias towards the majority class (No). Further improvement may be needed in predicting the minority class (Yes).

## Training Data Assumptions
- The training data is assumed to be representative of the problem domain, capturing the relevant features for predicting customer churn.