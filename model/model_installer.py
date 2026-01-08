from huggingface_hub import snapshot_download
from config import MODEL_ID, MODEL_REVISION

print(f"Downloading {MODEL_ID}...")

snapshot_download(
    MODEL_ID, 
    revision=MODEL_REVISION,
    max_workers=4
)

print("Download complete.")