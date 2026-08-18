# Data Profiling Report

## Core shape of the dataset:
- Rows: 891, Columns: 10

## Target column distribution:
- Survived: 
  - 0: 549 instances
  - 1: 342 instances

## Columns with missing/null values:
- None. All missing values have been handled.

## Proposed clean actions:
- None. The dataset is now clean.

## Additional insights:
- Numerical columns:
  - Age: Mean: 29.36, Std: 13.02
  - Fare: Mean: 32.20, Std: 49.69
- Categorical columns:
  - pclass, sex, embarked need encoding for model training.