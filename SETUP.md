# Project Setup Guide

This guide will help you set up the Predictive EHR Analytics Dashboard on a new machine.


## 1. Prerequisites
Make sure you have the following installed:
- Python 3.8+
- Node.js 18+
- MySQL 8+
- Git

## 2. Clone the Repository
```bash
git clone https://github.com/kwizerisezerano/TUBERCULOSIS.git
cd TUBERCULOSIS
```

## 3. Set Up the Large Dataset (IMPORTANT!)
Only the Tuberculosis_Dataset.csv file is too big for GitHub (131MB). All other datasets are included in the repo!

### Option A: Use the setup script (recommended)
First, edit `setup_datasets.py` and replace the example URL with your actual dataset download link.
Then run the script:
```bash
python setup_datasets.py
```

### Option B: Manual setup
Copy your `Tuberculosis_Dataset.csv` file into:
```
backend/data/raw/Tuberculosis_Dataset.csv
```

## 4. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```
Then, run the import script to set up the database:
```bash
python import_data.py
```

## 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 6. Run the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Notes on Datasets
- **Why one dataset is not in Git**: GitHub doesn't allow files > 100 MB, so `Tuberculosis_Dataset.csv` is excluded.
- **All other datasets are included**: All other smaller datasets are in Git!
- **Storage options for large dataset**:
  - Use cloud storage (Google Drive, Dropbox, etc.)
  - Use a data repository like Zenodo or Figshare
  - Use Git LFS (Large File Storage) if needed
