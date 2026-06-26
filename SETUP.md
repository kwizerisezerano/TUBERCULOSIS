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

## 3. Set Up Datasets (IMPORTANT!)
Datasets are not stored in Git due to GitHub's size limits.

### Option A: Use the setup script (recommended)
1. First, edit `setup_datasets.py` and replace the example URL with your actual dataset download link.
2. Run the script:
   ```bash
   python setup_datasets.py
   ```

### Option B: Manual setup
1. Copy your `Tuberculosis_Dataset.csv` into:
   ```
   backend/data/raw/Tuberculosis_Dataset.csv
   ```
2. Copy any other required datasets into the same folder.

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
- **Why datasets aren't in Git:** GitHub doesn't allow files > 100 MB.
- **Storage options:**
  - Use Git LFS (Large File Storage) if you want Git tracking
  - Use cloud storage (Google Drive, Dropbox, etc.)
  - Use a data repository like Zenodo or Figshare
