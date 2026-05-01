Build a full-stack web-based application called **“Intelligent MDB Agent”**, an AI-powered Moderated Discussion Board assistant. The system must use **Python (Flask/FastAPI) for backend and SQL (MySQL or SQLite)** for database storage.

---

### 🎯 Core Objective

The system should:

1. Filter non-academic MDB posts.
2. Extract keywords from student queries.
3. Match queries with course handouts.
4. Generate relevant responses.
5. Store all data in a structured SQL database.

---

# ⚙️ Tech Stack

### 🔹 Frontend

* HTML, CSS, JavaScript (or React)

### 🔹 Backend

* Python (Flask or FastAPI)

### 🔹 Database (IMPORTANT)

* Use **SQLite (for simplicity)** OR **MySQL (for advanced version)**
* Use **SQLAlchemy ORM** to interact with database

---

# 🗄️ Database Design (VERY IMPORTANT)

Create the following tables:

### 1. Users Table

* id (Primary Key)
* name
* email
* role (admin / instructor / student)

---

### 2. Handouts Table

* id (Primary Key)
* file_name
* extracted_text (LONG TEXT)
* upload_date

---

### 3. Queries Table

* id (Primary Key)
* user_id (Foreign Key)
* query_text
* is_academic (boolean)
* created_at

---

### 4. Responses Table

* id (Primary Key)
* query_id (Foreign Key)
* keywords (TEXT)
* matched_content (TEXT)
* generated_response (TEXT)
* similarity_score (FLOAT)

---

### 5. FilterLogs Table

* id (Primary Key)
* query_text
* reason (e.g., “non-academic keyword detected”)
* created_at

---

# 🔧 Backend Functional Modules

---

## 1. Handout Upload Module

* Upload PDF
* Extract text using PyPDF2
* Store extracted text in **Handouts table**

---

## 2. Query Processing Module

When user submits query:

1. Save query in **Queries table**
2. Check if query is non-academic

---

## 3. Filtering Module

* Use keyword list:
  ["done", "ok", "yes sir", "present", "whatsapp"]
* If detected:

  * Mark `is_academic = false`
  * Save in **FilterLogs**
  * Return warning message

---

## 4. Keyword Extraction Module

* Use KeyBERT or spaCy
* Store extracted keywords in **Responses table**

---

## 5. Semantic Matching Module

* Use Sentence-Transformers
* Compare query with all handout text
* Return best matching paragraph
* Store similarity score

---

## 6. Response Generation Module

* Generate short answer:
  “According to the handout: …”
* Store in **Responses table**

---

# 🌐 API Endpoints

Create these APIs:

### POST /upload_handout

* Upload PDF
* Save data in database

### POST /analyze_query

* Input: query + user_id
* Process:

  * Filter
  * Extract keywords
  * Match content
  * Generate response
* Save all results in database
* Return response

### GET /history

* Return past queries + responses from database

---

# 🔄 System Workflow

User → Submit Query
↓
Save in SQL Database
↓
Filter (SQL log if rejected)
↓
Keyword Extraction
↓
Semantic Matching (from Handouts table)
↓
Generate Response
↓
Store Result in Responses table
↓
Display Output

---

# 📊 Optional Dashboard (Advanced)

* Show:

  * Total queries
  * Filtered queries
  * Top keywords
* Fetch data from SQL tables

---

# ⚡ Constraints

* Use **open-source NLP models only**
* Ensure fast query response (optimize DB queries)
* Keep modular structure (separate services for NLP and DB)

---

# 🧪 Testing

* Insert sample handouts into database
* Run queries like:
  “Explain primary memory”
* Verify:

  * Query saved in DB
  * Correct filtering
  * Relevant match returned

---

# 🎯 Expected Output

* Fully working system with:
  ✔ SQL database integration
  ✔ Stored queries and responses
  ✔ Intelligent filtering
  ✔ Relevant answer generation

---

# 🚀 Goal

Develop a scalable AI-based academic assistant using **NLP + SQL backend** that improves MDB quality and reduces instructor workload.
