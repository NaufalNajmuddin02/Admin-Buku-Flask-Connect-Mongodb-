from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/bukukita'
app.config['UPLOAD_FOLDER'] = 'static/images'
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view_category')
def view_category():
    categories = mongo.db.categories.find()
    return render_template('view_category.html', categories=categories)


@app.route('/create_category', methods=['GET', 'POST'])
def create_category():
    if request.method == 'POST':
        name = request.form['name']
        mongo.db.categories.insert_one({'name': name})
        return redirect(url_for('view_category'))
    return render_template('create_category.html')

@app.route('/update_category/<category_id>', methods=['GET', 'POST'])
def update_category(category_id):
    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    if request.method == 'POST':
        name = request.form['name']
        mongo.db.categories.update_one({'_id': ObjectId(category_id)}, {'$set': {'name': name}})
        return redirect(url_for('view_category'))
    return render_template('update_category.html', category=category)

@app.route('/delete_category/<category_id>')
def delete_category(category_id):
    mongo.db.categories.delete_one({'_id': ObjectId(category_id)})
    mongo.db.books.delete_many({'category_id': ObjectId(category_id)})
    return redirect(url_for('view_category'))

@app.route('/view_books', methods=['GET', 'POST'])
def view_books():
    categories = list(mongo.db.categories.find())
    filter_category = request.args.get('category')
    filter_text = request.args.get('text')
    filter_date = request.args.get('date')

    query = {}
    if filter_category:
        query['category_id'] = ObjectId(filter_category)
    if filter_text:
        query['$or'] = [{'title': {'$regex': filter_text, '$options': 'i'}},
                        {'author': {'$regex': filter_text, '$options': 'i'}},
                        {'publisher': {'$regex': filter_text, '$options': 'i'}}]
    if filter_date:
        query['publication_date'] = filter_date

    books = mongo.db.books.find(query)
    return render_template('view_books.html', books=books, categories=categories)

@app.route('/create_book', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        publication_date = request.form['publication_date']
        category_id = request.form['category_id']
        image = request.files['image']
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        mongo.db.books.insert_one({
            'title': title,
            'author': author,
            'publisher': publisher,
            'publication_date': publication_date,
            'category_id': ObjectId(category_id),
            'image': image_filename
        })
        return redirect(url_for('view_books'))

    categories = mongo.db.categories.find()
    return render_template('create_book.html', categories=categories)

@app.route('/update_book/<book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    categories = mongo.db.categories.find()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        publication_date = request.form['publication_date']
        category_id = request.form['category_id']
        image = request.files.get('image')

        update_data = {
            'title': title,
            'author': author,
            'publisher': publisher,
            'publication_date': publication_date,
            'category_id': ObjectId(category_id)
        }

        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            update_data['image'] = image_filename

        mongo.db.books.update_one({'_id': ObjectId(book_id)}, {'$set': update_data})
        return redirect(url_for('view_books'))

    return render_template('update_book.html', book=book, categories=categories)

@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    mongo.db.books.delete_one({'_id': ObjectId(book_id)})
    return redirect(url_for('view_books'))

if __name__ == '__main__':
    app.run(debug=True)
