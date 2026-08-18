# Evaluation Report for Customer Churn Model

## Model Summary
The model built is a Random Forest Classifier, optimized for predicting customer churn. The target variable is "Churn", which indicates whether a customer has left (Yes) or stayed (No).

## Model Performance
- **Hyperparameters:**  
  - n_estimators: 100  
  - min_samples_split: 10  
  - max_depth: 10  

### Metrics on Holdout Set
- **Precision (No):** 0.84  
- **Recall (No):** 0.90  
- **F1-Score (No):** 0.87  
- **Precision (Yes):** 0.66  
- **Recall (Yes):** 0.52  
- **F1-Score (Yes):** 0.59  
- **Overall Accuracy:** 0.80  

The model shows a good balance in predicting the majority class (No), but has room for improvement in predicting the minority class (Yes).

## Conclusion
The model is effective in predicting customer retention with a good F1 score and can be improved further with more parameter tuning or different model families.