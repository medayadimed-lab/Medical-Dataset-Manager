import pydicom

def anonymize_dicom(ds):
    # Remove PHI fields
    for tag in ['PatientName', 'PatientID', 'PatientBirthDate']:
        if tag in ds:
            ds.data_element(tag).value = "ANONYMIZED"
    return ds
