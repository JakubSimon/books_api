DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS author_book;
DROP TABLE IF EXISTS category_book;

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    published_date TEXT NULL,
    average_rating INTEGER NULL,
    ratings_count INTEGER NULL,
    thumbnail TEXT NULL

);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE author_book (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     book_id INTEGER NOT NULL,
     author_id INTEGER NOT NULL,
     FOREIGN KEY (author_id) REFERENCES authors(id),
     FOREIGN KEY (book_id) REFERENCES books(id)
);
CREATE TABLE category_book(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     book_id INTEGER NOT NULL,
     category_id INTEGER NOT NULL,
     FOREIGN KEY (category_id) REFERENCES categories(id),
     FOREIGN KEY (book_id) REFERENCES books(id)
);




