from flask import Flask
import os
import books_library_app.db


app = Flask(__name__)

from books_library_app import db_commands

app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'books_library.sqlite'),
    )
app.config["JSON_SORT_KEYS"] = False
# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)


# @app.route('/')
# def index():
#     return "Hello flask!"
