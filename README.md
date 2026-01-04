# Natural Language Search Interface using PostgreSQL & Vector Embeddings

## 📌 Project Overview
This project implements a **Natural Language Search Interface** over a PostgreSQL database.  
Users can query the database using plain English, and the system retrieves relevant results using **semantic vector search** instead of traditional keyword-based SQL queries.

The project demonstrates how **LLMs, embeddings, and pgvector** can be combined to build intelligent database search systems.

---

## 🛠️ Tech Stack
- **Python**
- **PostgreSQL**
- **pgvector**
- **Sentence Transformers**
- **Streamlit** (for UI)
- **Docker** (for database container)

---

## 🗄️ Database Schema
The PostgreSQL database (`nl_search`) contains structured tables such as:

- `employees`
- `departments`
- `products`
- `orders`

Vector embeddings are stored using the `pgvector` extension to support semantic similarity search.

Schema definition is provided in:



---

## 🧠 How It Works
1. User enters a **natural language query** (e.g., “cheap laptops under 30000”)
2. The query is converted into a **vector embedding**
3. PostgreSQL performs **similarity search** using pgvector
4. The most relevant rows are returned
5. Results are displayed via Streamlit

This approach allows flexible querying without writing SQL manually.

---

## 🚀 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone <repository-url>
cd <project-folder>

2️⃣ Start PostgreSQL with pgvector (Docker)

docker run -d \
  --name pgvector-db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

3️⃣ Restore Database Schema
psql -U postgres -d nl_search -f schema.sql

4️⃣ Insert Sample Data
psql -U postgres -d nl_search -f seed.sql

▶️ Run the Application
streamlit run app.py
Open your browser and navigate to:
http://localhost:8501


```
# project results(sql and semantic search)
<img width="1839" height="821" alt="Image" src="https://github.com/user-attachments/assets/5f6df9af-16fd-4b42-a3a7-b1873a757782" />



<img width="1753" height="650" alt="g" src="https://github.com/user-attachments/assets/54b137bf-1e12-47d0-8516-fa66aaacf350" />





