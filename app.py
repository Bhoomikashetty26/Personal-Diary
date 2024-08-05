from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

client = MongoClient('localhost', 27017)
db = client['personal_diary']
entries_collection = db['entries']

class EntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def index():
    entries = entries_collection.find().sort("date", -1)
    return render_template('index.html', entries=entries)

@app.route('/new', methods=['GET', 'POST'])
def new_entry():
    form = EntryForm()
    if form.validate_on_submit():
        entries_collection.insert_one({
            'title': form.title.data,
            'description': form.description.data,
            'date': datetime.now()
        })
        return redirect(url_for('index'))
    return render_template('new_entry.html', form=form)

@app.route('/edit/<entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = entries_collection.find_one({'_id': ObjectId(entry_id)})
    form = EntryForm(obj=entry)
    if form.validate_on_submit():
        entries_collection.update_one(
            {'_id': ObjectId(entry_id)},
            {'$set': {
                'title': form.title.data,
                'description': form.description.data
            }}
        )
        return redirect(url_for('index'))
    return render_template('edit_entry.html', form=form)

@app.route('/delete/<entry_id>')
def delete_entry(entry_id):
    entries_collection.delete_one({'_id': ObjectId(entry_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
