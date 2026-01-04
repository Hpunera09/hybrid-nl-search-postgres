import psycopg2
import streamlit as st
import google.generativeai as genai
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch

# Gemini config 
GEMINI_API_KEY = "AIzaSyBYd-Kuzdd2RjcShBG8fuZS8I2RAbwELNM"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3-flash-preview")
print(torch.__version__)


embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

#  database schema 
SCHEMA = """
Tables:
employees(id, name, department_id, email, salary)
departments(id, name)
orders(id, customer_name, employee_id, order_total, order_date)
products(id, name, price, embedding)

Relationships:
employees.department_id -> departments.id
orders.employee_id -> employees.id
"""

#  database connection 
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="nl_search",
        user="postgres",
        password="postgres"
    )

# NL → SQL
def nl_to_sql_gemini(question):
    prompt = f"""
You are an expert PostgreSQL SQL generator.

Rules:
- Use ONLY the schema below
- Generate ONLY a SELECT query
- No explanations
- No markdown
- No comments

Schema:
{SCHEMA}

Question:
{question}
"""
    response = model.generate_content(prompt)

    if not response.text:
        raise ValueError("Empty response from Gemini")

    sql = response.text.strip()
    if "select" in sql.lower():
        sql = sql[sql.lower().find("select"):].strip()
    return sql

#  SQL safety check 
def is_safe_sql(sql):
    return sql.lower().strip().startswith("select")

#  execute SQL 
def run_sql(sql):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return rows, cols

#  get embedding
def get_embedding(text):
    # Force CPU for encoding to avoid meta tensor issues
    emb = embedding_model.encode(text, device="cpu")
    return emb.tolist()

#  hybrid vector search 
def hybrid_vector_search(query, price_limit=None, top_k=10):
    conn = get_connection()
    cur = conn.cursor()

    query_emb = get_embedding(query)
    query_emb_str = "[" + ",".join(map(str, query_emb)) + "]"

    sql = f"""
    SELECT id, name, price
    FROM products
    {"WHERE price <= %s" if price_limit else ""}
    ORDER BY embedding <-> %s::vector
    LIMIT %s
    """
    params = [price_limit] if price_limit else []
    params.extend([query_emb_str, top_k])

    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return rows, cols

#  Streamlit UI 
st.set_page_config(page_title="Hybrid NL Search", layout="wide")
st.title("Natural Language Database Search")

query = st.text_input("Ask a question about the database")
use_vector = st.checkbox("Use semantic (vector) search instead of Gemini NL → SQL")
price_filter = st.number_input("Max Price (optional)", min_value=0, step=1000)

if st.button("Search"):
    if not query.strip():
        st.warning("Please type a question first")
    else:
        try:
            if use_vector:
                # vector semantic search
                price_limit = price_filter if price_filter > 0 else None
                rows, cols = hybrid_vector_search(query, price_limit=price_limit)
                st.subheader("Results (Semantic Search)")
            else:
                # Gemini NL → SQL
                sql = nl_to_sql_gemini(query)
                st.subheader("Generated SQL")
                st.code(sql, language="sql")

                if not is_safe_sql(sql):
                    st.error("Only SELECT queries are allowed")
                    st.stop()

                rows, cols = run_sql(sql)
                st.subheader("Results (NL → SQL)")

            if rows:
                df = pd.DataFrame(rows, columns=cols)
                st.dataframe(df)
            else:
                st.info("No matching results found")

        except Exception as e:
            st.error("Query failed")
            st.exception(e)
