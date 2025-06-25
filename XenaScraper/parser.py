import os
from tkinter import messagebox

from pymongo import MongoClient

TARGET_GENES = [
    'C6orf150', 'CCL5', 'CXCL10', 'TMEM173', 'CXCL9', 'CXCL11',
    'NFKB1', 'IKBKE', 'IRF3', 'TREX1', 'ATM', 'IL6', 'IL8'
]

def parse_tsv_file(file_path):
    cancer_cohort = os.path.basename(file_path).split('HiSeqV2_PANCAN.tsv')[0]
    documents = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # header: first line, first col empty or "id", then patient IDs
    header = lines[0].strip().split('\t')
    patient_ids = header[1:]  # skip first col

    # collect gene expressions per patient
    gene_data = {pid: {} for pid in patient_ids}

    for line in lines[1:]:
        parts = line.strip().split('\t')
        gene = parts[0]
        if gene not in TARGET_GENES:
            continue
        expr_values = parts[1:]
        for pid, val in zip(patient_ids, expr_values):
            try:
                gene_data[pid][gene] = float(val)
            except ValueError:
                gene_data[pid][gene] = None  # or 0 or skip

    # create documents
    for pid in patient_ids:
        doc = {
            'patient_id': pid,
            'cancer_cohort': cancer_cohort,
            'gene_expression': gene_data[pid]
        }
        documents.append(doc)
    return documents

def import_to_mongodb():
    try:
        uri = "mongodb+srv://lauraisel:hospitalBorna@cluster0.vpd1jbp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(uri)
        db = client['cancers']
        collection = db['hospitals']

        folder = "tsv_files"
        all_docs = []

        for file in os.listdir(folder):
            if file.endswith(".tsv"):
                full_path = os.path.join(folder, file)
                docs = parse_tsv_file(full_path)
                all_docs.extend(docs)

        if all_docs:
            collection.insert_many(all_docs)
            messagebox.showinfo("Success", f"Imported {len(all_docs)} documents to MongoDB.")
        else:
            messagebox.showwarning("No data", "No TSV files found or no data to import.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import data:\n{e}")