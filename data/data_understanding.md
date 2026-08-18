# Data Understanding Report for Customer Churn Dataset

## Shape and Data Types
- Shape: (7043, 21)
- Features: customerID, gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges, Churn
- Data Types:
  - int64: SeniorCitizen, tenure
  - float64: MonthlyCharges
  - str: gender, Partner, Dependents, PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaperlessBilling, PaymentMethod, Churn, TotalCharges

## Missing Values
- No missing values detected:
  - gender: 0
  - SeniorCitizen: 0
  - Partner: 0
  - Dependents: 0
  - tenure: 0
  - PhoneService: 0
  - MultipleLines: 0
  - InternetService: 0
  - OnlineSecurity: 0
  - OnlineBackup: 0
  - DeviceProtection: 0
  - TechSupport: 0
  - StreamingTV: 0
  - StreamingMovies: 0
  - Contract: 0
  - PaperlessBilling: 0
  - PaymentMethod: 0
  - MonthlyCharges: 0
  - TotalCharges: 0
  - Churn: 0

## Target Distribution
- Churn distribution:
  - No: 5174 (73.4%)
  - Yes: 1869 (26.6%)

## Unique Values in Categorical Features
- customerID is an identifier and has been removed.

## Distribution of 'TotalCharges'
- TotalCharges was converted from empty spaces to NaN and imputed with the median value.

## Preprocessing Decisions
- Remove 'customerID'.
- Convert 'TotalCharges' empty spaces to NaN and impute using the median.