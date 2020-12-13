"""
Blueprint containing all API resources for WSWP.
"""

from flask import Blueprint, jsonify, request


api = Blueprint('api', __name__)


@api.route('/pulse', methods=['GET'])
def check_pulse():
    return jsonify(message="API is online"), 200