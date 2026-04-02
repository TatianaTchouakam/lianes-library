# 📚 Liane's Library

🚀 **End-to-End Data Engineering Project**

Liane's Library is a data-driven library management application built with Python, SQL, and Streamlit.  
It demonstrates how to design a complete data system from database modeling to an interactive dashboard.

---

## 🚀 Project Overview

This application allows users to:

- Manage a personal or shared library  
- Track book loans and returns  
- Monitor user activity  
- Analyze borrowing trends  
- Interact with a clean and intuitive dashboard  

---

## 🧰 Tech Stack

- Python (Pandas, SQLAlchemy)  
- SQL (MySQL) – database design & queries  
- Streamlit – interactive dashboard  
- Git & GitHub – version control  

---

## 🏗️ Database Structure

The system is built on 4 main tables:

- authors → stores author information  
- books → contains book details  
- friends → library users  
- loans → tracks borrowing activity  

---

## 📊 Features

### 🔍 Search System
- Global search across books, authors, and friends  
- Fast filtering with dynamic queries  

### 📈 Dashboard

Key metrics:
- Current Loans  
- Overdue Loans  
- Current Borrowers  
- Return Rate  

Analytics:
- Loan activity by genre  
- Top borrowed books  
- Most active users  

---

### 📘 Books Management

- Add books  
- Remove books  
- Filter by genre  
- View available books  
- Prevent duplicate entries  

---

### 👥 Friends Management

- Add friends  
- Track borrowing activity  
- Monitor current loans per user  
- Limit number of loans per user  

---

### 🔄 Loans Management

- Create loans  
- Return books  
- Prevent borrowing unavailable books  
- Prevent users exceeding max_loans  

---

### ✍️ Authors Analysis

- Number of books per author  
- Most borrowed authors  

---

## ⚡ Example SQL Queries

-- Current loans  
SELECT COUNT(*)  
FROM loans  
WHERE return_date IS NULL;

-- Overdue loans  
SELECT COUNT(*)  
FROM loans  
WHERE return_date IS NULL  
  AND due_date < CURDATE();

-- Loans by genre  
SELECT b.genre, COUNT(l.loan_id)  
FROM books b  
JOIN loans l ON b.isbn = l.isbn  
GROUP BY b.genre;

---

## 🖥️ How to Run the Project

1. Clone the repository  
git clone https://github.com/TatianaTchouakam/lianes-library.git  
cd lianes-library  

2. Install dependencies  
pip install -r requirements.txt  

3. Create a `.env` file (not included for security)  

DB_USER=root  
DB_PASSWORD=your_password  
DB_HOST=localhost  
DB_NAME=lianes_library  

4. Run the app  
streamlit run src/app.py  

---

## 💡 What This Project Demonstrates

- Relational database design (MySQL)  
- Advanced SQL querying  
- Backend integration with Python  
- Building interactive data applications  
- End-to-end data workflow  

---

## 📌 Highlights

- Full-stack data project (SQL → Python → UI)  
- Real-time data updates  
- Clean and user-friendly interface  
- Strong focus on data-driven decision-making  

---

## 🎯 Future Improvements

- Authentication system  
- Recommendation system (Machine Learning)  
- Cloud deployment (AWS)  
- API integration  

---

## 👩🏽‍💻 Author

Tatiana Tchouakam Chouacheu  
Data & Cloud Engineer in Training  

GitHub: https://github.com/TatianaTchouakam  

---

## ⭐ Support

If you like this project, give it a star ⭐ and feel free to contribute!
