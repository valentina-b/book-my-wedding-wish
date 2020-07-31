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
    new_wishlist = wishlists.insert_one(request.form.to_dict())
    new_wishlist_id = new_wishlist.inserted_id
    wishlists.update({'_id': ObjectId(new_wishlist_id)},
        {'$set':
            {'present_description': "",
            'present_header_image_URL': ""
            }
        })
    return redirect(url_for('owner_view_dynamic', new_wishlist_id=new_wishlist_id))


# go to created wishlist owner page where owner can add presents
@app.route('/<new_wishlist_id>/owner')
def owner_view_dynamic(new_wishlist_id):
    return render_template('owner_view.html', new_wishlist_id=new_wishlist_id)


# function that lets you add presents to the wishlist on the owner view
@app.route('/<new_wishlist_id>/present_added', methods=['POST'])
def add_new_present(new_wishlist_id):
    mongo.db.wishlists.update({'_id': ObjectId(new_wishlist_id)},
        {'$set':
            {'present_description': request.form.get('present_description'),
            'present_header_image_URL': request.form.get('present_header_image_URL')
            }
        })
    return render_template('present_added.html', new_wishlist_id=new_wishlist_id)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
