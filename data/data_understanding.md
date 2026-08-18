# Data Understanding for Diabetes Dataset

## Dataset Overview
- **Shape**: (768, 9)
- **Feature Names**: ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']
- **Dtypes**:
  - Numeric: float64, int64

## Missing Values
- **Count of Missing Values**:
  - Glucose: 5
  - BloodPressure: 35
  - SkinThickness: 227
  - Insulin: 374
  - BMI: 11

## Unique Values in Target 'Outcome'
- **Unique Values**: [0, 1] (2 classes)
- **Distribution**:
  - Class 0: 500
  - Class 1: 268

## Distribution Check
- The target shows some imbalance, but there are 2 classes available. No further action is needed on the target.

## Feature Analysis
- **Numeric Feature Basic Stats**:
  - Mean, Median, Std, Min, Max for all numeric features.
- **Skewness**:
  - Examine each feature for skewness and potential transforms if needed.

## Categorical Features
- **Cardinality**: There are no categorical features present in the dataset.

## Correlation Analysis
- **Correlation Matrix**: Check for highly correlated features.
- **Documentation of Features with High Correlation** with a documented threshold.

## Feature-to-Target Relationship
- **Pairs Analysis**: Analyze relationships without leaking target information.