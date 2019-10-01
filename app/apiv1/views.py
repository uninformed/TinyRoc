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

# TODO: add method for searching items
# TODO: add methods for managing checkouts
# TODO: add methods for managing borrowers
