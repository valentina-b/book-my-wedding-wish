import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from os import path
if path.exists("env.py"):
    import env

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'wedding-registry'
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost')

mongo = PyMongo(app)

# @app.route('/')
# def hello():
#     return 'Hello world'

@app.route('/')
@app.route('/homepage')
def homepage():
    return render_template('homepage.html',
                            page_title="Welcome to Book My Wedding Wish!")


# on the homepage, enter and submit a wishlist name/description through a form
@app.route('/create_wishlist_name', methods=['POST'])
def create_wishlist_name():
    wishlists = mongo.db.wishlists
    wishlists.insert_one(request.form.to_dict())
    return redirect(url_for('owner_view'))


# go to created wishlist owner page where owner can add presents
@app.route('/owner/wishlist_name')
def owner_view():
    return render_template('owner_view.html')


# function that lets you add presents to the wishlist on the owner view
@app.route('/add_presents', methods=['POST'])
def add_new_present():
    present = mongo.db.present
    present.insert_one(request.form.to_dict())
    return render_template('present_added.html')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
