from sentence_transformers import SentenceTransformer
import psycopg2

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="nl_search",
    user="postgres",
    password="postgres",
    host="127.0.0.1",
    port="5432"
)
print("connected")
cur = conn.cursor()

#  Embed product names
cur.execute("SELECT id, name FROM products;")
products = cur.fetchall()

for pid, name in products:
    emb = model.encode(name).tolist()
    cur.execute(
        "UPDATE products SET embedding = %s WHERE id = %s",
        (emb, pid)
    )

print("product embeddings stored")

#  Embed customer names 
cur.execute("SELECT id, customer_name FROM orders;")
orders = cur.fetchall()

for oid, cname in orders:
    emb = model.encode(cname).tolist()
    cur.execute(
        "UPDATE orders SET customer_embedding = %s WHERE id = %s",
        (emb, oid)
    )

print("customer embeddings stored")

# Commit and close
conn.commit()
cur.close()
conn.close()

print("all embeddings stored successfully")
