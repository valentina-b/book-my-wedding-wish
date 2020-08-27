import os
import string
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


# on the homepage, enter and submit a wishlist name/description through a form
@app.route('/complete_wishlist', methods=['POST'])
def create_wishlist_name():
    wishlists = mongo.db.wishlists
    new_wishlist = wishlists.insert_one(request.form.to_dict())
    new_wishlist_id = new_wishlist.inserted_id
    the_wishlist = mongo.db.wishlists.find_one({"_id": ObjectId(new_wishlist_id)})
    # capitalise entered wishlist name
    the_wishlist_name = the_wishlist['wishlist_name']
    the_wishlist_name_capitalised = string.capwords(the_wishlist_name, sep = None)
    # create wishlist username - which goes into the link
    the_wishlist_username = the_wishlist_name.lower().replace(" ", "-")
    # validate the username against other wishlist usernames (must be unique, it's in the link)
    check_wishlist_usernames = wishlists.count_documents((
        {
            'wishlist_username': the_wishlist_username
         }))
    if check_wishlist_usernames == 0:
        # update the wishlist with the new information
        wishlists.update({"_id": ObjectId(new_wishlist_id)},
            {'$set':
                {
                    'wishlist_username': the_wishlist_username,
                    'wishlist_name': the_wishlist_name_capitalised
                }
            })
        return render_template('wishlist_completing.html', new_wishlist_id=new_wishlist_id,
                                wishlist=the_wishlist_name_capitalised)
    else:
        # delete this document and return error page
        mongo.db.wishlists.remove({'_id': ObjectId(new_wishlist_id)})
        mongo.db.present.remove({"wishlist_id": ObjectId(new_wishlist_id)})
        return redirect(url_for('wishlist_username_not_available'))


# return error page that wishlist username is taken
@app.route('/wishlist_username_not_available')
def wishlist_username_not_available():
    return render_template('wishlist_username_not_available.html')


# complete the wishlist
@app.route('/<new_wishlist_id>/wishlist_created', methods=['POST'])
def complete_wishlist(new_wishlist_id):
    wishlists = mongo.db.wishlists
    the_wishlist = wishlists.find_one({'_id': ObjectId(new_wishlist_id)})
    wishlist_username = the_wishlist['wishlist_username']
    wishlists.update({"_id": ObjectId(new_wishlist_id)},
        {'$set':
            {
                'wishlist_description': request.form.get('wishlist_description'),
                'wishlist_header_image_URL': request.form.get('wishlist_header_image_URL'),
                'wishlist_wedding_date': request.form.get('wishlist_wedding_date')
            }
        })
    return render_template('wishlist_created.html', new_wishlist_id=new_wishlist_id,
                            wishlist=the_wishlist,
                            wishlist_username=wishlist_username)


# go to created wishlist owner page where owner can add presents
# display all the presents stored with the created wishlist id in the presents collection
@app.route('/<wishlist_username>/owner')
def owner_view_dynamic(wishlist_username):
    the_wishlist = mongo.db.wishlists.find_one({'wishlist_username': wishlist_username})
    wishlist_username = the_wishlist['wishlist_username']
    wishlist_id = the_wishlist['_id']
    presents = mongo.db.present
    displayed_presents = presents.find({'wishlist_id_username': wishlist_username})
    return render_template('owner_view.html', wishlist_id=wishlist_id,
                            the_wishlist=the_wishlist,
                            displayed_presents=displayed_presents,
                            wishlist_username=wishlist_username)


# function that lets you add presents stored with the created wishlist id in the presents collection
# create a link back to the owner's wishlist
@app.route('/<wishlist_username>/present_added', methods=['POST'])
def add_new_present(wishlist_username):
    presents = mongo.db.present
    new_present = presents.insert_one(request.form.to_dict())
    new_present_id = new_present.inserted_id
    presents.update({'_id': ObjectId(new_present_id)},
        {'$set':
            {
                'wishlist_id_username': wishlist_username,
                'present_availability': True,
                'present_booked_by': ""
            }
        })
    return render_template('present_added.html', wishlist_username=wishlist_username)


# delete a present from the present collection
@app.route('/<wishlist_username>/present_deleted/<present_id>')
def delete_present(wishlist_username, present_id):
    mongo.db.present.remove({'_id': ObjectId(present_id)})
    return render_template('present_deleted.html', wishlist_username=wishlist_username,
                            present_id=present_id)


# edit a present of a wishlist
@app.route('/<wishlist_username>/edit_present/<present_id>')
def edit_present(wishlist_username, present_id):
    the_present = mongo.db.present.find_one({"wishlist_id_username": wishlist_username})
    return render_template('present_editing.html', wishlist_username=wishlist_username,
                            present_id=present_id, present=the_present)


# update the present in the edit view
@app.route('/<wishlist_username>/update_present/<present_id>', methods=["POST"])
def update_present(wishlist_username, present_id):
    presents = mongo.db.present
    presents.update({"wishlist_id_username": wishlist_username},
        {'$set':
            {
                'present_description': request.form.get('present_description'),
                'present_header_image_URL': request.form.get('present_header_image_URL')
            }
        })
    return render_template('present_updated.html', wishlist_username=wishlist_username,
                            present_id=present_id)


# edit the wishlist
@app.route('/<wishlist_username>/owner/edit_wishlist')
def edit_wishlist(wishlist_username):
    the_wishlist =  mongo.db.wishlists.find_one({"wishlist_username": wishlist_username})
    return render_template('wishlist_editing.html', wishlist_username=wishlist_username,
                            wishlist=the_wishlist)


# update the wishlist in the edit view
@app.route('/<wishlist_username>/owner/update_wishlist', methods=["POST"])
def update_wishlist(wishlist_username):
    wishlist = mongo.db.wishlists
    wishlist.update({"wishlist_username": wishlist_username},
        {'$set':
            {
                'wishlist_name': request.form.get('wishlist_name'),
                'wishlist_description': request.form.get('wishlist_description'),
                'wishlist_header_image_URL': request.form.get('wishlist_header_image_URL')
            }
        })
    return render_template('wishlist_updated.html', wishlist_username=wishlist_username)


# delete the wishlist
@app.route('/<wishlist_username>/owner/wishlist_deleted')
def delete_wishlist(wishlist_username):
    mongo.db.wishlists.remove({"wishlist_username": wishlist_username})
    mongo.db.present.remove({"wishlist_id_username": wishlist_username})
    mongo.db.username.remove({"wishlist_id_username": wishlist_username})
    return render_template('wishlist_deleted.html', wishlist_username=wishlist_username)


# go to guest page where guests can book presents
# display all the presents stored with the created wishlist id in the presents collection
@app.route('/<wishlist_username>/guest')
def guest_view_static(wishlist_username):
    the_wishlist = mongo.db.wishlists.find_one({"wishlist_username": wishlist_username})
    presents = mongo.db.present
    displayed_presents = presents.find({"wishlist_id_username": wishlist_username})
    return render_template('guest_view.html', wishlist_username=wishlist_username,
                            the_wishlist=the_wishlist,
                            displayed_presents=displayed_presents)


# create a guest username to book the presents
@app.route('/<wishlist_username>/guest/username_created', methods=["POST"])
def add_guest_username(wishlist_username):
    usernames = mongo.db.username
    new_username = usernames.insert_one(request.form.to_dict())
    new_username_id = new_username.inserted_id
    mongo.db.username.update({'_id': ObjectId(new_username_id)},
        {'$set':
            {
                'wishlist_id_username': wishlist_username
            }
        })
    return render_template('guest_username_created.html', wishlist_username=wishlist_username,
                            new_username_id=new_username_id)


# go back to the guest wishlist as a 'registered' wishlist guest
@app.route('/<wishlist_username>/guest/<new_username_id>')
def guest_view_dynamic(wishlist_username, new_username_id):
    the_wishlist = mongo.db.wishlists.find_one({'wishlist_username': wishlist_username})
    presents = mongo.db.present
    displayed_presents = presents.find({'wishlist_id_username': wishlist_username})
    return render_template('guest_view_username.html', wishlist_username=wishlist_username,
                            new_username_id=new_username_id,
                            displayed_presents=displayed_presents,
                            the_wishlist=the_wishlist)


# book a present as a guest
@app.route('/<wishlist_username>/guest/<new_username_id>/<present_id>/present_booked', methods=["POST", "GET"])
def book_present(wishlist_username, new_username_id, present_id):
    presents = mongo.db.present
    presents.update({"_id": ObjectId(present_id)},
        {'$set':
            {
                'present_availability': False,
                'present_booked_by': new_username_id
            }
        })
    return render_template('present_booked.html', wishlist_username=wishlist_username,
                            new_username_id=new_username_id,
                            present_id=present_id)


# unbook a present as a guest
@app.route('/<wishlist_username>/guest/<new_username_id>/<present_id>/present_unbooked', methods=["POST", "GET"])
def unbook_present(wishlist_username, new_username_id, present_id):
    presents = mongo.db.present
    presents.update({"_id": ObjectId(present_id)},
        {'$set':
            {
                'present_availability': True,
                'present_booked_by': ""
            }
        })
    return render_template('present_unbooked.html', wishlist_username=wishlist_username,
                            new_username_id=new_username_id,
                            present_id=present_id)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
