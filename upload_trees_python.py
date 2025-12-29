#!/usr/bin/env python3
"""
Upload trees data to Google Cloud Storage using Python
"""
from google.cloud import storage
import os

PROJECT_ID = "gen-lang-client-0096113115"
BUCKET_NAME = f"{PROJECT_ID}-coolride-data"
FILE_PATH = "data/trees_downloaded.csv"

print(f"Uploading {FILE_PATH} to GCS bucket {BUCKET_NAME}...")

# Initialize client
client = storage.Client(project=PROJECT_ID)

# Create bucket if it doesn't exist
try:
    bucket = client.create_bucket(BUCKET_NAME, location="asia-southeast1")
    print(f"✅ Created bucket {BUCKET_NAME}")
except Exception as e:
    bucket = client.bucket(BUCKET_NAME)
    print(f"Bucket {BUCKET_NAME} already exists")

# Make bucket publicly readable
bucket.make_public(future=True)
print("✅ Bucket is publicly readable")

# Upload file
blob = bucket.blob("trees_downloaded.csv")
blob.upload_from_filename(FILE_PATH)
blob.make_public()

print(f"✅ Uploaded {os.path.getsize(FILE_PATH) / (1024*1024):.1f} MB")
print(f"✅ File available at: https://storage.googleapis.com/{BUCKET_NAME}/trees_downloaded.csv")
