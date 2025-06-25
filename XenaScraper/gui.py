import tkinter as tk
from tkinter import messagebox
import asyncio
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import visualize
from downloader import download_and_extract_all
from scraper import get_dataset_gz_links
from storage import upload_all_tsv_from_folder
from parser import import_to_mongodb  

base_url = "https://xenabrowser.net/datapages/?hub=https://tcga.xenahubs.net:443"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gene Expression Data Tool")
        self.geometry("600x500")  

        self.download_btn = tk.Button(self, text="Download TSV Files", command=self.download_tsv)
        self.download_btn.pack(pady=10)

        self.upload_btn = tk.Button(self, text="Upload TSV to MinIO", command=self.upload_tsv)
        self.upload_btn.pack(pady=10)

        self.mongo_import_btn = tk.Button(self, text="Import TSV to MongoDB", command=self.import_tsv_to_mongo)
        self.mongo_import_btn.pack(pady=10)

        
        tk.Label(self, text="Enter patient IDs (comma-separated):").pack(pady=(20, 0))
        self.patient_id_entry = tk.Entry(self, width=50)
        self.patient_id_entry.pack(pady=5)

        
        self.visualize_btn = tk.Button(self, text="Visualize Gene Expression", command=self.visualize_gene_expression)
        self.visualize_btn.pack(pady=10)

        
        self.fig, self.ax = plt.subplots(figsize=(6,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

    def download_tsv(self):
        try:
            tsv_files = asyncio.run(self.async_download_and_extract())
            messagebox.showinfo("Success", f"Downloaded and extracted {len(tsv_files)} TSV files.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @staticmethod
    async def async_download_and_extract():
        gz_links = await get_dataset_gz_links(base_url)
        tsv_files = download_and_extract_all(gz_links)
        return tsv_files

    @staticmethod
    def upload_tsv():
        try:
            upload_all_tsv_from_folder("laura-isel2", "tsv_files")
            messagebox.showinfo("Success", "Upload to MinIO completed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @staticmethod
    def import_tsv_to_mongo():
        try:
            import_to_mongodb()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data:\n{e}")

    def visualize_gene_expression(self):
        patient_ids_raw = self.patient_id_entry.get().strip()
        if not patient_ids_raw:
            messagebox.showwarning("Input Error", "Please enter at least one patient ID.")
            return

        patient_ids = [pid.strip() for pid in patient_ids_raw.split(",") if pid.strip()]
        if not patient_ids:
            messagebox.showwarning("Input Error", "Please enter valid patient IDs.")
            return

        try:
            docs = visualize.get_gene_expression_data(patient_ids)
            if not docs:
                messagebox.showinfo("No Data", "No data found for the given patient IDs.")
                return

            visualize.plot_gene_expression(docs, self.canvas, self.ax)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize data:\n{e}")
