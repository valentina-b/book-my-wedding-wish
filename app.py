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
    return render_template('homepage.html')


@app.route('/create_wishlistname', methods=['POST'])
def create_wishlistname():
    wishlists = mongo.db.wishlists
    wishlists.insert_one(request.form.to_dict())
    return redirect('homepage')


# route to wishlist form
# @app.route('/<>')
# def edit_wishlist():
#     return render_template('edit_wishlist.html')



if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
