from books_library_app import app
from flask import request
from books_library_app.books_library import selecting_books, select_books_from_id, books_from_authors, fetch_api

@app.route('/')
def index():
    return {'results': 'Check possible methods and URI on https://github.com/JakubSimon/books_api'}


@app.route('/books', methods=['GET'])
def list_books():
    incoming_data = request.args.to_dict()
    if len(incoming_data) == 0:
        return {'results': selecting_books()}
    elif len(incoming_data) == 1 and "published_date" in incoming_data.keys():
        published_date = str(request.args.get('published_date'))
        return {'results': selecting_books(published_date)}
    elif len(incoming_data) == 1 and "sort" in incoming_data.keys():
        sort = str(request.args.get('sort'))
        return {'results': selecting_books(sort=sort)}
    elif len(incoming_data) == 1 and "author" in incoming_data.keys():
        authors_list = request.args.getlist('author')
        authors_list = [author[1:-1] for author in authors_list]
        return {'results': books_from_authors(authors_list)}
    else:

        return {'results': 'Wrong parameter. Example acceptable parameters: : /books?published_date=2000 , '
                           '/books?sort=published_date , /books?sort=-published_date , '
                           '/books?author="Jan Kowalski"&author="Anna Kowalska"'}


@app.route('/books/<book_id>/', methods=['GET'])
def book(book_id):
    try:
        return {'results': select_books_from_id(book_id)}
    except AttributeError:
        return {"results": f"This ID is not in the database: {book_id}"
                           f"{(f' and ID should be a number' if not book_id.isnumeric() else '')}"}


@app.route('/db', methods=['POST'])
def db():
    if request.method == 'POST':
        req_q = request.get_json()
        if not 'q' in req_q:
            return {'results': 'Body should look like this {"q": "name_of_volumes"}'}
        try:
            return {"results": fetch_api(req_q)}
        except KeyError:
            return {'results': f"No one volumes contains this text: {req_q['q']}"}
    return {'results': "You should use POST method"}


@app.errorhandler(404)
def not_found(e):
    e = 404
    return {'results': 'ERROR 404. Check possible methods and URI on https://github.com/JakubSimon/books_api'}

