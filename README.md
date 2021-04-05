### Create an environment

```
python3 -m venv venv
``` 

### Activate the environment
Linux:
```
. venv/bin/activate
```
Windows:
```
venv\Scripts\activate
```
### Install flask:
```
pip install -r requirements.txt
```

### Run app
Linux:
```
export FLASK_APP=books_app.py
```
Windows:
```
set FLASK_APP="books_app.py"
```

### Database initialization
```
flask init-db
```

### Methods and URI
* GET '/books' - prints list of all books
* GET '/books?published_date=1995' - filters books by published year
* GET '/books?sort=published_date' -  sorts books from the newest published date
* GET '/books?sort=-published_date' - sorts books from the oldest published date
* GET 'GET /books/<bookId> ' - prints book with the selected ID
* GET 'GET /books?author="Jan Kowalski"&author="Anna Kowalska"' allows to print books of selected authors (multiple arguments are allowed, first name and last name in quotation mark are required)
* POST '/db' - gets data from body {"q": "example_word"}, downloads data set from https://www.googleapis.com/books/v1/volumes?q=example_word and adds it to database
