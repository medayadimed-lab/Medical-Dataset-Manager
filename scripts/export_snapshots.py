import shutil
from pathlib import Path
from datetime import datetime

DATA_FOLDER = "data/augmented"
SNAPSHOT_FOLDER = "data/snapshots"

def export_snapshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_path = Path(SNAPSHOT_FOLDER) / f"snapshot_{timestamp}"
    shutil.copytree(DATA_FOLDER, snapshot_path)
    print(f"Snapshot created: {snapshot_path}")
