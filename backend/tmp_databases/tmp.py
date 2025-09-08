# tmp.py -> script to get all the collections names
import chromadb

client = chromadb.PersistentClient(path="./db")
print(client.list_collections())
