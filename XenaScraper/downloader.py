import os
import gzip
import shutil
import requests
from urllib.parse import unquote, urlparse

output_folder = "tsv_files"
os.makedirs(output_folder, exist_ok=True)

def download_and_extract_all(urls):
    tsv_files = []

    for url in urls:
        tsv_path = download_and_extract_gz(url)
        if tsv_path:
            tsv_files.append(tsv_path)

    return tsv_files

def download_and_extract_gz(url):
    print(f"Downloading: {url}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        path = unquote(urlparse(url).path)
        parts = path.strip("/").split("/")  # e.g., ['download', 'TCGA.LAML.sampleMap', 'HiSeqV2_PANCAN.gz']

        if len(parts) < 2:
            raise ValueError(f"Unexpected URL format: {url}")

        cohort_raw = parts[-2]  # TCGA.LAML.sampleMap
        cohort_clean = cohort_raw.replace(".", "").replace("sampleMap", "")  # TCGALAML

        data_file = parts[-1].replace(".gz", "")  # HiSeqV2_PANCAN

        final_filename = f"{cohort_clean}{data_file}.tsv"
        gz_path = os.path.join(output_folder, parts[-1])  # Keep original .gz name
        tsv_path = os.path.join(output_folder, final_filename)

        # Save .gz file
        with open(gz_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract and save as .tsv
        with gzip.open(gz_path, "rb") as f_in, open(tsv_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        os.remove(gz_path)  # Optionally delete .gz
        return tsv_path

    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None