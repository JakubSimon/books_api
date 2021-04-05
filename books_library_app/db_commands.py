from books_library_app import app
from flask import jsonify, request
from books_library_app.books_library import filter_books, sort_books, authors_books, get_book, fetch_api, sorting


@app.route('/books', methods=['GET'])
def list_books():
    incoming_data = request.args.to_dict()
    if len(incoming_data) == 1 and "published_date" in incoming_data.keys():
        published_date = str(request.args.get('published_date'))
        return jsonify(filter_books(published_date))
    elif len(incoming_data) == 1 and "sort" in incoming_data.keys():
        sort = str(request.args.get('sort'))
        return {'results': sorting(sort)}
    elif len(incoming_data) == 1 and "author" in incoming_data.keys():
        authors_list = request.args.getlist('author')
        authors_list = [author[1:-1] for author in authors_list]
        return {'results': authors_books(authors_list)}
    else:

        return {'status': "Wrong parameter"}


@app.route('/books/<book_id>/', methods=['GET'])
def book(book_id):
    return {'results': get_book(book_id)}


@app.route('/db', methods=('GET', 'POST'))
def db():
    if request.method == 'POST':
        req_q = request.get_json()
        q = req_q['q']
        print(q)
        params = dict(
            q=q
        )
        return jsonify(fetch_api(params))

    return jsonify({'status': "Not working"})

@app.route('/')
def index():
    return "Hello flask!"
