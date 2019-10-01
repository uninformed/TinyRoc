from flask import jsonify, abort, request

from . import apiv1
from ..models import Item
from .. import db

@apiv1.route('/items', methods=['GET'])
def get_items():
    """Returns all items in the collection."""
    return jsonify(items=[i.serialize for i in Item.query.all()])

@apiv1.route('/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    return jsonify(item=item.serialize)

@apiv1.route('/items', methods=['POST'])
def create_item():
    """Add a new item to the collection."""
    if not request.json or not 'title' in request.json:
        abort(400)
    item = Item(
        title=request.json['title'],
        creator=request.json.get('creator', ''),
        publisher=request.json.get('publisher', ''),
        notes=request.json.get('notes', '')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item=item.serialize), 201

@apiv1.route('/item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'result': True})
