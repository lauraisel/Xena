from pymongo import MongoClient

uri = "mongodb+srv://lauraisel:<hospitalBorna>@cluster0.vpd1jbp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['cancers']
collection = db['hospitals']
