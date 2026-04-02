import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)


# =========================
# HELPER FUNCTIONS
# =========================
def run_query(query):
    return pd.read_sql(query, engine)

def execute_query(query):
    with engine.begin() as conn:
        conn.exec_driver_sql(query)

def esc(value):
    return str(value).replace("'", "''").strip()

def safe_metric(query, default=0):
    df = run_query(query)
    if df.empty:
        return default
    value = df.iloc[0, 0]
    if pd.isna(value):
        return default
    return value

def section_title(title):
    st.markdown(f"## {title}")

def table_or_info(df, info_message="No data available yet."):
    if df.empty:
        st.info(info_message)
    else:
        st.dataframe(df, use_container_width=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📚 Liane's Library")
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📘 Books", "👥 Friends", "🔄 Loans", "✍️ Authors"]
)

# =========================
# HOME PAGE
# =========================
if menu == "🏠 Home":
    st.markdown("# 📚 Liane's Library")
    st.markdown("### Smart Book Tracking & Lending System")

    section_title("🔍 Global Search")
    search = st.text_input("Search books, friends, authors, or genres")

    if search:
        search_clean = esc(search)

        search_results = run_query(f"""
            SELECT 
                'Book' AS result_type,
                b.title AS main_result,
                b.genre AS detail_1,
                CONCAT(a.first_name, ' ', a.last_name) AS detail_2
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            WHERE LOWER(b.title) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(b.genre) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(a.first_name) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(a.last_name) LIKE LOWER('%%{search_clean}%%')

            UNION

            SELECT
                'Friend' AS result_type,
                CONCAT(f.first_name, ' ', f.last_name) AS main_result,
                f.city AS detail_1,
                f.email AS detail_2
            FROM friends f
            WHERE LOWER(f.first_name) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(f.last_name) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(f.city) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(f.email) LIKE LOWER('%%{search_clean}%%')

            UNION

            SELECT
                'Author' AS result_type,
                CONCAT(a.first_name, ' ', a.last_name) AS main_result,
                a.nationality AS detail_1,
                CAST(a.birth_year AS CHAR) AS detail_2
            FROM authors a
            WHERE LOWER(a.first_name) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(a.last_name) LIKE LOWER('%%{search_clean}%%')
               OR LOWER(a.nationality) LIKE LOWER('%%{search_clean}%%')
        """)

        if search_results.empty:
            st.warning("No results found.")
        else:
            st.success(f"{len(search_results)} result(s) found.")
            st.dataframe(search_results, use_container_width=True)

    total_books = safe_metric("SELECT COUNT(*) AS value FROM books")
    current_loans = safe_metric("""
        SELECT COUNT(*) AS value
        FROM loans
        WHERE return_date IS NULL
    """)
    overdue_loans = safe_metric("""
        SELECT COUNT(*) AS value
        FROM loans
        WHERE return_date IS NULL
          AND due_date < CURDATE()
    """)
    current_borrowers = safe_metric("""
        SELECT COUNT(DISTINCT friend_id) AS value
        FROM loans
        WHERE return_date IS NULL
    """)
    return_rate = safe_metric("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN return_date IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2
        ) AS value
        FROM loans
    """, 0)

    section_title("📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Books", total_books)
    col2.metric("Current Loans", current_loans)
    col3.metric("Overdue Loans", overdue_loans)
    col4.metric("Active Borrowers", current_borrowers)
    col5.metric("Return Rate (%)", return_rate)

    section_title("🔄 Current Loans")
    current_loans_df = run_query("""
        SELECT 
            l.loan_id,
            b.title AS book_title,
            b.genre,
            CONCAT(f.first_name, ' ', f.last_name) AS friend_name,
            l.loan_date,
            l.due_date
        FROM loans l
        JOIN books b ON l.isbn = b.isbn
        JOIN friends f ON l.friend_id = f.friend_id
        WHERE l.return_date IS NULL
        ORDER BY l.due_date ASC
    """)
    table_or_info(current_loans_df, "No current loans.")

    section_title("⏰ Overdue Loans")
    overdue_loans_df = run_query("""
        SELECT 
            l.loan_id,
            b.title AS book_title,
            b.genre,
            CONCAT(f.first_name, ' ', f.last_name) AS friend_name,
            l.loan_date,
            l.due_date,
            DATEDIFF(CURDATE(), l.due_date) AS days_overdue
        FROM loans l
        JOIN books b ON l.isbn = b.isbn
        JOIN friends f ON l.friend_id = f.friend_id
        WHERE l.return_date IS NULL
          AND l.due_date < CURDATE()
        ORDER BY days_overdue DESC
    """)
    table_or_info(overdue_loans_df, "No overdue loans.")

    col_a, col_b = st.columns(2)

    with col_a:
        section_title("👥 Top 5 Frequent Borrowers")
        frequent_borrowers_df = run_query("""
            SELECT 
                CONCAT(f.first_name, ' ', f.last_name) AS friend_name,
                COUNT(l.loan_id) AS total_loans
            FROM friends f
            JOIN loans l ON f.friend_id = l.friend_id
            GROUP BY f.friend_id, f.first_name, f.last_name
            ORDER BY total_loans DESC, friend_name ASC
            LIMIT 5
        """)
        table_or_info(frequent_borrowers_df, "No borrower activity yet.")

    with col_b:
        section_title("📚 Top 5 Most Borrowed Books")
        most_borrowed_books_df = run_query("""
            SELECT 
                b.title AS book_title,
                b.genre,
                COUNT(l.loan_id) AS total_loans
            FROM books b
            JOIN loans l ON b.isbn = l.isbn
            GROUP BY b.isbn, b.title, b.genre
            ORDER BY total_loans DESC, b.title ASC
            LIMIT 5
        """)
        table_or_info(most_borrowed_books_df, "No borrowing data yet.")

    section_title("📈 Loan Activity by Genre")
    loans_by_genre_df = run_query("""
        SELECT 
            b.genre,
            COUNT(l.loan_id) AS total_loans
        FROM books b
        JOIN loans l ON b.isbn = l.isbn
        GROUP BY b.genre
        ORDER BY total_loans DESC
    """)
    if loans_by_genre_df.empty:
        st.info("No loan activity by genre available yet.")
    else:
        st.bar_chart(loans_by_genre_df.set_index("genre"))

# =========================
# BOOKS PAGE
# =========================
elif menu == "📘 Books":
    st.title("📘 Books")

    section_title("⚡ Manage Books")
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### ➕ Add a Book")

        isbn = st.text_input("ISBN", key="book_isbn")
        title = st.text_input("Title", key="book_title")
        genre = st.text_input("Genre", key="book_genre")
        note = st.text_area("Note (optional)", key="book_note")
        published_year = int(
            st.number_input(
                "Published Year",
                min_value=1000,
                max_value=2100,
                step=1,
                key="book_year"
            )
        )

        author_mode = st.radio(
            "Author option",
            ["Use Existing Author", "Add New Author"],
            key="author_mode"
        )

        author_id = None

        if author_mode == "Use Existing Author":
            authors_df = run_query("""
                SELECT author_id, first_name, last_name
                FROM authors
                ORDER BY first_name ASC, last_name ASC
            """)

            if authors_df.empty:
                st.warning("No authors available yet. Please choose 'Add New Author'.")
            else:
                authors_df["author_label"] = authors_df["first_name"] + " " + authors_df["last_name"]
                author_map = dict(zip(authors_df["author_label"], authors_df["author_id"]))

                selected_author_label = st.selectbox(
                    "Select Author",
                    authors_df["author_label"].tolist(),
                    key="book_author_select"
                )
                author_id = author_map[selected_author_label]
        else:
            new_author_first_name = st.text_input("Author First Name", key="new_author_first_name")
            new_author_last_name = st.text_input("Author Last Name", key="new_author_last_name")
            new_author_nationality = st.text_input("Author Nationality", key="new_author_nationality")
            new_author_birth_year = int(
                st.number_input(
                    "Author Birth Year",
                    min_value=0,
                    max_value=2100,
                    step=1,
                    key="new_author_birth_year"
                )
            )

        if st.button("Add Book", key="add_book_btn"):
            isbn_clean = esc(isbn)
            title_clean = esc(title)
            genre_clean = esc(genre)
            note_clean = esc(note)

            if isbn_clean == "" or title_clean == "" or genre_clean == "":
                st.error("Please fill in ISBN, title, and genre.")
            else:
                book_check = run_query(f"""
                    SELECT * FROM books
                    WHERE isbn = '{isbn_clean}'
                """)

                if not book_check.empty:
                    st.error("This book already exists.")
                else:
                    if author_mode == "Use Existing Author":
                        if author_id is None:
                            st.error("Please select an existing author.")
                        else:
                            execute_query(f"""
                                INSERT INTO books (isbn, title, genre, note, published_year, author_id)
                                VALUES (
                                    '{isbn_clean}',
                                    '{title_clean}',
                                    '{genre_clean}',
                                    '{note_clean}',
                                    {published_year},
                                    {author_id}
                                )
                            """)
                            st.success("Book added successfully.")
                            st.rerun()
                    else:
                        first_name_clean = esc(new_author_first_name)
                        last_name_clean = esc(new_author_last_name)
                        nationality_clean = esc(new_author_nationality)

                        if first_name_clean == "" or last_name_clean == "":
                            st.error("Please enter the new author's first and last name.")
                        else:
                            existing_author_check = run_query(f"""
                                SELECT author_id
                                FROM authors
                                WHERE LOWER(first_name) = LOWER('{first_name_clean}')
                                  AND LOWER(last_name) = LOWER('{last_name_clean}')
                            """)

                            if existing_author_check.empty:
                                execute_query(f"""
                                    INSERT INTO authors (first_name, last_name, nationality, birth_year)
                                    VALUES (
                                        '{first_name_clean}',
                                        '{last_name_clean}',
                                        '{nationality_clean}',
                                        {new_author_birth_year}
                                    )
                                """)

                                new_author_id = run_query(f"""
                                    SELECT author_id
                                    FROM authors
                                    WHERE LOWER(first_name) = LOWER('{first_name_clean}')
                                      AND LOWER(last_name) = LOWER('{last_name_clean}')
                                    ORDER BY author_id DESC
                                    LIMIT 1
                                """).iloc[0, 0]
                            else:
                                new_author_id = existing_author_check.iloc[0, 0]

                            execute_query(f"""
                                INSERT INTO books (isbn, title, genre, note, published_year, author_id)
                                VALUES (
                                    '{isbn_clean}',
                                    '{title_clean}',
                                    '{genre_clean}',
                                    '{note_clean}',
                                    {published_year},
                                    {new_author_id}
                                )
                            """)
                            st.success("Book added successfully.")
                            st.rerun()

    with col_right:
        st.markdown("### 🗑️ Delete a Book")

        books_delete_df = run_query("""
            SELECT 
                b.isbn,
                b.title,
                b.genre,
                CONCAT(a.first_name, ' ', a.last_name) AS author_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            ORDER BY b.title ASC
        """)

        if books_delete_df.empty:
            st.info("No books available to delete.")
        else:
            books_delete_df["book_label"] = (
                books_delete_df["title"] + " | " +
                books_delete_df["isbn"] + " | " +
                books_delete_df["genre"].fillna("") + " | " +
                books_delete_df["author_name"].fillna("")
            )
            book_delete_map = dict(zip(books_delete_df["book_label"], books_delete_df["isbn"]))

            selected_book_delete = st.selectbox(
                "Select Book to Delete",
                books_delete_df["book_label"].tolist(),
                key="book_delete_select"
            )

            confirm_delete_book = st.checkbox("I confirm book deletion", key="confirm_delete_book")

            if st.button("Delete Book", key="delete_book_btn"):
                isbn_delete = book_delete_map[selected_book_delete]

                book_check = run_query(f"""
                    SELECT * FROM books
                    WHERE isbn = '{esc(isbn_delete)}'
                """)

                loan_check = run_query(f"""
                    SELECT * FROM loans
                    WHERE isbn = '{esc(isbn_delete)}'
                      AND return_date IS NULL
                """)

                if book_check.empty:
                    st.warning("Book not found.")
                elif not confirm_delete_book:
                    st.warning("Please confirm deletion first.")
                elif not loan_check.empty:
                    st.error("Cannot delete this book because it is currently borrowed.")
                else:
                    execute_query(f"""
                        DELETE FROM books
                        WHERE isbn = '{esc(isbn_delete)}'
                    """)
                    st.success("Book deleted successfully.")
                    st.rerun()

    section_title("🔍 Search and Filter Books")
    df_books = run_query("""
        SELECT 
            b.isbn,
            b.title,
            b.genre,
            b.note,
            b.published_year,
            CONCAT(a.first_name, ' ', a.last_name) AS author_name
        FROM books b
        LEFT JOIN authors a ON b.author_id = a.author_id
        ORDER BY b.title ASC
    """)

    if df_books.empty:
        st.info("No books available yet.")
    else:
        col_filter_1, col_filter_2 = st.columns(2)

        with col_filter_1:
            book_search = st.text_input("Search by title, author, or ISBN", key="book_search")

        with col_filter_2:
            genre_options = ["All"] + sorted(df_books["genre"].dropna().unique().tolist())
            selected_genre = st.selectbox("Filter by genre", genre_options, key="books_genre_filter")

        filtered_books = df_books.copy()

        if book_search:
            search_term = book_search.lower()
            filtered_books = filtered_books[
                filtered_books["title"].astype(str).str.lower().str.contains(search_term, na=False) |
                filtered_books["author_name"].astype(str).str.lower().str.contains(search_term, na=False) |
                filtered_books["isbn"].astype(str).str.lower().str.contains(search_term, na=False)
            ]

        if selected_genre != "All":
            filtered_books = filtered_books[filtered_books["genre"] == selected_genre]

        section_title("📚 Library Books")
        table_or_info(filtered_books, "No books match your search or filter.")

        section_title("🔥 Top Borrowed Books")
        top_borrowed_books_df = run_query("""
            SELECT 
                b.title AS book_title,
                b.genre,
                COUNT(l.loan_id) AS total_loans
            FROM books b
            JOIN loans l ON b.isbn = l.isbn
            GROUP BY b.isbn, b.title, b.genre
            ORDER BY total_loans DESC, b.title ASC
            LIMIT 5
        """)
        table_or_info(top_borrowed_books_df, "No borrowing data yet.")

# =========================
# FRIENDS PAGE
# =========================
elif menu == "👥 Friends":
    st.title("👥 Friends")
    section_title("⚡ Manage Friends")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ➕ Add a Friend")

        first_name = st.text_input("First Name", key="friends_add_first")
        last_name = st.text_input("Last Name", key="friends_add_last")
        email = st.text_input("Email", key="friends_add_email")
        phone = st.text_input("Phone", key="friends_add_phone")
        city = st.text_input("City", key="friends_add_city")
        max_loans = int(st.number_input("Max Loans", min_value=1, step=1, key="friends_add_max"))

        if st.button("Add Friend", key="friends_add_btn"):
            first_name_clean = esc(first_name)
            last_name_clean = esc(last_name)
            email_clean = esc(email)
            phone_clean = esc(phone)
            city_clean = esc(city)

            if first_name_clean == "" or last_name_clean == "":
                st.error("Please enter at least first and last name.")
            else:
                duplicate_friend_check = run_query(f"""
                    SELECT *
                    FROM friends
                    WHERE LOWER(first_name) = LOWER('{first_name_clean}')
                      AND LOWER(last_name) = LOWER('{last_name_clean}')
                      AND LOWER(COALESCE(email, '')) = LOWER('{email_clean}')
                """)

                if not duplicate_friend_check.empty:
                    st.error("This friend already exists.")
                else:
                    execute_query(f"""
                        INSERT INTO friends (first_name, last_name, email, phone, city, max_loans)
                        VALUES (
                            '{first_name_clean}',
                            '{last_name_clean}',
                            '{email_clean}',
                            '{phone_clean}',
                            '{city_clean}',
                            {max_loans}
                        )
                    """)
                    st.success("Friend added successfully.")
                    st.rerun()

    with col2:
        st.markdown("### 🗑️ Delete a Friend")

        friends_delete_df = run_query("""
            SELECT 
                friend_id,
                first_name,
                last_name,
                email,
                city
            FROM friends
            ORDER BY first_name ASC, last_name ASC
        """)

        if friends_delete_df.empty:
            st.info("No friends available to delete.")
        else:
            friends_delete_df["friend_label"] = (
                friends_delete_df["first_name"] + " " +
                friends_delete_df["last_name"] + " | " +
                friends_delete_df["email"].fillna("") + " | " +
                friends_delete_df["city"].fillna("")
            )
            friend_delete_map = dict(zip(friends_delete_df["friend_label"], friends_delete_df["friend_id"]))

            selected_friend_delete = st.selectbox(
                "Select Friend to Delete",
                friends_delete_df["friend_label"].tolist(),
                key="friends_delete_select"
            )

            confirm_delete_friend = st.checkbox("I confirm friend deletion", key="confirm_delete_friend")

            if st.button("Delete Friend", key="delete_friend_btn"):
                friend_id = friend_delete_map[selected_friend_delete]

                friend_check = run_query(f"""
                    SELECT * FROM friends
                    WHERE friend_id = {friend_id}
                """)

                loan_check = run_query(f"""
                    SELECT * FROM loans
                    WHERE friend_id = {friend_id}
                      AND return_date IS NULL
                """)

                if friend_check.empty:
                    st.warning("Friend not found.")
                elif not confirm_delete_friend:
                    st.warning("Please confirm deletion first.")
                elif not loan_check.empty:
                    st.error("Cannot delete this friend because they still have active loans.")
                else:
                    execute_query(f"""
                        DELETE FROM friends
                        WHERE friend_id = {friend_id}
                    """)
                    st.success("Friend deleted successfully.")
                    st.rerun()

    section_title("👥 Friends List")
    df_friends = run_query("""
        SELECT *
        FROM friends
        ORDER BY last_name ASC, first_name ASC
    """)
    table_or_info(df_friends, "No friends available yet.")

    section_title("📊 Borrowing Activity")
    borrowing_df = run_query("""
        SELECT 
            f.friend_id,
            f.first_name,
            f.last_name,
            COUNT(l.loan_id) AS total_loans
        FROM friends f
        LEFT JOIN loans l ON f.friend_id = l.friend_id
        GROUP BY f.friend_id, f.first_name, f.last_name
        ORDER BY total_loans DESC
    """)
    table_or_info(borrowing_df, "No borrowing activity yet.")

    section_title("📚 Current Loans per Friend")
    current_loans_df = run_query("""
        SELECT 
            f.first_name,
            f.last_name,
            COUNT(l.loan_id) AS current_loans
        FROM friends f
        LEFT JOIN loans l 
            ON f.friend_id = l.friend_id 
            AND l.return_date IS NULL
        GROUP BY f.friend_id, f.first_name, f.last_name
        ORDER BY current_loans DESC
    """)
    table_or_info(current_loans_df, "No current loans yet.")

# =========================
# LOANS PAGE
# =========================
elif menu == "🔄 Loans":
    st.title("🔄 Loans")

    section_title("✅ Available Books")
    available_books_df = run_query("""
        SELECT 
            b.isbn,
            b.title AS book_title,
            b.genre
        FROM books b
        WHERE b.isbn NOT IN (
            SELECT l.isbn
            FROM loans l
            WHERE l.return_date IS NULL
        )
        ORDER BY b.genre ASC, b.title ASC
    """)
    table_or_info(available_books_df, "No books available right now.")

    section_title("⚡ Manage Loans")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ➕ Create a Loan")

        available_books_add_df = run_query("""
            SELECT 
                b.isbn,
                b.title
            FROM books b
            WHERE b.isbn NOT IN (
                SELECT l.isbn
                FROM loans l
                WHERE l.return_date IS NULL
            )
            ORDER BY b.title ASC
        """)

        friends_add_df = run_query("""
            SELECT 
                friend_id,
                first_name,
                last_name,
                max_loans
            FROM friends
            ORDER BY first_name ASC, last_name ASC
        """)

        selected_book_label = None
        selected_friend_label = None
        book_map = {}
        friend_map = {}

        if available_books_add_df.empty:
            st.warning("No available books to loan.")
        else:
            available_books_add_df["book_label"] = (
                available_books_add_df["isbn"] + " - " + available_books_add_df["title"]
            )
            book_map = dict(zip(available_books_add_df["book_label"], available_books_add_df["isbn"]))

            selected_book_label = st.selectbox(
                "Select Book",
                available_books_add_df["book_label"].tolist(),
                key="loan_page_book_select"
            )

        if friends_add_df.empty:
            st.warning("No friends available.")
        else:
            friends_add_df["friend_label"] = friends_add_df["first_name"] + " " + friends_add_df["last_name"]
            friend_map = dict(zip(friends_add_df["friend_label"], friends_add_df["friend_id"]))

            selected_friend_label = st.selectbox(
                "Select Friend",
                friends_add_df["friend_label"].tolist(),
                key="loan_page_friend_select"
            )

        if st.button("Add Loan", key="loan_page_add_btn"):
            if selected_book_label is None:
                st.error("Please select a book.")
            elif selected_friend_label is None:
                st.error("Please select a friend.")
            else:
                isbn_clean = book_map[selected_book_label]
                friend_id = friend_map[selected_friend_label]

                book_check = run_query(f"""
                    SELECT * FROM books
                    WHERE isbn = '{isbn_clean}'
                """)

                friend_check = run_query(f"""
                    SELECT * FROM friends
                    WHERE friend_id = {friend_id}
                """)

                loan_check = run_query(f"""
                    SELECT * FROM loans
                    WHERE isbn = '{isbn_clean}'
                      AND return_date IS NULL
                """)

                current_loans_check = run_query(f"""
                    SELECT COUNT(*) AS current_loans
                    FROM loans
                    WHERE friend_id = {friend_id}
                      AND return_date IS NULL
                """)

                if book_check.empty:
                    st.error("Book not found.")
                elif friend_check.empty:
                    st.error("Friend not found.")
                elif not loan_check.empty:
                    st.warning("This book is already on loan.")
                else:
                    max_loans_allowed = friend_check.iloc[0]["max_loans"]
                    current_loans_count = current_loans_check.iloc[0]["current_loans"]

                    if current_loans_count >= max_loans_allowed:
                        st.error("This friend has reached the maximum number of allowed loans.")
                    else:
                        execute_query(f"""
                            INSERT INTO loans (isbn, friend_id, loan_date, due_date)
                            VALUES (
                                '{isbn_clean}',
                                {friend_id},
                                CURDATE(),
                                DATE_ADD(CURDATE(), INTERVAL 14 DAY)
                            )
                        """)
                        st.success("Loan added successfully.")
                        st.rerun()

    with col2:
        st.markdown("### ↩️ Return a Book")

        active_loans_return_df = run_query("""
            SELECT 
                l.loan_id,
                b.title AS book_title,
                CONCAT(f.first_name, ' ', f.last_name) AS friend_name
            FROM loans l
            JOIN books b ON l.isbn = b.isbn
            JOIN friends f ON l.friend_id = f.friend_id
            WHERE l.return_date IS NULL
            ORDER BY b.title ASC
        """)

        if active_loans_return_df.empty:
            st.info("No active loans to return.")
        else:
            active_loans_return_df["return_label"] = (
                active_loans_return_df["book_title"] +
                " - borrowed by " +
                active_loans_return_df["friend_name"]
            )
            return_map = dict(zip(active_loans_return_df["return_label"], active_loans_return_df["loan_id"]))

            selected_return_label = st.selectbox(
                "Select the Book to Return",
                active_loans_return_df["return_label"].tolist(),
                key="return_book_select"
            )

            if st.button("Return Book", key="return_book_btn"):
                loan_id = return_map[selected_return_label]

                loan_check = run_query(f"""
                    SELECT * FROM loans
                    WHERE loan_id = {loan_id}
                      AND return_date IS NULL
                """)

                if loan_check.empty:
                    st.warning("Loan not found or already returned.")
                else:
                    execute_query(f"""
                        UPDATE loans
                        SET return_date = CURDATE()
                        WHERE loan_id = {loan_id}
                    """)
                    st.success("Book returned successfully.")
                    st.rerun()

    section_title("🗑️ Delete a Loan")
    loans_delete_df = run_query("""
        SELECT 
            l.loan_id,
            b.title AS book_title,
            CONCAT(f.first_name, ' ', f.last_name) AS friend_name,
            l.loan_date,
            l.return_date
        FROM loans l
        JOIN books b ON l.isbn = b.isbn
        JOIN friends f ON l.friend_id = f.friend_id
        ORDER BY l.loan_id DESC
    """)

    if loans_delete_df.empty:
        st.info("No loans available to delete.")
    else:
        loans_delete_df["loan_label"] = (
            loans_delete_df["book_title"] + " - " +
            loans_delete_df["friend_name"] + " - " +
            loans_delete_df["loan_date"].astype(str)
        )
        loan_delete_map = dict(zip(loans_delete_df["loan_label"], loans_delete_df["loan_id"]))

        selected_loan_delete = st.selectbox(
            "Select Loan to Delete",
            loans_delete_df["loan_label"].tolist(),
            key="loan_delete_select"
        )

        confirm_delete_loan = st.checkbox("I confirm loan deletion", key="confirm_delete_loan")

        if st.button("Delete Loan", key="loan_delete_btn"):
            loan_id = loan_delete_map[selected_loan_delete]

            loan_check = run_query(f"""
                SELECT * FROM loans
                WHERE loan_id = {loan_id}
            """)

            if loan_check.empty:
                st.warning("Loan not found.")
            elif not confirm_delete_loan:
                st.warning("Please confirm deletion first.")
            else:
                execute_query(f"""
                    DELETE FROM loans
                    WHERE loan_id = {loan_id}
                """)
                st.success("Loan deleted successfully.")
                st.rerun()

    section_title("📋 All Loans")
    df_loans = run_query("""
        SELECT 
            l.loan_id,
            l.isbn,
            b.title AS book_title,
            l.friend_id,
            CONCAT(f.first_name, ' ', f.last_name) AS friend_name,
            l.loan_date,
            l.due_date,
            l.return_date
        FROM loans l
        JOIN books b ON l.isbn = b.isbn
        JOIN friends f ON l.friend_id = f.friend_id
        ORDER BY l.loan_id ASC
    """)
    table_or_info(df_loans, "No loans recorded yet.")

    section_title("📌 Active Loans")
    active_loans_df = run_query("""
        SELECT 
            l.loan_id,
            b.title AS book_title,
            CONCAT(f.first_name, ' ', f.last_name) AS friend_name,
            l.loan_date,
            l.due_date
        FROM loans l
        JOIN books b ON l.isbn = b.isbn
        JOIN friends f ON l.friend_id = f.friend_id
        WHERE l.return_date IS NULL
        ORDER BY l.due_date ASC
    """)
    table_or_info(active_loans_df, "No active loans.")

# =========================
# AUTHORS PAGE
# =========================
elif menu == "✍️ Authors":
    st.title("✍️ Authors")
    section_title("⚡ Manage Authors")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ➕ Add an Author")

        author_first_name = st.text_input("First Name", key="author_add_first")
        author_last_name = st.text_input("Last Name", key="author_add_last")
        author_nationality = st.text_input("Nationality", key="author_add_nationality")
        author_birth_year = int(
            st.number_input(
                "Birth Year",
                min_value=0,
                max_value=2100,
                step=1,
                key="author_add_birth_year"
            )
        )

        if st.button("Add Author", key="author_add_btn"):
            first_name_clean = esc(author_first_name)
            last_name_clean = esc(author_last_name)
            nationality_clean = esc(author_nationality)

            if first_name_clean == "" or last_name_clean == "":
                st.error("Please enter the author's first and last name.")
            else:
                author_check = run_query(f"""
                    SELECT *
                    FROM authors
                    WHERE LOWER(first_name) = LOWER('{first_name_clean}')
                      AND LOWER(last_name) = LOWER('{last_name_clean}')
                """)

                if not author_check.empty:
                    st.error("This author already exists.")
                else:
                    execute_query(f"""
                        INSERT INTO authors (first_name, last_name, nationality, birth_year)
                        VALUES (
                            '{first_name_clean}',
                            '{last_name_clean}',
                            '{nationality_clean}',
                            {author_birth_year}
                        )
                    """)
                    st.success("Author added successfully.")
                    st.rerun()

    with col2:
        st.markdown("### 🗑️ Delete an Author")

        authors_delete_df = run_query("""
            SELECT 
                author_id,
                first_name,
                last_name,
                nationality,
                birth_year
            FROM authors
            ORDER BY first_name ASC, last_name ASC
        """)

        if authors_delete_df.empty:
            st.info("No authors available to delete.")
        else:
            authors_delete_df["author_label"] = (
                authors_delete_df["first_name"] + " " +
                authors_delete_df["last_name"] + " | " +
                authors_delete_df["nationality"].fillna("").astype(str)
            )
            author_delete_map = dict(zip(authors_delete_df["author_label"], authors_delete_df["author_id"]))

            selected_author_delete = st.selectbox(
                "Select Author to Delete",
                authors_delete_df["author_label"].tolist(),
                key="author_delete_select"
            )

            confirm_delete_author = st.checkbox("I confirm author deletion", key="confirm_delete_author")

            if st.button("Delete Author", key="author_delete_btn"):
                author_id = author_delete_map[selected_author_delete]

                author_check = run_query(f"""
                    SELECT * FROM authors
                    WHERE author_id = {author_id}
                """)

                books_check = run_query(f"""
                    SELECT * FROM books
                    WHERE author_id = {author_id}
                """)

                if author_check.empty:
                    st.warning("Author not found.")
                elif not confirm_delete_author:
                    st.warning("Please confirm deletion first.")
                elif not books_check.empty:
                    st.error("Cannot delete this author because they are linked to existing books.")
                else:
                    execute_query(f"""
                        DELETE FROM authors
                        WHERE author_id = {author_id}
                    """)
                    st.success("Author deleted successfully.")
                    st.rerun()

    section_title("✍️ Authors List")
    df_authors = run_query("""
        SELECT *
        FROM authors
        ORDER BY last_name ASC, first_name ASC
    """)
    table_or_info(df_authors, "No authors available yet.")

    section_title("📚 Number of Books per Author")
    books_per_author_df = run_query("""
        SELECT 
            a.author_id,
            a.first_name,
            a.last_name,
            COUNT(b.isbn) AS total_books
        FROM authors a
        LEFT JOIN books b ON a.author_id = b.author_id
        GROUP BY a.author_id, a.first_name, a.last_name
        ORDER BY total_books DESC, a.last_name ASC
    """)
    table_or_info(books_per_author_df, "No author-book data yet.")

    section_title("🔥 Most Borrowed Authors")
    most_borrowed_authors_df = run_query("""
        SELECT 
            a.first_name,
            a.last_name,
            COUNT(l.loan_id) AS total_loans
        FROM authors a
        JOIN books b ON a.author_id = b.author_id
        JOIN loans l ON b.isbn = l.isbn
        GROUP BY a.author_id, a.first_name, a.last_name
        ORDER BY total_loans DESC, a.last_name ASC
    """)
    table_or_info(most_borrowed_authors_df, "No borrowing data for authors yet.")