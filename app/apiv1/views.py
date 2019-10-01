from datetime import datetime, timedelta

from flask import jsonify, abort, request

from . import apiv1
from ..models import Item, Acquisition, Borrower, Checkout
from .. import db

# TODO: implement security measures for unsafe API methods

@apiv1.route('/items', methods=['GET'])
def get_items():
    '''Return all items in the collection.'''
    return jsonify(items=[i.serialize for i in Item.query.all()])

@apiv1.route('/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    '''Return a specific item from the collection.'''
    item = Item.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    return jsonify(item=item.serialize)

@apiv1.route('/items', methods=['POST'])
def create_item():
    '''Add a new item to the collection.'''
    if not request.json or not 'title' in request.json:
        abort(400)
    item = Item(
        title=request.json['title'],
        creator=request.json.get('creator', ''),
        publisher=request.json.get('publisher', ''),
        location_id=request.json.get('location_id', None),
        notes=request.json.get('notes', '')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item=item.serialize), 201

@apiv1.route('/item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    '''Remove an item from the collection.'''
    item = Item.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'result': True})

@apiv1.route('/item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    '''Update an existing item.'''
    item = Item.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    if not request.json:
        abort(400)
    # launch a series of type checks
    if 'title' in request.json and type(request.json['title']) != str:
        abort(400)
    if 'creator' in request.json and type(request.json['creator']) != str:
        abort(400)
    if 'publisher' in request.json and type(request.json['publisher']) != str:
        abort(400)
    if 'notes' in request.json and type(request.json['notes']) != str:
        abort(400)
    if 'location_id' in request.json and type(request.json['location_id']) != int:
        abort(400)

    # finally make the changes
    item.title = request.json.get('title', item.title)
    item.creator = request.json.get('creator', item.creator)
    item.publisher = request.json.get('publisher', item.publisher)
    item.notes = request.json.get('notes', item.notes)
    item.locationid = request.json.get('location_id', item.location_id)
    db.session.add(item)
    db.session.commit()
    return jsonify(item=item.serialize)

@apiv1.route('/acquisitions', methods=['GET'])
def get_acquisitions():
    '''Return all acquisition requests.'''
    return jsonify(acquisitions=[a.serialize for a in Acquisition.query.all()])

@apiv1.route('/acquisition/<int:acq_id>', methods=['GET'])
def get_acquisition(acq_id):
    acq = Acquisition.query.filter_by(id=acq_id).first()
    if acq is None:
        abort(404)
    return jsonify(acq.serialize)

@apiv1.route('/acquisiton/<int:acq_id>', methods=['DELETE'])
def delete_acquisition(acq_id):
    acq = Acquisition.query.filter_by(id=acq_id).first()
    if acq is None:
        abort(404)
    db.session.delete(acq)
    db.session.commit()
    return jsonify({'result': True})

# TODO: add PUT acquisition method
# TODO: add POST acquisition method

@apiv1.route('/checkout', methods=['POST'])
def checkout():
    '''Check one or more items out to a borrower.

    Expects a JSON request containing a list of ```item_id```s
    and a ```borrower_id```.

    :returns: JSON reponse with a list of failed checkouts and a list of successful ones
    '''
    # make sure we got a json request
    if not request.json:
        abort(400)

    if 'items' not in request.json or type(request.json['items']) != list:
        abort(400)
    if 'borrower_id' not in request.json or type(request.json['borrower_id']) != int:
        abort(400)

    borrower = Borrower.query.filter_by(id=request.json['borrower_id']).first()
    if borrower is None:
        abort(404)

    succeeded = []
    failed = []
    for item_id in request.json['items']:
        item = Item.query.filter_by(id=item_id).first()
        if item is None or not item.is_available():
            failed.append(item_id)
        else:
            co = Checkout(borrower=borrower,
                          item=item,
                          # IDEA: calculate loan period based on borrower standing?
                          date_due=datetime.utcnow()+timedelta(days=14),
                         )
            db.session.add(co)
            succeeded.append(item_id)
    db.session.commit()
    return jsonify(succeeded=succeeded, failed=failed)

@apiv1.route('/checkin', methods=['POST'])
def checkin():
    '''Check one or more items in.

    Expects a JSON request containing a list of ```item_id```s.
    '''
    if not request.json:
        abort(400)
    if 'items' not in request.json or type(request.json['items']) != list:
        abort(400)

    failed, succeeded = [], []
    for item_id in request.json['items']:
        co = Checkout.query.filter_by(item_id=item_id, date_returned=None).first()
        if co is None:
            failed.append(item_id)
        else:
            co.date_returned = datetime.utcnow()
            db.session.add(co)
            succeeded.append(item_id)
    db.session.commit()
    return jsonify(succeeded=succeeded, failed=failed)


# TODO: add method for searching items

@apiv1.route('/borrowers', methods=['GET'])
def get_borrowers():
    '''Return all borrowers.'''
    return jsonify(borrowers=[b.serialize for b in Borrower.query.all()])

@apiv1.route('/borrower/<int:borrower_id>', methods=['DELETE'])
def delete_borrower(borrower_id):
    borrower = Borrower.query.filter_by(id=borrower_id).first()
    if borrower is None:
        abort(404)
    db.session.delete(borrower)
    db.session.commit()
    return jsonify({'result': True})

# TODO: add borrower GET by id method
# TODO: add borrower PUT method
# TODO: add borrower POST method
