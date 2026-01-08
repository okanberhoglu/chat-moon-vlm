from huggingface_hub import snapshot_download

model_id = "vikhyatk/moondream2"
print(f"Downloading {model_id}...")

snapshot_download(
    model_id, 
    revision="2025-06-21",
    max_workers=4
)

print("Download complete.")