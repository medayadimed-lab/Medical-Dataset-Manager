import hashlib

def hash_file(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def save_metadata(db, metadata):
    db.images.insert_one(metadata)
