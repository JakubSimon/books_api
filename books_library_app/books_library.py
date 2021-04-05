from books_library_app.db import get_db
import requests
from operator import itemgetter


# selects books with passed ID
def select_books_from_id(book_id):
    db = get_db()
    categories = db.execute("""
            SELECT cat.id, categories.name 
            FROM category_book cat 
            JOIN categories categories ON cat.category_id = categories.id 
            WHERE cat.book_id = ?""", (book_id,)).fetchall()

    authors = db.execute("""
            SELECT author.id, author.name 
            FROM author_book aut 
            JOIN authors author ON aut.author_id = author.id 
            WHERE aut.book_id = ?""", (book_id,)).fetchall()

    categories = ([dict_from_row(row) for row in categories])
    authors = ([dict_from_row(row) for row in authors])

    book = db.execute("""
            SELECT * from books 
            WHERE id = ?""", (book_id,)).fetchone()

    book = dict_from_row(book)

    book["categories"] = [category["name"] for category in categories]
    book["authors"] = [author["name"] for author in authors]

    order_keys = ["id", "title", "authors", "published_date",
                  "categories", "average_rating", "ratings_count", "thumbnail"]

    ordered_dict = {}

    for key in order_keys:
        ordered_dict[key] = book[key]

    return ordered_dict


# modifies ROW object into a dictionary
def dict_from_row(row):
    return dict(zip(row.keys(), row))


# selects books id to print by select_books_from_id function
def selecting_books(published_date='', sort=False):
    db = get_db()
    list_of_results = db.execute(f"""
                SELECT {"COUNT(*)" if not published_date else "id"}
                FROM books 
                {f"WHERE published_date LIKE '{published_date}%'" if published_date else ''}
    """).fetchall()
    list_of_books = []
    if published_date:
        for book_id in list_of_results:
            print(book_id[0])
            book = select_books_from_id(book_id[0])
            list_of_books.append(book)
    else:
        for book_id in range(1, list_of_results[0][0]+1):
            book = select_books_from_id(book_id)
            list_of_books.append(book)

    if sort:
        if sort == "published_date":
            list_of_books = sorted(list_of_books, key=itemgetter('published_date'), reverse=True)
        elif sort == "-published_date":
            list_of_books = sorted(list_of_books, key=itemgetter('published_date'))
        else:
            return "Wrong parameter. Acceptable parameters: published_date or -published_date"
    if not list_of_books:
        return "No matching results"

    return list_of_books


# selects books id of passed authors list
def books_from_authors(authors_list):
    db = get_db()
    books_id = db.execute(f"""
            SELECT DISTINCT author_book.book_id
            FROM author_book 
            JOIN authors ON author_book.author_id = authors.id
            WHERE authors.name {f'IN {tuple(authors_list)}' if len(authors_list) > 1 
            else f'= "{authors_list[0]}"'}
    """).fetchall()

    list_of_books = []

    for book_id in books_id:
        book = select_books_from_id(book_id[0])
        list_of_books.append(book)

    return list_of_books


# adds data to database
def fetch_api(params):
    url = 'https://www.googleapis.com/books/v1/volumes'
    resp = requests.get(url=url, params=params)
    con = get_db()
    cur = con.cursor()
    data = resp.json()  # Check the JSON Response Content documentation below
    for item in data["items"]:
        title = item["volumeInfo"]["title"]
        try:
            authors = [author for author in item["volumeInfo"]["authors"]]
        except KeyError:
            authors = ["Unknown"]
        try:
            categories = [category for category in item["volumeInfo"]["categories"]]
        except KeyError:
            categories = []
        try:
            published_date = item["volumeInfo"]["publishedDate"]
        except KeyError:
            published_date = ""
        try:
            thumbnail = item["volumeInfo"]["imageLinks"]["thumbnail"]
        except KeyError:
            thumbnail = ""
        try:
            average_rating = item["volumeInfo"]["averageRating"]
        except KeyError:
            average_rating = ""
        try:
            ratings_count = item["volumeInfo"]["ratingsCount"]
        except KeyError:
            ratings_count = ""

        for author in authors:
            duplicate_author = cur.execute("SELECT name FROM authors WHERE name = (?)", (author,))
            if duplicate_author.fetchall():
                pass
            else:
                cur.execute("INSERT INTO authors (name) VALUES (?)", (author,))
                con.commit()

        for category in categories:
            duplicate_category = cur.execute("SELECT name FROM categories WHERE name = (?)", (category,))
            if duplicate_category.fetchall():
                pass
            else:
                cur.execute("INSERT INTO categories (name) VALUES (?)", (category,))
                con.commit()

        book_duplicate = cur.execute("SELECT id FROM books WHERE title = (?) AND published_date = (?)",
                                     (title, published_date))
        if not book_duplicate.fetchall():
            cur.execute("INSERT INTO books (title, published_date, average_rating, ratings_count, thumbnail) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (title, published_date, average_rating, ratings_count, thumbnail))
            con.commit()

            for author in authors:
                author_id = cur.execute("SELECT id FROM authors WHERE name = (?)", (author,)).fetchone()[0]
                book_id = cur.execute("SELECT id FROM books WHERE title = (?) "
                                      "AND published_date = (?)", (title, published_date)
                                      ).fetchone()[0]
                cur.execute("INSERT INTO author_book (book_id, author_id) VALUES (?, ?)", (book_id, author_id))
                con.commit()

            if categories:
                for category in categories:
                    category_id = cur.execute("SELECT id FROM categories WHERE name = (?)", (category,)).fetchone()[0]
                    book_id = cur.execute("SELECT id FROM books WHERE title = (?) "
                                          "AND published_date = (?)", (title, published_date)).fetchone()[0]

                    cur.execute("INSERT INTO category_book (book_id, category_id) VALUES (?, ?)",
                                (book_id, category_id))
                    con.commit()

    return "Database updated"
