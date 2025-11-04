import os
from pathlib import Path
import pydicom
from utils.anonymize import anonymize_dicom
from utils.mongo_client import get_db
from utils.helpers import hash_file, save_metadata

RAW_FOLDER = "data/raw"
INGEST_FOLDER = "data/ingest"

db = get_db()

def ingest_dicom_file(dicom_path: Path, output_folder: Path):
    try:
        ds = pydicom.dcmread(dicom_path)
        ds_anonymized = anonymize_dicom(ds)
        output_path = output_folder / dicom_path.name
        ds_anonymized.save_as(output_path)

        metadata = {
            "filename": dicom_path.name,
            "hash": hash_file(output_path),
            "path": str(output_path),
            "status": "anonymized"
        }
        save_metadata(db, metadata)
        print(f"✅ Ingested: {dicom_path.name}")
    except Exception as e:
        print(f"❌ Failed to ingest {dicom_path.name}: {e}")

def ingest_folder(folder_path=RAW_FOLDER, output_subfolder="batch"):
    folder_path = Path(folder_path)
    output_folder = Path(INGEST_FOLDER) / output_subfolder
    output_folder.mkdir(parents=True, exist_ok=True)

    dicom_files = list(folder_path.glob("*.dcm"))
    if not dicom_files:
        print(f"No DICOM files found in {folder_path}")
        return

    for dicom_file in dicom_files:
        ingest_dicom_file(dicom_file, output_folder)

    print(f"\n📦 Ingestion complete. Files saved in {output_folder}")

def ingest_single_file(file_path: str, output_subfolder="single"):
    dicom_path = Path(file_path)
    if not dicom_path.exists() or dicom_path.suffix != ".dcm":
        print(f"Invalid DICOM file: {file_path}")
        return

    output_folder = Path(INGEST_FOLDER) / output_subfolder
    output_folder.mkdir(parents=True, exist_ok=True)

    ingest_dicom_file(dicom_path, output_folder)
    print(f"\n📦 Single file ingestion complete. Saved in {output_folder}")
