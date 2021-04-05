from books_library_app.db import get_db
from flask import jsonify
import requests
from operator import itemgetter

def filter_books(published_date):
    db = get_db()
    books = db.execute("SELECT title FROM books WHERE published_date LIKE ?", (published_date+'%', )).fetchall()
    books = [book[0] for book in books]
    return books


def sort_books(sort):
    db = get_db()
    if sort == "published_date" or sort == "-published_date":
        books = db.execute(f"""
        SELECT books.title, authors.name, books.published_date, 
        books.average_rating, books.ratings_count, books.thumbnail 
        FROM author_book 
        JOIN authors ON author_book.author_id = authors.id 
        JOIN books ON books.id = author_book.book_id 
        ORDER BY books.published_date {'DESC' if sort == "published_date" else ''}
    """).fetchall()
    else:
        return "Wrong param"

    list_of_books = []
    for book in books:
        list_of_books.append(dict(zip(book.keys(), book)))

    return list_of_books


def authors_books(authors_list):
    db = get_db()
    db = db.cursor()

    books = db.execute(f"""
        SELECT books.title, authors.name, books.published_date, 
        books.average_rating, books.ratings_count, books.thumbnail 
        FROM author_book 
        JOIN authors ON author_book.author_id = authors.id 
        JOIN books ON books.id = author_book.book_id 
        WHERE authors.name {f'IN {tuple(authors_list)}' if len(authors_list) > 1 else f'= "{authors_list[0]}"'}
    """).fetchall()

    list_of_books = []
    for book in books:
        list_of_books.append(dict(zip(book.keys(), book)))

    return list_of_books

    # books = db.execute("SELECT books.title, authors.name, books.published_date, books.average_rating, books.ratings_count, books.thumbnail "
    #     "FROM author_book "
    #     "JOIN authors ON author_book.author_id = authors.id "
    #     "JOIN books ON books.id = author_book.book_id "
    #     f"WHERE authors.name IN {tuple(authors_list)}")
    # list_of_books = []
    # for book in books:
    #     list_of_books.append(dict(zip(book.keys(), book)))
    # return list_of_books



def get_book(book_id):
    db = get_db()
    categories = db.execute(
        'SELECT cat.id, categories.name'
        ' FROM category_book cat JOIN categories categories ON cat.category_id = categories.id'
        ' WHERE cat.book_id = ?',
        (book_id,)
    ).fetchall()
    authors = db.execute(
        'SELECT author.id, author.name'
        ' FROM author_book aut JOIN authors author ON aut.author_id = author.id'
        ' WHERE aut.book_id = ?',
        (book_id,)
    ).fetchall()

    def dict_from_row(row):
        return dict(zip(row.keys(), row))

    categories = ([dict_from_row(row) for row in categories])
    authors = ([dict_from_row(row) for row in authors])
    book = db.execute(
        'SELECT * from books'
        ' WHERE id = ?',
        (book_id,)
    ).fetchone()
    book = dict_from_row(book)
    book["categories"] = [category["name"] for category in categories]
    book["authors"] = [author["name"] for author in authors]

    order_keys = ["title", "authors", "published_date",
                  "categories", "average_rating", "ratings_count", "thumbnail"]
    ordered_dict = {}
    for key in order_keys:
        ordered_dict[key] = book[key]
    return ordered_dict


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
            print(author)
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

    return True


def sorting(sort):
    if sort == "published_date" or sort == "-published_date":
        db = get_db()
        num_of_rows = db.execute("SELECT COUNT(*) FROM books").fetchone()
        list_of_books = []
        for book_id in range(1, num_of_rows[0]+1):
            categories = db.execute(
                'SELECT cat.id, categories.name'
                ' FROM category_book cat JOIN categories categories ON cat.category_id = categories.id'
                ' WHERE cat.book_id = ?',
                (book_id,)
            ).fetchall()
            authors = db.execute(
                'SELECT author.id, author.name'
                ' FROM author_book aut JOIN authors author ON aut.author_id = author.id'
                ' WHERE aut.book_id = ?',
                (book_id,)
            ).fetchall()

            def dict_from_row(row):
                return dict(zip(row.keys(), row))

            categories = ([dict_from_row(row) for row in categories])
            authors = ([dict_from_row(row) for row in authors])
            book = db.execute(
                'SELECT * from books'
                ' WHERE id = ?',
                (book_id,)
            ).fetchone()
            book = dict_from_row(book)
            book["categories"] = [category["name"] for category in categories]
            book["authors"] = [author["name"] for author in authors]

            order_keys = ["title", "authors", "published_date",
                          "categories", "average_rating", "ratings_count", "thumbnail"]

            ordered_dict = {}
            for key in order_keys:
                ordered_dict[key] = book[key]

            list_of_books.append(ordered_dict)

        if sort == "published_date":
            sorted_books = sorted(list_of_books, key=itemgetter('published_date'), reverse=True)
        else:
            sorted_books = sorted(list_of_books, key=itemgetter('published_date'))

        return sorted_books

    else:
        return "Wrong param"
