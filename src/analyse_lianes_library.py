from sqlalchemy import create_engine

def connect_db():
    engine = create_engine("mysql+pymysql://root:password/lianes_library")
    return engine

if __name__ == "__main__":
    engine = connect_db()
    print("Connexion réussie 🚀")

    import pandas as pd
from sqlalchemy import create_engine

def connect_db():
    engine = create_engine("mysql+pymysql://root:password/lianes_library")
    return engine


def load_data(engine):
    query = """
    SELECT 
        l.loan_id,
        f.first_name,
        f.last_name,
        b.title,
        l.loan_date,
        l.due_date,
        l.return_date
    FROM loans l
    JOIN friends f ON l.friend_id = f.friend_id
    JOIN books b ON l.isbn = b.isbn
    """
    return pd.read_sql(query, engine)


def main():
    engine = connect_db()
    df = load_data(engine)

    print("📚 DATA FROM LIANE'S LIBRARY")
    print(df)
    print("\n📊 SUMMARY")
    print("Total loans:", len(df))
    print("Returned:", df["return_date"].notna().sum())
    print("Still borrowed:", df["return_date"].isna().sum())


if __name__ == "__main__":
    main()





    import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

def connect_db():
    """Connect to the MySQL database."""
    engine = create_engine("mysql+pymysql://root:19921992@127.0.0.1:3306/lianes_library")
    return engine

def load_data(engine):
    """Load library loan data as a pandas DataFrame."""
    query = """
    SELECT 
        l.loan_id,
        f.first_name,
        f.last_name,
        b.title,
        b.genre,
        l.loan_date,
        l.due_date,
        l.return_date
    FROM loans l
    JOIN friends f ON l.friend_id = f.friend_id
    JOIN books b ON l.isbn = b.isbn
    """
    return pd.read_sql(query, engine)

def print_preview(df):
    """Print the first few rows of the DataFrame."""
    print("First rows of data:")
    print(df.head(), "\n")

def print_summary(df):
    """Print summary statistics for the library loans."""
    print("Summary statistics:")
    print("Total number of loans:", len(df))
    print("Returned books:", df["return_date"].notna().sum())
    print("Books still on loan:", df["return_date"].isna().sum(), "\n")

def plot_loans_by_genre(df, output_path):
    """Create and save a bar chart of loans by genre."""
    genre_counts = df["genre"].value_counts()

    plt.figure(figsize=(10, 5))
    plt.bar(genre_counts.index, genre_counts.values)
    plt.title("Number of Loans by Genre")
    plt.xlabel("Genre")
    plt.ylabel("Number of Loans")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

def main():
    output_path = "reports/loans_by_genre.png"

    engine = connect_db()
    df = load_data(engine)
    print_preview(df)
    print_summary(df)
    plot_loans_by_genre(df, output_path)

# Only run main() when this file is executed directly
if __name__ == "__main__":
    main()
