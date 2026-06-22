# Owner TB Species Dataset Schema

This file documents the curated owner dataset used to extend the project from:

`TB detection -> TB type -> species estimate -> resistance review -> treatment plan`

into a species-labeled decision workflow aligned with WHO-style TB management.

## File

- `backend/data/raw/owner_tb_species_dataset.csv`

## Purpose

- Store curated patient-level examples for all supported MTBC species.
- Provide starter data for future supervised training and evaluation.
- Preserve richer metadata than the current public datasets.

## Core Columns

- `patient_id`: Unique record id for the curated case.
- `age`: Patient age in years.
- `gender`: `Male`, `Female`, or `Other`.
- `city`: Patient city or reporting location.
- `region`: Epidemiologic region or country context.
- `symptoms`: Free-text symptom summary.
- `exposure_history`: Exposure clues such as cattle, goats, rodents, marine mammals, unpasteurized milk, or travel.
- `sputum_smear_test`: `Positive`, `Negative`, or `Unknown`.
- `genexpert_test`: `Positive`, `Negative`, `Rifampicin-resistant`, or `Unknown`.
- `chest_xray`: `Abnormal`, `Normal`, or `Unknown`.
- `tb_culture`: `Positive`, `Negative`, or `Unknown`.
- `tst`: `Positive`, `Negative`, or `Unknown`.
- `igra`: `Positive`, `Negative`, or `Unknown`.
- `drug_resistance`: High-level resistance summary such as `No`, `Yes`, `Rifampicin-resistant`, `Isoniazid and Rifampicin`, or `Extensively drug-resistant`.
- `antibiogram_result`: Short DST / susceptibility interpretation.
- `resistant_to`: Comma-separated resistant medicines.
- `susceptible_to`: Comma-separated susceptible medicines.
- `bacteria_species`: Curated MTBC species label.
- `infection_type`: Main clinical infection pattern.
- `treatment_regimen`: Preferred regimen label for the case.
- `treatment_duration`: Total treatment duration.
- `administration_notes`: How treatment is taken, including daily dosing, DOTS, monitoring, and specialist review.
- `tb_status_label`: `Yes` or `No`.
- `source_note`: Notes on why the example exists or how it should be used.

## Supported Species

- `Mycobacterium tuberculosis`
- `Mycobacterium bovis`
- `Mycobacterium africanum`
- `Mycobacterium canettii`
- `Mycobacterium microti`
- `Mycobacterium caprae`
- `Mycobacterium pinnipedii`
- `Mycobacterium orygis`

## Scientific Use

- Species labels in this starter dataset are curated and project-oriented.
- Treatment choice must still be interpreted through:
  - infection site
  - severity
  - DST / antibiogram
  - patient comorbidities
  - international TB guidance
- The dataset is suitable as a starter curated dataset, not as a replacement for validated hospital-scale surveillance data.
