from flask import jsonify, make_response

from . import apiv1

@apiv1.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@apiv1.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)
