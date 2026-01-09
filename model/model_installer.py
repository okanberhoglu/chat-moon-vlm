from huggingface_hub import snapshot_download
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from config import MODEL_ID, MODEL_REVISION

print(f"Downloading {MODEL_ID}...")

snapshot_download(
    MODEL_ID, 
    revision=MODEL_REVISION,
    max_workers=4
)

print("Download complete.")