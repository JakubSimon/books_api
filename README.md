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

## Database initialization
```
flask init-db
```