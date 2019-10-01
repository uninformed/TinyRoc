'''API, version 1'''
from flask import Blueprint, jsonify, abort, request

apiv1 = Blueprint('apiv1', __name__, url_prefix='/api/v1')

from . import errors, views
