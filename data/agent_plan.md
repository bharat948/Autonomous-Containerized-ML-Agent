# Agent Plan for Customer Churn Prediction Model

## Objective
Build a binary classification model to predict customer churn based on customer data.

## Steps
1. **Data profiling**: Inspect the dataset for shape, dtypes, missing values, and target distribution.
2. **Preprocessing**: Use a scikit-learn Pipeline and ColumnTransformer for leakage-safe preprocessing.
3. **Data Split**: Split the data into training and holdout sets.
4. **Model trials**: Evaluate a baseline and three model families (Linear, Bagged trees, Boosting).
5. **Hyperparameter tuning**: Tune the best model family using RandomizedSearchCV.
6. **Evaluation**: Assess models with CV and store metrics.
7. **Exporting**: Save the final model, validation reports, and inference Python script.
8. **Cleanup**: Remove temporary data and maintain essential files only.

## Acceptance Criteria
- Complete evidence for each step. 
- Metrics surpassing naive baseline.
- Validated and clean exported files.
- Documented decisions and outcomes.