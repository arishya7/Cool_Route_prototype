#!/bin/bash
# Upload trees data to Google Cloud Storage
# Run this once: chmod +x upload_trees_to_gcs.sh && ./upload_trees_to_gcs.sh

PROJECT_ID="gen-lang-client-0096113115"
BUCKET_NAME="${PROJECT_ID}-coolride-data"

echo "Creating GCS bucket (if it doesn't exist)..."
gsutil mb -p ${PROJECT_ID} -l asia-southeast1 gs://${BUCKET_NAME}/ 2>/dev/null || echo "Bucket already exists"

echo "Making bucket publicly readable..."
gsutil iam ch allUsers:objectViewer gs://${BUCKET_NAME}

echo "Uploading trees data (45MB - this may take a minute)..."
gsutil cp data/trees_downloaded.csv gs://${BUCKET_NAME}/trees_downloaded.csv

echo "Done! File available at:"
echo "https://storage.googleapis.com/${BUCKET_NAME}/trees_downloaded.csv"
