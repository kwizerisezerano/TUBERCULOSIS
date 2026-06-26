#!/usr/bin/env python3
"""
Setup script to download required datasets for the project.
Run this script when setting up the project on a new machine.
"""

import os
import urllib.request
import zipfile
from pathlib import Path

# Create directories if they don't exist
BASE_DIR = Path(__file__).parent
DATA_RAW_DIR = BASE_DIR / "backend" / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "backend" / "data" / "processed"

DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------
# Dataset Configuration
# --------------------------
# Add your dataset download links here!
# Since I don't have your actual dataset source, you'll need to fill this in.
# Examples of sources:
# - Google Drive (direct download link)
# - Dropbox
# - Zenodo
# - Figshare
# - Your own cloud storage

DATASETS = [
    {
        "name": "Tuberculosis Dataset",
        "filename": "Tuberculosis_Dataset.csv",
        # Replace this with your actual dataset download URL
        "url": "https://example.com/path/to/Tuberculosis_Dataset.csv",
        "description": "Main tuberculosis dataset for analysis",
    }
    # Add more datasets here if needed
]

def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from a URL to a destination path."""
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Successfully downloaded to {dest_path}")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        print("Please download the file manually and place it in:", dest_path)
        return False

def setup_datasets():
    """Main setup function."""
    print("=" * 60)
    print("Predictive EHR Analytics Dashboard - Dataset Setup")
    print("=" * 60)
    print()

    for dataset in DATASETS:
        dest_path = DATA_RAW_DIR / dataset["filename"]
        
        if dest_path.exists():
            print(f"✓ {dataset['name']} already exists at {dest_path}")
            print()
            continue
        
        print(f"Setting up {dataset['name']}...")
        print(f"  Description: {dataset['description']}")
        
        if dataset["url"]:
            success = download_file(dataset["url"], dest_path)
            if not success:
                print("  Please manually place the file in:", DATA_RAW_DIR)
        else:
            print("  No download URL configured.")
            print("  Please manually place the file in:", DATA_RAW_DIR)
        
        print()

    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. If you had to download datasets manually, please place them in", DATA_RAW_DIR)
    print("2. Run the data preprocessing script (if applicable): cd backend && python import_data.py")
    print()

if __name__ == "__main__":
    setup_datasets()
