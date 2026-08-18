# Data Profiling Report

## Core shape of the dataset.
The dataset contains 768 entries and 9 columns.

## Target column distribution.
- Class 0: 500 occurrences
- Class 1: 268 occurrences

## Columns with missing/null values.
- No missing values found in any column.

## Proposed clean actions:
- Change any zero values in 'Glucose' and 'BMI' to NaN for imputation (as those are not realistic physiological values).

## Feature Scores
| Feature                        | Score               |
|--------------------------------|---------------------|
| Glucose                        | 245.86              |
| BMI                            | 82.56               |
| Age                            | 46.14               |
| Pregnancies                   | 39.67               |
| DiabetesPedigreeFunction      | 23.87               |
| Insulin                       | 13.28               |
| SkinThickness                 | 4.30                |
| BloodPressure                 | 3.26                |