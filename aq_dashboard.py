"""OpenAQ Air Quality Dashboard with Flask."""
from datetime import datetime
from flask import Flask
import openaq 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
api = openaq.OpenAQ()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)


class Record(DB.Model):
    # id (integer, primary key)
    id = DB.Column(DB.BigInteger, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String)
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'<Record: {self.datetime}, {self.value}>'


def get_results():
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    tuples = []
    for result in body['results']:
        tup = (result['date']['utc'], result['value'])
        tuples.append(tup)
    return tuples


@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # Get data from OpenAQ, make Record objects with it, and add to db
    curr_id = 1
    for datetime, value in get_results():
        record = Record(id=curr_id, datetime=datetime, value=value)
        curr_id += 1
        DB.session.add(record)
    DB.session.commit()
    return 'Data refreshed!'


@app.route('/')
def root():
    """Base view."""
    return str(get_results())