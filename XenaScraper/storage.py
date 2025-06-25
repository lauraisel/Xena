import os

from minio import Minio, S3Error
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE, MINIO_BUCKET

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def ensure_bucket():
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)

def upload_to_minio(bucket_name, file_path, object_name=None):
    try:
        # Ensure the bucket exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Use filename if object name not provided
        if object_name is None:
            object_name = os.path.basename(file_path)

        # Upload the file
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type="text/tab-separated-values"
        )

        print(f"Uploaded {file_path} to bucket '{bucket_name}' as '{object_name}'")
        return True

    except S3Error as e:
        print(f"S3Error: {e}")
        return False

def upload_all_tsv_from_folder(bucket_name, folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsv"):
            file_path = os.path.join(folder_path, filename)
            success = upload_to_minio(bucket_name, file_path)
            if not success:
                print(f"Failed to upload {filename}")