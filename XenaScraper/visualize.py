from pymongo import MongoClient
import matplotlib.pyplot as plt

MONGO_URI = "mongodb+srv://lauraisel:hospitalBorna@cluster0.vpd1jbp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'cancers'
COLLECTION_NAME = 'hospitals'

TARGET_GENES = [
    'C6orf150', 'CCL5', 'CXCL10', 'TMEM173', 'CXCL9', 'CXCL11',
    'NFKB1', 'IKBKE', 'IRF3', 'TREX1', 'ATM', 'IL6', 'IL8'
]

def get_gene_expression_data(patient_ids):
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    docs = list(collection.find({"patient_id": {"$in": patient_ids}}))
    return docs


def plot_gene_expression(docs, canvas, ax):
    
    if not docs:
        raise ValueError("No documents to plot.")

    ax.clear()
    width = 0.8 / len(docs)  
    x = range(len(TARGET_GENES))

    for i, doc in enumerate(docs):
        gene_expr = doc.get('gene_expression', {})
        y = [gene_expr.get(gene, 0) for gene in TARGET_GENES]
        positions = [pos + i*width for pos in x]
        ax.bar(positions, y, width=width, label=doc['patient_id'])

    ax.set_xticks([pos + width*(len(docs)/2) for pos in x])
    ax.set_xticklabels(TARGET_GENES, rotation=45, ha='right')
    ax.set_ylabel('Expression Level')
    ax.set_title('Gene Expression of Selected Patients')
    ax.legend()
    plt.tight_layout()
    canvas.draw()
