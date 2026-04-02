# 📚 Liane's Library

🚀 **End-to-End Data Engineering Project**

Liane's Library is a data-driven library management application built with **Python, SQL, and Streamlit**.  
It showcases how to design a full data system — from database modeling to an interactive dashboard.

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

- **Python** (Pandas, SQLAlchemy)  
- **SQL (MySQL)** – database design & queries  
- **Streamlit** – interactive dashboard  
- **Git & GitHub** – version control  

---

## 🏗️ Database Design

The system is built on a relational database with 4 core tables:

- **authors** → author details  
- **books** → book information (linked to authors)  
- **friends** → users of the library  
- **loans** → borrowing and return tracking  

---

## 📊 Key Features

### 🔍 Search & Filtering
- Global search across books, authors, and friends  
- Dynamic filtering by genre  

---

### 📈 Dashboard

Real-time KPIs:

- 📚 Current Loans  
- ⏰ Overdue Loans  
- 👥 Active Borrowers  
- 📊 Return Rate  

Analytics:
- Loans by genre  
- Most borrowed books  
- Most active users  

---

### 📘 Books Management

- Add new books  
- Remove books  
- Filter by genre  
- View available books  
- Prevent duplicate entries  

---

### 👥 Friends Management

- Add new users  
- Track borrowing activity  
- Limit number of loans per user  

---

### 🔄 Loans System

- Create loans  
- Return books  
- Prevent borrowing unavailable books  
- Prevent users exceeding max_loans  

---

### ✍️ Authors Insights

- Number of books per author  
- Most borrowed authors  

---

## ⚡ Example SQL Queries

```sql
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


💡 What This Project Demonstrates
Relational database design (MySQL)
Advanced SQL querying
Backend integration with Python
Building interactive data applications
End-to-end data workflow

📌 Highlights
Full-stack data project (SQL → Python → UI)
Real-time data updates
Clean and user-friendly interface
Strong focus on data-driven decision-making

🎯 Future Improvements
Authentication system
Recommendation system (Machine Learning)
Cloud deployment (AWS)
API integration


👩🏽‍💻 Author
Tatiana Tchouakam Chouacheu
Data & Cloud Engineer in Training
🔗 GitHub: https://github.com/TatianaTchouakam
