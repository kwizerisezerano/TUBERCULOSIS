# [OPEN] bootstrap-train-failure

## Bug Summary
- `python bootstrap.py --no-reset --runserver` fails during model training.
- Error: `ValueError: Number of classes, 1, does not match size of target_names, 2`.
- User also asked for a careful review of backend/frontend integration.

## Hypotheses
1. The drug-resistance training subset currently contains only one class, but the report code assumes all label-encoder classes are present in the test split.
2. The label encoder is fitted on a broader dataset than the actual `y_test`/`y_pred`, causing `classification_report()` to reject mismatched `target_names`.
3. The importer is normalizing drug resistance into a single value for almost all records, collapsing the training target.
4. Bootstrap should tolerate single-class training data and skip/report that model instead of crashing the whole backend startup.
5. Backend/frontend integration still has remaining mismatches after auth/pagination fixes, especially around diagnoses and training readiness.

## Evidence Plan
- Inspect training pipeline and dataset preparation for the drug-resistance classifier.
- Add runtime instrumentation around class distributions and training inputs first.
- Reproduce the bootstrap training failure and capture debug logs.
- Fix only after evidence confirms whether this is a data-distribution or reporting-path problem.

## Status
- Session created.
- Runtime evidence collected from the training pipeline.
- Minimal training-report fix applied.
- Direct training function no longer crashes on the imbalanced drug-resistance dataset.

## Evidence
- `drug_resistance` training rows: `20005`
- Label distribution: `No=20003`, `Yes=2`
- Encoder classes: `["No", "Yes"]`
- Split state for drug resistance:
  - `y_train_unique = [0, 1]`
  - `y_test_unique = [0]`
- Prediction state for drug resistance:
  - `y_pred_unique = [0]`
  - `y_test_unique = [0]`
- Root failure before fix:
  - `classification_report()` received two `target_names` but only one class existed in the test/prediction arrays.

## Root Cause
- The backend did use real database data.
- The training crash was not caused by frontend/backend integration.
- The crash happened because the drug-resistance dataset is extremely imbalanced, and the reporting code assumed both classes would appear in the evaluation split.

## Outcome
- Training report generation now passes explicit labels and `zero_division=0`.
- Bootstrap/training can proceed without crashing even when one class is absent from `y_test`.
- The real data issue that remains is class imbalance, not integration failure.
